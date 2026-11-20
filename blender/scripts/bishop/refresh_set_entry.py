"""Refresh just the bishop's two generated records in the current set page."""
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path


def section(document, key):
    pattern = rb'(<script\b[^>]*\bid="' + key.encode() + rb'"[^>]*>)(.*?)(</script>)'
    matches = list(re.finditer(pattern, document, re.DOTALL))
    if len(matches) != 1:
        raise ValueError(f'Expected exactly one {key} in the existing set page')
    return matches[0]


def compact(value):
    return json.dumps(value,separators=(',',':')).replace('<','\\u003c').encode()


def replace_bishop(document, board, side):
    for key in ('model-profile-data','board-data'):
        m=section(document,key)
        raw=m.group(2)
        records=json.loads(raw)
        if key=='model-profile-data':
            prior=records['bishop']
            fresh=side
        else:
            prior,=[x for x in records['pieces'] if x['piece']=='bishop']
            fresh=board
        old=compact(prior)
        if raw.count(old)!=1:
            raise ValueError(f'Cannot isolate the existing bishop entry in {key}')
        raw=raw.replace(old,compact(fresh),1)
        document=document[:m.start(2)]+raw+document[m.end(2):]
    return document


def update_page(path, board, side):
    before=path.read_bytes()
    after=replace_bishop(before,board,side)
    if before!=after:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.bishop-set-', delete=False) as stream:
            tmp=Path(stream.name)
            stream.write(after)
        try:
            os.chmod(tmp,path.stat().st_mode)
            if path.read_bytes()!=before:
                raise RuntimeError('The set page changed during the update. Retry against its current contents.')
            os.replace(tmp,path)
        finally:
            tmp.unlink(missing_ok=True)
    return hashlib.sha256(after).hexdigest()


def entries(root):
    sys.path.insert(0,str(root/'scripts'))
    from board_comparison_data import build_board_data
    from png_profile_bounds import profile_bounds
    board,=[row for row in build_board_data(root)['pieces'] if row['piece']=='bishop']
    relative='assets/bishop/side-profile.png'
    src=root/relative
    side={'file':relative,'version':hashlib.sha256(src.read_bytes()).hexdigest()[:16],**profile_bounds(src)}
    return board,side


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    parser.add_argument('--preview',type=Path)
    args=parser.parse_args()
    board,side=entries(args.root)
    for repo in [args.root]+([args.preview] if args.preview else []):
        result=update_page(repo/'set-comparison.html',board,side)
        print(repo,board['sourceSha256'],board['version'],side['version'],result)
