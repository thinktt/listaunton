"""Compare all projection renders against original and selected source images."""
from pathlib import Path
import argparse,json,runpy,shutil,sys
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2]);ap.add_argument('--only',type=int);args=ap.parse_args();root=args.root
manifest=json.loads((root/'assets/king-projections/variants.json').read_text())
for item in manifest['variants']:
 if args.only is not None and item['elevation']!=args.only:continue
 temp=root/'build/king-projections'/item['id'];dest=root/item['assetDir']
 shutil.copy2(dest/'render.png',temp/'assets/king/render.png')
 sys.argv=[str(root/'scripts/king/compare.py'),str(temp)]
 runpy.run_path(str(root/'scripts/king/compare.py'),run_name='__main__')
 for name in ['qa.json','contour-original.png','contour-selected.png']:shutil.copy2(temp/'assets/king'/name,dest/name)
 item['comparison']=json.loads((dest/'qa.json').read_text())['images']
(root/'assets/king-projections/variants.json').write_text(json.dumps(manifest,indent=2)+'\n')
