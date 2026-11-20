from pathlib import Path
import ast

source=Path(__file__).resolve().parents[1]
root=source/'work/listauton-staging'
scripts=root/'scripts/queen'
scripts.mkdir(parents=True,exist_ok=True)
files={
 'build_queen.py':'outputs/queen-hires',
 'export_viewer_mesh.py':'outputs/queen-hires',
 'overlay_qa.py':'outputs/queen-hires',
 'build_viewer.py':'work/queen-hires',
 'inspect_viewer_camera.py':'work/queen-hires',
 'check_viewer_camera.cjs':'work/queen-hires',
 'validate_seamless_crown.py':'work/queen-hires',
 'viewer-template.html':'work/queen-hires',
}
for name,folder in files.items():
 text=(source/folder/name).read_text(encoding='utf-8')
 if name=='build_queen.py':
  text=text.replace('OUT=Path(__file__).resolve().parent\nROOT=OUT.parents[1]', "ROOT=Path(__file__).resolve().parents[2]\nOUT=ROOT/'assets/queen'\nMODEL=ROOT/'models/queen/queen-rebuilt.blend'\nOUT.mkdir(parents=True,exist_ok=True)\nMODEL.parent.mkdir(parents=True,exist_ok=True)")
  text=text.replace("str(OUT/'queen-rebuilt.blend')",'str(MODEL)')
 elif name=='export_viewer_mesh.py':
  text=text.replace('DELIVERABLES = Path(__file__).resolve().parent\nWORK = DELIVERABLES.parents[1] / "work" / "queen-hires"', 'ROOT = Path(__file__).resolve().parents[2]\nDELIVERABLES = ROOT / "models" / "queen"\nWORK = ROOT / "build" / "queen"\nWORK.mkdir(parents=True, exist_ok=True)')
 elif name=='overlay_qa.py':
  text=text.replace('WORKSPACE / "outputs" / "queen-hires"','WORKSPACE / "assets" / "queen"')
 elif name=='build_viewer.py':
  text=text.replace("root / 'work' / 'queen-hires'","root / 'build' / 'queen'")
  text=text.replace("root / 'outputs' / 'queen-hires' / 'queen-3d.html'","root / 'queen-3d.html'")
  text=text.replace("root / 'outputs' / 'queen-hires' / 'queen-rebuilt.blend'","root / 'models' / 'queen' / 'queen-rebuilt.blend'")
  text=text.replace("(work / 'viewer-template.html')","(Path(__file__).resolve().parent / 'viewer-template.html')")
 elif name=='inspect_viewer_camera.py':
  text=text.replace('ROOT / "outputs" / "queen-hires" / "queen-rebuilt.blend"','ROOT / "models" / "queen" / "queen-rebuilt.blend"')
  text=text.replace('OUTPUT = Path(__file__).resolve().parent / "viewer-camera.json"','OUTPUT = ROOT / "build" / "queen" / "viewer-camera.json"\nOUTPUT.parent.mkdir(parents=True, exist_ok=True)')
 elif name=='check_viewer_camera.cjs':
  text=text.replace("'outputs/queen-hires/queen-3d.html'","'queen-3d.html'")
  text=text.replace("path.join(__dirname,'viewer-camera", "path.join(root,'build/queen/viewer-camera")
 elif name=='validate_seamless_crown.py':
  text=text.replace('WORK = Path(__file__).resolve().parent\nOUTPUT = WORK.parents[1] / "outputs" / "queen-hires"','ROOT = Path(__file__).resolve().parents[2]\nWORK = ROOT / "history" / "queen-hires"\nOUTPUT = ROOT / "assets" / "queen"')
  text=text.replace('default=OUTPUT / "queen-rebuilt.blend"','default=ROOT / "models" / "queen" / "queen-rebuilt.blend"')
 elif name=='viewer-template.html':
  text=text.replace('href="queen-rebuilt.blend"','href="models/queen/queen-rebuilt.blend"')
 if name.endswith('.py'):ast.parse(text,filename=name)
 (scripts/name).write_text(text,encoding='utf-8')
(scripts/'requirements.txt').write_text('numpy>=1.26,<3\nPillow>=10.1,<13\n',encoding='utf-8')
print('Portable queen pipeline written; Python syntax verified.')
