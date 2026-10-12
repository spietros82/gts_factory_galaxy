"""Internal portable source/build/synthetic-data package; no credentials or model redistribution."""
from pathlib import Path
import zipfile,hashlib,json,argparse
ROOT=Path.cwd()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true');args=parser.parse_args()
 destination=ROOT/('dist/FactoryGalaxy-focused-inspection-m1-final.zip' if args.final else 'dist/FactoryGalaxy-focused-inspection-m1.zip')
 if destination.exists():raise SystemExit('Package exists; preserve it')
 items=[]
 # Include only this milestone plus original reusable source and pinned Unity files.
 for base in ['inspection','factory','UnityProject/Assets','UnityProject/Packages','UnityProject/ProjectSettings','builds/inspection','reports/inspection']:
  for p in (ROOT/base).rglob('*'):
   if not p.is_file():continue
   rel=p.relative_to(ROOT)
   if any(x in rel.parts for x in ['private','__pycache__','gui-profiles','portable-copy']):continue
   if p.suffix in ['.joblib','.pyc','.log']:continue
   if p.name.startswith('config.') and p.name not in ['config.example.json']:continue
   if 'inspection/dataset' in str(rel) or 'reports/inspection' in str(rel) or base not in ['inspection'] or p.suffix in ['.py','.sh','.md','.txt','.json']:items.append(p)
 for name in ['README.md','ENVIRONMENT.md','ARCHITECTURE.md','PERFORMANCE.md','TEST_REPORT.md','STATUS.md','CHANGELOG.md','HANDOVER.md','.gitignore']:
  items.append(ROOT/name)
 items=sorted(set(items));manifest={str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in items}
 with zipfile.ZipFile(destination,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in items:z.write(p,str(p.relative_to(ROOT)))
  z.writestr('PACKAGE_READ_FIRST.txt','Internal review package. Source/build/synthetic images/results included. Runtime, credentials, old projects and trained joblib weights excluded. To run learned mode, supply trusted locally generated cap-rf.joblib matching inspection/models/policy.json; external redistribution permission not assumed. Use existing Python dependencies with VISION_PYTHON and editable config; no weights/environment installed by launch. Native release uses Linux/OpenGLCore. Same-host copied launch checked separately, not proof on another platform. No cloud inference or real control. Do not rerun locked evaluation.\n')
  z.writestr('CONTENT_MANIFEST.json',json.dumps(manifest,indent=2))
 with zipfile.ZipFile(destination) as z:
  assert z.testzip() is None
  for name,r in manifest.items():assert hashlib.sha256(z.read(name)).hexdigest()==r['sha256']
  assert not any('private/' in n or n.endswith('.joblib') or 'config.local' in n for n in z.namelist())
 Path('reports/inspection/package-verification-final.json' if args.final else 'reports/inspection/package-verification.json').write_text(json.dumps({'file':str(destination),'bytes':destination.stat().st_size,'sha256':hashlib.sha256(destination.read_bytes()).hexdigest(),'entries':len(items),'crc_and_hashes':'PASS','model_weights_included':False,'reason':'locally generated artifact kept on host; external redistribution rights not presumed','other_hardware':'unverified'},indent=2))
 print(destination,destination.stat().st_size)
if __name__=='__main__':main()
