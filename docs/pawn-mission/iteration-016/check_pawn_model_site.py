"""Run the unchanged pawn assertions from the shared checker independently.

The full checker currently stops on unrelated king edits. This reports only
the pawn section; it does not turn that whole-set failure into a pass or edit
the shared script. Supply the repository root as the sole argument.
"""
import ast,hashlib,sys
from pathlib import Path
root=Path(sys.argv[1]).resolve();path=root/'scripts/check_model_site.py'
source=path.read_text(encoding='utf8');tree=ast.parse(source,filename=str(path));body=[];narrowed=False;loop_found=False
for node in tree.body:
    if isinstance(node,ast.ClassDef) and node.name=='PageFacts':break
    body.append(node)
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='selection' for t in node.targets):
        body.extend(ast.parse("assert 'pawn' in selection\nselection={'pawn':selection['pawn']}").body);narrowed=True
    if isinstance(node,ast.For) and isinstance(node.iter,ast.Call) and isinstance(node.iter.func,ast.Attribute) and isinstance(node.iter.func.value,ast.Name) and node.iter.func.value.id=='selection':loop_found=True
assert narrowed and loop_found,'Shared checker structure changed; inspect it instead of guessing scope.'
module=ast.fix_missing_locations(ast.Module(body=body,type_ignores=[]))
sys.argv=[str(path),str(root)]
exec(compile(module,str(path),'exec'),{'__file__':str(path),'__name__':'__pawn_model_site_scope__'})
print('SCOPE: pawn section only; shared checker SHA-256',hashlib.sha256(source.encode()).hexdigest())
