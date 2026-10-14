"""Image-space association only. A track is not a simulator bottle ID."""
from .detector import iou
class Tracker:
    def __init__(self):self.tracks={};self.next_id=0;self.last_time=-1
    def update(self,detections,capture_time):
        if capture_time<=self.last_time:return [dict(d,track_id='',association='out-of-order',inspection='uncertain') for d in detections]
        self.last_time=capture_time
        self.tracks={k:v for k,v in self.tracks.items() if capture_time-v['time']<=.5}
        used=set();out=[]
        for d in detections:
            matches=sorted([(iou(d['box'],v['box']),k) for k,v in self.tracks.items() if k not in used],reverse=True)
            compatible=[m for m in matches if m[0]>=.20]
            ambiguous=len(compatible)>1 and compatible[0][0]-compatible[1][0]<.15
            if ambiguous:
                out.append(dict(d,track_id='',association='ambiguous',inspection='uncertain'));continue
            if compatible:key=compatible[0][1];hits=self.tracks[key]['hits']+1
            else:self.next_id+=1;key='T'+str(self.next_id);hits=1
            used.add(key);self.tracks[key]={'box':d['box'],'time':capture_time,'hits':hits}
            x0,y0,x1,y1=d['box'];w=x1-x0;h=y1-y0
            regions={'cap':[x0,y0,x1,y0+.28*h],'fill':[x0,y0+.25*h,x1,y0+.75*h],'label':[x0,y0+.40*h,x1,y0+.85*h]}
            # Geometry fractions are proposals, not the frozen Stage4 160px controlled station input.
            out.append(dict(d,track_id=key,association='confirmed image track' if hits>=2 else 'tentative',inspection='uncertain',inspection_reason='Detector-derived regions have not been validated for frozen station classifiers',regions=regions))
        return out
