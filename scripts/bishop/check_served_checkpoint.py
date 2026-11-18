"""Verify the bishop review and whole-set entry through the user's local HTTP server."""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

from refresh_set_entry import section

def sha(data):
    return hashlib.sha256(data).hexdigest()

def main(root,url):
    received={}
    def get(relative):
        req=Request(url+'/'+relative,headers={'Cache-Control':'no-cache'})
        with urlopen(req,timeout=35) as response:
            assert response.status==200,(relative,response.status)
            data=response.read()
        received[relative]=sha(data)
        return data
    meta=json.loads(get('assets/bishop/mesh.json'))
    assert meta['sourceSha256']==sha((root/'models/bishop/bishop-rebuilt.blend').read_bytes())
    viewer=get('bishop-model.html')
    review=get('bishop-review.html')
    assert b'bishop-model.html' in review and sha(viewer)[:16].encode() in review
    assert json.loads(section(viewer,'mesh-metadata').group(2))['sourceSha256']==meta['sourceSha256']
    vertex_buffer=get('assets/bishop/mesh.bin')
    assert base64.b64decode(section(viewer,'mesh-data').group(2),validate=True)==vertex_buffer
    assert len(vertex_buffer)==meta['totalByteLength']
    for tag,filename in [('model-image','render.png'),('model-neutral-image','render-clay.png'),('original-image','original.png')]:
        match=re.search(rb'id="'+tag.encode()+rb'" src="data:image/png;base64,([^"]+)"',viewer)
        assert match and base64.b64decode(match[1],validate=True)==get('assets/bishop/'+filename),tag
    lineup=get('set-comparison.html')
    board,=[p for p in json.loads(section(lineup,'board-data').group(2))['pieces'] if p['piece']=='bishop']
    assert board['sourceSha256']==meta['sourceSha256']
    assert board['file']=='assets/bishop/render.png' and board['version']==received[board['file']][:16]
    assert board['modelHeight']==meta['bounds']['size'][2] and board['baseWidth']==meta['bounds']['size'][0]
    side=json.loads(section(lineup,'model-profile-data').group(2))['bishop']
    assert side['file']=='assets/bishop/side-profile.png'
    assert sha(get(side['file']))[:16]==side['version']
    for path in ['assets/bishop/head-side.png','assets/bishop/rear-oblique.png','assets/bishop/camera.json']:
        get(path)
    for path,digest in received.items():
        if path!='set-comparison.html':
            assert sha((root/path).read_bytes())==digest,('Local server returned a different file',path)
    return {'passed':True,'server':url,'source_sha256':meta['sourceSha256'],'bishop_review_revision':sha(viewer)[:16],
            'embedded_mesh_and_images_exact':True,'set_board_entry':board,'set_profile_entry':side,
            'served_sha256':received}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
    p.add_argument('--url',choices=['http://localhost:8080','http://127.0.0.1:8080'],default='http://localhost:8080')
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args()
    data=main(a.root,a.url)
    a.out.write_text(json.dumps(data,indent=2)+'\n')
    print('HTTP bishop checkpoint verified',data['source_sha256'])
