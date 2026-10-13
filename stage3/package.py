"""Portable reviewed source only; no credentials, datasets, weights or Unity binaries."""
import hashlib,json,subprocess,zipfile
from pathlib import Path
ROOT=Path.cwd();OUT=ROOT/'dist';OUT.mkdir(exist_ok=True)
def main():
 files=[]
 for name in subprocess.check_output(['git','ls-files'],text=True).splitlines():
  p=Path(name)
  if name.startswith('UnityProject/') and not any(x in p.parts for x in ['Library','Temp','Logs','UserSettings']):files.append(p)
  elif name.startswith('stage3/') and p.suffix in ['.py','.sh','.md','.json','.txt','.jpg']:files.append(p)
  elif name in ['factory/model.py','factory/__init__.py','tools/unity_ui.py','.gitignore']:files.append(p)
 # Root docs in this package are clean Stage3 summaries, never full local history.
 aliases={'README.md':'stage3/README.md','STATUS.md':'stage3/MILESTONE-3.md','HANDOVER.md':'stage3/MILESTONE-3.md','ARCHITECTURE.md':'stage3/ARCHITECTURE.md','PERFORMANCE.md':'stage3/PERFORMANCE.md','TEST_REPORT.md':'stage3/VERIFICATION.md'}
 path=OUT/'FactoryGalaxy-Stage3-source.zip'
 with zipfile.ZipFile(path,'w',zipfile.ZIP_DEFLATED) as archive:
  for p in files:
   if not p.exists():continue
   archive.write(p,str(p))
  for target,source in aliases.items():archive.write(source,target)
  archive.writestr('PACKAGE-LIMITS.txt','Source package: existing pinned Python and licensed Unity required. No weights, datasets, builds, credentials, runtime history or private configuration. Reproduce local captures/training using README; this is not a turnkey binary or cross-hardware verification.\n')
 with zipfile.ZipFile(path) as z:
  assert z.testzip() is None
  assert not any(any(s in n for s in ['dataset/','models/','.venv/','config.local','runtime/','Library/','builds/']) for n in z.namelist())
 Path('reports/stage3/package.json').write_text(json.dumps({'path':str(path),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'scope':'Source-only reproducible package; no portability runtime claim'},indent=2));print(path,path.stat().st_size)
if __name__=='__main__':main()
