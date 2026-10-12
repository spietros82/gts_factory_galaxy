import statistics
ALLOWED_NAMES={'fill_ml','cap_presence_switch','buffer_count','packed_total','active_bottles'}
def validate_observations(body):
    if not isinstance(body,dict) or body.get('contract')!='gts.observation-batch/1':raise ValueError('Unsupported observation contract')
    if set(body)-{'contract','session','sim_time','profile','observations'}:raise ValueError('Unsupported batch fields')
    forbidden={'fault','cause','scenario','severity','ground_truth','cap_displaced'}
    if forbidden.intersection(body):raise ValueError('Presenter/ground-truth fields prohibited')
    rows=body.get('observations'); clock=body.get('sim_time');session=body.get('session')
    if not isinstance(session,str) or not 1<=len(session)<=80:raise ValueError('Invalid session')
    if not isinstance(clock,(int,float)) or clock<0:raise ValueError('Invalid simulation clock')
    if not isinstance(rows,list) or len(rows)>400:raise ValueError('Bounded observation batch required')
    clean=[]
    keys={'contract','asset_id','name','unit','quality','machine_state','sequence','timestamp','value','has_value','bottle_id','head'}
    for row in rows:
        if not isinstance(row,dict) or set(row)-keys:raise ValueError('Unsupported observation fields')
        if row.get('contract')!='gts.telemetry/1' or row.get('name') not in ALLOWED_NAMES:raise ValueError('Unsupported measurement')
        expected_units={'fill_ml':'mL','cap_presence_switch':'boolean','buffer_count':'bottles','packed_total':'bottles','active_bottles':'bottles'}
        if row.get('unit')!=expected_units[row['name']]:raise ValueError('Unsupported measurement unit')
        if row.get('quality') not in ['good','missing']:raise ValueError('Unsupported quality')
        if not isinstance(row.get('timestamp'),(int,float)) or row['timestamp']>clock+.001:raise ValueError('Future measurement')
        if not isinstance(row.get('sequence'),int) or not isinstance(row.get('has_value'),bool):raise ValueError('Invalid sequence/value flag')
        if row['has_value'] and (not isinstance(row.get('value'),(int,float)) or not __import__('math').isfinite(row['value'])):raise ValueError('Invalid value')
        clean.append(dict(row))
    return clean

def findings(rows,clock,profile):
    if profile<2:return []
    good=[r for r in rows if r['quality']=='good' and r['has_value'] and 0<=clock-r['timestamp']<=90]
    answer=[]
    for head in range(4):
        values=[r for r in good if r['name']=='fill_ml' and r['head']==head][-20:]
        if len(values)>=8:
            mean=statistics.mean(r['value'] for r in values); sd=statistics.stdev(r['value'] for r in values)
            answer.append({'id':f'A-HEAD-{head}','category':'Statistical calculation','title':f'Head {head+1}: recent mean {mean:.1f} mL; sample SD {sd:.1f} mL ({len(values)} bottles)',
             'flagged':abs(mean-500)>3 or sd>4,'evidence_ids':[f"O-{r['sequence']}" for r in values],
             'uncertainty':'Synthetic screening thresholds; measurement/calibration and physical cause unconfirmed. Not remaining-life prediction.'})
    if profile>=3:
        buffer=[r for r in good if r['name']=='buffer_count']
        packed=[r for r in good if r['name']=='packed_total']
        if len(packed)>=2:
            a,b=packed[0],packed[-1];dt=b['timestamp']-a['timestamp'];rate=(b['value']-a['value'])/dt if dt>0 else None
            if rate is not None:answer.append({'id':'A-FLOW','category':'Conventional arithmetic','title':f'Observed packing throughput {rate:.2f} bottles/s; latest buffer '+(str(int(buffer[-1]['value'])) if buffer else 'unknown'),
              'flagged':bool(buffer and buffer[-1]['value']>=15),'evidence_ids':[f"O-{a['sequence']}",f"O-{b['sequence']}"]+([f"O-{buffer[-1]['sequence']}"] if buffer else []),
              'uncertainty':'Observed throughput window; physical restriction or planned slowdown remains unconfirmed.'})
    return answer

def assistant_evidence(rows,clock,analyses):
    latest={}
    for r in rows:
        key=(r['asset_id'],r['name'],r['head'])
        if key not in latest or latest[key]['timestamp']<r['timestamp']:latest[key]=r
    observations=[]
    for r in latest.values():
        copy={k:v for k,v in r.items() if k!='contract'};copy['id']=f"O-{r['sequence']}";copy['age_sim_seconds']=round(clock-r['timestamp'],3)
        if not r['has_value'] or clock-r['timestamp']>3:copy['value']=None;copy['quality']='missing' if not r['has_value'] else 'stale'
        observations.append(copy)
    return {'synthetic':True,'sim_time':clock,'observations':observations[-24:],'calculations':analyses,'control_boundary':'Observe/advice only; no control writes; no failure-time estimate'}
