"""One-time, non-destructive import into the user-requested WSL repository."""
from pathlib import Path
import ast
import hashlib
import shutil
import subprocess

source=Path('/mnt/c/Users/toby/Documents/Codex/2026-10-01/go-x20/work/listauton-staging')
dest=Path('/home/toby/code/listauton')
assert dest.parent.resolve()==Path('/home/toby/code')
assert not dest.exists(), f'Refusing to overwrite existing project: {dest}'
shutil.copytree(source,dest,ignore=shutil.ignore_patterns('__pycache__','_site','.git'))
for path in source.rglob('*'):
    if path.is_file() and '__pycache__' not in path.parts and '_site' not in path.parts:
        imported=dest/path.relative_to(source)
        assert hashlib.sha256(path.read_bytes()).digest()==hashlib.sha256(imported.read_bytes()).digest(),str(imported)
for path in (dest/'scripts').rglob('*.py'):
    ast.parse(path.read_text(encoding='utf-8'),filename=str(path))
def run(*args):
    subprocess.run(args,cwd=dest,check=True)
run('python3','scripts/check_site.py')
run('python3','scripts/package_site.py')
run('python3','scripts/check_site.py','_site')
run('git','init','-b','main')
run('git','add','--all')
run('git','diff','--cached','--check')
message=('Import Staunton queen reconstruction and project site\n\n'
         'Preserve reference sprites, editable queen, renders, earlier iterations,\n'
         'and working scripts. Add portable build/check scripts, a home page\n'
         'linking the three queen tools, and a GitHub Pages deployment workflow.\n\n'
         'Co-Authored-By: Codex GPT 6 Astra Ultra <codex@openai.com>\n')
run('git','commit','-m',message)
run('git','status','--short')
run('git','log','-1','--format=%h%n%B')
print('IMPORT_COMPLETE',dest)
