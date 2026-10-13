"""Saved-results-only tables/charts; never runs a benchmark or model."""
import json,math,html,statistics
from pathlib import Path
ROOT=Path('reports/stage4/capacity');OUT=Path('stage4/charts')
def chart(path,title,key,label,unit,threshold=None):
 phases=json.loads((ROOT/'corrected-summary.json').read_text())['phases'];OUT.mkdir(exist_ok=True);width,height=940,470;left,right,top,bottom=88,30,68,72;plotw=width-left-right;ploth=height-top-bottom
 series={};colors={'full-cpu':'#087e8b','full-gpu':'#a23b85','render-cpu':'#657181'}
 for r in phases:
  if r['mode'] not in ['full','render']:continue
  obj=r
  for name in key.split('.'):
   obj=obj.get(name,None) if isinstance(obj,dict) else None
  if obj is not None:series.setdefault(r['mode']+'-'+r['device'],[]).append((r['line_count'],float(obj),r['iteration'],r['passed']))
 values=[v[1] for points in series.values() for v in points];maximum=max(values+[threshold or 0,1])*1.1
 def x(n):return left+math.log2(n)/math.log2(48)*plotw
 def y(v):return top+ploth-v/maximum*ploth
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">','<rect width="100%" height="100%" fill="white"/>',f'<text x="24" y="32" font-family="sans-serif" font-size="21" fill="#142838">{html.escape(title)}</text>']
 for i in range(6):
  value=maximum*i/5;yy=y(value);svg +=[f'<path d="M{left},{yy}H{width-right}" stroke="#e4e9ec"/>',f'<text x="{left-12}" y="{yy+5}" text-anchor="end" font-family="sans-serif" font-size="13">{value:.1f}</text>']
 for n in [1,3,6,12,24,48]:svg.append(f'<text x="{x(n)}" y="{height-bottom+25}" text-anchor="middle" font-family="sans-serif" font-size="14">{n}</text>')
 if threshold:svg +=[f'<path d="M{left},{y(threshold)}H{width-right}" stroke="#ad4242" stroke-dasharray="6 4"/>',f'<text x="{left+7}" y="{y(threshold)-6}" font-family="sans-serif" font-size="12" fill="#ad4242">Protocol threshold {threshold:g}{unit}</text>']
 for index,(name,points) in enumerate(series.items()):
  color=colors[name];explore=sorted([p for p in points if p[2]=='explore']);pathdata=' '.join(('M'if i==0 else 'L')+f'{x(p[0]):.2f},{y(p[1]):.2f}' for i,p in enumerate(explore));svg.append(f'<path d="{pathdata}" fill="none" stroke="{color}" stroke-width="2"/>')
  for count,value,iteration,passed in points:
   xx,yy=x(count),y(value);radius=5 if iteration=='explore'else 3;svg.append(f'<circle cx="{xx}" cy="{yy}" r="{radius}" fill="{color}" stroke="{"white" if passed else "#d02323"}" stroke-width="2"><title>{html.escape(name)} {count} lines {iteration}: {value:.3f}{unit}, {"PASS" if passed else "FAIL"}</title></circle>')
  svg.append(f'<text x="{left+index*235}" y="56" font-family="sans-serif" font-size="13" fill="{color}">{name}</text>')
 svg +=[f'<text x="{width/2}" y="{height-18}" text-anchor="middle" font-family="sans-serif" font-size="14">Active independent lines (log2 positions); small dots = confirmations</text>',f'<text x="18" y="{height/2}" transform="rotate(-90 18 {height/2})" text-anchor="middle" font-family="sans-serif" font-size="14">{html.escape(label)} ({unit})</text>','</svg>'];(OUT/path).write_text('\n'.join(svg))
def main():
 v=json.loads((ROOT/'corrected-summary.json').read_text());rows=[]
 for r in v['phases']:
  rows.append('|'+ '|'.join([r['name'],str(r['line_count']),f"{r['fps']:.2f}",f"{r['frames_ms'].get('p95',0):.2f}/{r['frames_ms'].get('p99',0):.2f}",f"{r['end_to_end_ms'].get('p95',0):.2f}",f"{r['completed_images_per_s']:.2f}",str(r['drops_total']),str(r['missed_deadlines_steady']),'PASS'if r['passed']else 'FAIL'])+'|')
 (ROOT/'results-table.md').write_text('|Phase|Lines|FPS mean|Frame p95/p99 ms|Inspection p95 ms|Completed images/s|Native terminal drops|2s misses|Protocol|\n|---|---:|---:|---:|---:|---:|---:|---:|---|\n'+'\n'.join(rows))
 chart('frame-time.svg','Complete factory versus rendering-only','frames_ms.p95','Frame interval p95','ms',20)
 chart('latency.svg','Actual capture-to-result latency','end_to_end_ms.p95','Capture→result p95','ms')
 chart('trigger-latency.svg','Station trigger to result — acquisition queue included','trigger_to_result_ms.p95','Trigger→result p95','ms',2000)
 chart('throughput.svg','Completed inspections (three images per bottle batch)','completed_images_per_s','Completed images','images/s')
 chart('host-cpu.svg','Host CPU across all32 logical processors','resources.host_cpu_percent.mean','Host CPU mean','%')
 chart('gpu.svg','Device-wide GPU — includes all background workloads','resources.gpu_busy_percent.mean','amdgpu GPU busy mean','%')
 chart('memory.svg','Native process resident memory (shared memory not summed)','resources.native_rss_mb.mean','Native RSS mean','MB')
 print('Saved seven SVGcharts and exact phase table')
if __name__=='__main__':main()
