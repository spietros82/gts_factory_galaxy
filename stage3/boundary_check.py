"""Bounded live service boundary verification, synthetic test envelopes only."""
import base64,json,time,uuid,copy
from datetime import datetime,timezone,timedelta
from pathlib import Path
from stage3.gui_check import api,wait,click,shot,audit

def main():
 out=Path('reports/stage3/boundary');out.mkdir(exist_ok=True);checks=[];saved=[]
 click(130,112);time.sleep(1);checks.append({'name':'Machine data settled audit','pass':audit()['view']=='Machine data'});shot('machine-data-final')
 click(90,155);time.sleep(.5)
 image=next(Path('runtime/stage3-service/frames').glob('*.png')).read_bytes()
 def new():return dict(contract='gts.three-frame/1',line_id='Line01',session_id=uuid.uuid4().hex,bottle_id='synthetic-boundary',batch_id=uuid.uuid4().hex,capture_utc=datetime.now(timezone.utc).isoformat(),source_time=0.0,target_count=1,observations_available=True,product='LAGER',frames=[dict(station_id=s,frame_id=uuid.uuid4().hex,image=base64.b64encode(image).decode(),roi=[48,48,160,160]) for s in ['cap','fill','label']])
 for kind in ['missing','ambiguous','stale']:
  b=new()
  if kind=='missing':b['observations_available']=False
  elif kind=='ambiguous':b['target_count']=2
  else:b['capture_utc']=(datetime.now(timezone.utc)-timedelta(seconds=10)).isoformat()
  reply=api('/batch',b);state=wait(lambda s:len([r for r in s['events'] if r['batch_id']==b['batch_id']])==3);records=[r for r in state['events'] if r['batch_id']==b['batch_id']];checks.append({'name':kind+' withholds pass','pass':all(r['decision']=='uncertain' for r in records)});saved.append({'case':kind,'request':b,'reply':reply,'records':records})
  if kind=='missing':
   try:api('/batch',b);duplicate=False
   except Exception as e:duplicate='400' in str(e)
   checks.append({'name':'Duplicate batch refused','pass':duplicate})
 b=new();b['expected_class']='aligned'
 try:api('/batch',b);rejected=False
 except Exception as e:rejected='400' in str(e)
 checks.append({'name':'Hidden truth field refused','pass':rejected})
 click(90,155)
 (out/'results.json').write_text(json.dumps({'checks':checks,'raw':saved},indent=2));print(checks)
 assert all(c['pass'] for c in checks)
if __name__=='__main__':main()
