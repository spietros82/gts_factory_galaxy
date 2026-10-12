"""Same-host copied package smoke test; stages trusted OWN artifact locally, zero Ollama calls."""
from pathlib import Path
import zipfile,json,subprocess,os,time,urllib.request,shutil
ROOT=Path.cwd();COPY=ROOT/'runtime/inspection-portable-copy'
def main():
 if COPY.exists():raise SystemExit('Copy exists; preserve it')
 COPY.mkdir()
 with zipfile.ZipFile(ROOT/'dist/FactoryGalaxy-focused-inspection-m1.zip') as z:z.extractall(COPY)
 # Only local private smoke copy; distributed archive does NOT include the weight.
 shutil.copyfile(ROOT/'inspection/models/cap-rf.joblib',COPY/'inspection/models/cap-rf.joblib')
 cfg=json.loads((COPY/'inspection/config.example.json').read_text());cfg['port']=8813;cfg['data_path']='runtime/copied-smoke';cfg['explanation_budget']=0
 (COPY/'inspection/config.local.json').write_text(json.dumps(cfg))
 python=ROOT/'.venv/bin/python';env=os.environ.copy();env.update({'OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2'})
 exe=COPY/'builds/inspection/FactoryGalaxy.x86_64';exe.chmod(0o755)
 service=subprocess.Popen([str(python),'-m','inspection.service','--config','inspection/config.local.json'],cwd=COPY,env=env,stdout=subprocess.DEVNULL,stderr=(COPY/'service-stderr.txt').open('w'))
 try:
  for _ in range(50):
   try:json.load(urllib.request.urlopen('http://127.0.0.1:8813/health',timeout=1));break
   except Exception:time.sleep(.2)
  out=COPY/'runtime/native';out.mkdir(parents=True)
  run=subprocess.run([str(exe),'-screen-fullscreen','0','-screen-width','1280','-screen-height','720','-logFile',str(COPY/'native.log'),'--focused-inspection','true','--inspection-endpoint','http://127.0.0.1:8813','--profile','2','--data-path',str(out),'--duration','12','--screenshot',str(COPY/'copied-native.png'),'--screenshot-after','8'],cwd=COPY,stdout=subprocess.DEVNULL,timeout=30)
  state=json.load(urllib.request.urlopen('http://127.0.0.1:8813/state',timeout=2))
  result={'returncode':run.returncode,'copied_directory':str(COPY),'different_loopback_port':8813,'model_staged_locally_for_test_only':True,'trained_weight_in_distributed_archive':False,'native_screenshot':str(COPY/'copied-native.png'),'inspected':state['inspected'],'explanation_calls':state['explanation_calls'],'same_host_only':True,'pass':run.returncode==0 and state['inspected']>0 and state['explanation_calls']==0}
  (ROOT/'reports/inspection/portable-check.json').write_text(json.dumps(result,indent=2));print(result)
 finally:service.terminate();service.wait(10)
if __name__=='__main__':main()
