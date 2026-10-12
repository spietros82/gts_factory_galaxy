using System;
using System.IO;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEngine;
using Debug=UnityEngine.Debug;
namespace Braemac.Factory {
 public sealed class FactoryApp:MonoBehaviour {
  public LineSimulation Sim {get;private set;} public string Selected="line";public int Profile=1;
  FactoryGeometry geometry;Camera main;float accumulator,speed=1,yaw=10,pitch=30,distance=28;Vector3 target=Vector3.zero;
  bool paused,technical,showProcedures,measurement,computeTechnical;int tab;Vector2 sidebarScroll;EdgeClient edge;FocusedInspection focused;double started;string screenshotPath="";float quitAfter;bool screenshotSaved;
  List<float> frames=new List<float>();List<double> frameWall=new List<double>();List<double> tickTimes=new List<double>();
  GUIStyle title,heading,text,small,button,toggle;Texture2D panel;string dataPath;
  public bool Paused{get{return paused;}}
  public FactoryGeometry Geometry{get{return geometry;}}
  public Camera MainCamera{get{return main;}}
  public string DataPath{get{return dataPath;}}
  public static string Argument(string key,string fallback=""){var a=Environment.GetCommandLineArgs();for(int i=0;i<a.Length-1;i++)if(a[i]==key)return a[i+1];return fallback;}
  void Awake(){
   measurement=Argument("--measurement","false")=="true";if(Argument("--inspection-dataset")!="")paused=true;
   Application.runInBackground=true;Application.targetFrameRate=int.Parse(Argument("--frame-target","60"));QualitySettings.vSyncCount=0;
   QualitySettings.antiAliasing=4;QualitySettings.shadows=ShadowQuality.All;QualitySettings.shadowDistance=55;
   dataPath=Argument("--data-path",Path.Combine(Application.persistentDataPath,"factory"));Directory.CreateDirectory(dataPath);
   screenshotPath=Argument("--screenshot");float.TryParse(Argument("--duration","0"),out quitAfter);
   Sim=new LineSimulation(42);for(int pre=0;pre<800;pre++)Sim.Step();string scenario=Argument("--scenario");if(scenario!="")Sim.PresenterFault(scenario);
   int.TryParse(Argument("--profile","1"),out Profile);Profile=Mathf.Clamp(Profile,1,3);
   float.TryParse(Argument("--speed","1"),out speed);speed=Mathf.Clamp(speed,.25f,8);
   geometry=new FactoryGeometry();
   main=new GameObject("Overview camera").AddComponent<Camera>();main.tag="MainCamera";main.fieldOfView=43;main.nearClipPlane=.1f;main.farClipPlane=100;
   main.rect=new Rect(0,0,.77f,1);
   main.backgroundColor=new Color(.017f,.026f,.05f);main.clearFlags=CameraClearFlags.SolidColor;
   RenderSettings.ambientMode=UnityEngine.Rendering.AmbientMode.Flat;RenderSettings.ambientLight=new Color(.4f,.48f,.57f);
   var sun=new GameObject("Soft industrial key light").AddComponent<Light>();sun.type=LightType.Directional;sun.intensity=1.3f;sun.color=new Color(.9f,.95f,1);sun.transform.rotation=Quaternion.Euler(48,-28,0);sun.shadows=LightShadows.Soft;
   var rim=new GameObject("Cyan rim light").AddComponent<Light>();rim.type=LightType.Directional;rim.intensity=.65f;rim.color=new Color(.3f,.7f,1);rim.transform.rotation=Quaternion.Euler(28,155,0);
   if(Argument("--focused-inspection","false")=="true"){focused=gameObject.AddComponent<FocusedInspection>();edge=gameObject.AddComponent<EdgeClient>();edge.enabled=false;}else edge=gameObject.AddComponent<EdgeClient>();
   started=Time.realtimeSinceStartupAsDouble;
   if(Argument("--stream-path")!="")gameObject.AddComponent<StreamBridge>();
  }
  void Update(){
   float dt=Time.unscaledDeltaTime;if(frames.Count<120000){frames.Add(dt*1000);frameWall.Add(Time.realtimeSinceStartupAsDouble-started);}
   if(!paused){accumulator+=Mathf.Min(dt,.25f)*speed;int steps=0;
    while(accumulator>=LineSimulation.TickSeconds&&steps++<40){var sw=Stopwatch.StartNew();Sim.Step();sw.Stop();tickTimes.Add(sw.Elapsed.TotalMilliseconds);accumulator-=(float)LineSimulation.TickSeconds;}
   }
   if(Input.GetKeyDown(KeyCode.F12))ScreenCapture.CaptureScreenshot(Path.Combine(dataPath,"screen-"+DateTime.UtcNow.ToString("yyyyMMddTHHmmssZ")+".png"));
   if(Input.GetKeyDown(KeyCode.F2))tab=0;if(Input.GetKeyDown(KeyCode.F3))tab=1;if(Input.GetKeyDown(KeyCode.F4))tab=2;
   if(!measurement&&Input.GetKeyDown(KeyCode.Space))paused=!paused;
   if(!measurement&&Input.GetKeyDown(KeyCode.Home))Overview();
   bool ui=Input.mousePosition.y>Screen.height-150||Input.mousePosition.x>Screen.width-365;
   if(!measurement&&!ui){distance=Mathf.Clamp(distance-Input.mouseScrollDelta.y*1.3f,7,42);
    if(Input.GetMouseButton(1)){yaw+=Input.GetAxis("Mouse X")*3;pitch=Mathf.Clamp(pitch-Input.GetAxis("Mouse Y")*2,20,70);}
    if(Input.GetMouseButtonDown(0)){RaycastHit hit;if(Physics.Raycast(main.ScreenPointToRay(Input.mousePosition),out hit,100)){var pick=hit.collider.GetComponent<MachinePick>();if(pick!=null){Selected=pick.Asset;target=pick.Focus;distance=11;}}}
   }
   main.transform.position=target+Quaternion.Euler(pitch,yaw,0)*new Vector3(0,0,-distance);main.transform.LookAt(target+Vector3.up*.8f);
   geometry.Update(Sim,paused?1:accumulator/(float)LineSimulation.TickSeconds,main);
   if(!screenshotSaved&&screenshotPath!=""&&Time.realtimeSinceStartupAsDouble-started>=double.Parse(Argument("--screenshot-after","5"),System.Globalization.CultureInfo.InvariantCulture)){Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(screenshotPath)));ScreenCapture.CaptureScreenshot(screenshotPath);screenshotSaved=true;}
   if(quitAfter>0&&Time.realtimeSinceStartupAsDouble-started>=quitAfter)Application.Quit();
  }
  public void Overview(){Selected="line";target=Vector3.zero;distance=28;yaw=10;pitch=30;}
  public void ResetLine(){Sim=new LineSimulation(42);for(int pre=0;pre<800;pre++)Sim.Step();accumulator=0;paused=false;if(focused!=null)focused.NewSession();}
  // Semantic, application-only input. Never inject desktop keys or OS commands.
  public string RemoteAction(string action,string value){
   if(measurement)return "rejected: measurement controls held";
   switch(action){
    case "pause":paused=true;break;
    case "resume":paused=false;break;
    case "overview":Overview();break;
    case "reset":ResetLine();break;
    case "fault":if(value!="cap"&&value!="fill"&&value!="outfeed")return "rejected: fault";Sim.PresenterFault(value);break;
    case "profile":int n;if(!int.TryParse(value,out n)||n<1||n>3)return "rejected: profile";Profile=n;break;
    case "tab":if(value=="line")tab=0;else if(value=="evidence")tab=1;else if(value=="ai")tab=2;else return "rejected: tab";break;
    case "explain":if(focused!=null){focused.Explain();tab=2;break;}if(Profile<2)return "rejected: select edge profile";edge.RequestAssistant();tab=2;break;
    case "zoom":if(value=="in")distance=Mathf.Max(7,distance-2);else if(value=="out")distance=Mathf.Min(42,distance+2);else return "rejected: zoom";break;
    case "orbit":if(value=="left")yaw-=10;else if(value=="right")yaw+=10;else return "rejected: orbit";break;
    case "machine":float px;if(value=="infeed")px=-11;else if(value=="filler")px=-7;else if(value=="capper")px=-2;else if(value=="inspection")px=3;else if(value=="packer")px=10;else return "rejected: machine";Selected=value;target=new Vector3(px,1,0);distance=11;break;
    default:return "rejected: unsupported application action";
   }
   return "applied to simulator only";
  }
  void Styles(){
   if(title!=null)return;panel=new Texture2D(1,1);panel.SetPixel(0,0,new Color(.025f,.055f,.09f,.96f));panel.Apply();
   title=new GUIStyle(GUI.skin.label){fontSize=25,fontStyle=FontStyle.Bold,normal={textColor=new Color(.83f,.96f,1)}};
   heading=new GUIStyle(title){fontSize=17,wordWrap=true};text=new GUIStyle(GUI.skin.label){fontSize=14,wordWrap=true,normal={textColor=new Color(.84f,.91f,.96f)}};
   small=new GUIStyle(text){fontSize=12};button=new GUIStyle(GUI.skin.button){fontSize=14,fixedHeight=32};toggle=new GUIStyle(GUI.skin.toggle){fontSize=13,wordWrap=true};
  }
  public void OnGUI(){
   Styles();float scale=Mathf.Max(.7f,Screen.width/1600f);GUI.matrix=Matrix4x4.Scale(new Vector3(scale,scale,1));float w=Screen.width/scale,h=Screen.height/scale;
   GUI.DrawTexture(new Rect(18,18,w-36,112),panel);GUILayout.BeginArea(new Rect(34,25,w-68,100));
   GUILayout.BeginHorizontal();GUILayout.Label("BRAEMAC  /  GTS FACTORY GALAXY",title);GUILayout.FlexibleSpace();GUILayout.Label("SYNTHETIC DIGITAL TWIN • OBSERVE & ADVISE",small);GUILayout.EndHorizontal();
   GUI.enabled=!measurement;GUILayout.BeginHorizontal();if(GUILayout.Button(paused?"▶  Play":"Ⅱ  Pause",button,GUILayout.Width(100)))paused=!paused;
   if(GUILayout.Button("Reset replay",button,GUILayout.Width(130)))ResetLine();if(GUILayout.Button("Overview",button,GUILayout.Width(115)))Overview();
   GUILayout.Label("Simulation speed",text,GUILayout.Width(118));speed=GUILayout.HorizontalSlider(speed,.25f,8,GUILayout.Width(100));GUILayout.Label(speed.ToString("0.0")+"×",text,GUILayout.Width(45));
   GUILayout.FlexibleSpace();if(GUILayout.Button("1  PLC",button,GUILayout.Width(90)))Profile=1;if(GUILayout.Button("2  Entry",button,GUILayout.Width(90)))Profile=2;if(GUILayout.Button("3  Higher",button,GUILayout.Width(100)))Profile=3;GUILayout.Label("Sim "+Sim.Time.ToString("0.0")+" s",text);GUILayout.EndHorizontal();GUI.enabled=true;GUILayout.EndArea();
   GUI.DrawTexture(new Rect(w-355,146,337,h-174),panel);GUILayout.BeginArea(new Rect(w-339,160,305,h-200));
   GUILayout.BeginHorizontal();if(GUILayout.Button("Line",button))tab=0;if(GUILayout.Button("Evidence",button))tab=1;if(GUILayout.Button("Local AI",button))tab=2;GUILayout.EndHorizontal();
   sidebarScroll=GUILayout.BeginScrollView(sidebarScroll,false,false);
   if(tab==0){
    GUILayout.Label("LINE STATUS",heading);GUILayout.Label(paused?"Paused • process clock held":"Running • seeded synthetic replay",text);
    GUILayout.Label("Packed "+Sim.Packed+"  •  Rejected "+Sim.Rejected,text);GUILayout.Label("Buffer "+Sim.BufferCount+" bottles • finite capacity",text);
    GUILayout.Space(10);GUILayout.Label("SIMULATED PLC • ALARM HISTORY",heading);
    if(Sim.Alarms.Count==0)GUILayout.Label("No conventional alarms",text);else foreach(string alarm in Sim.Alarms)GUILayout.Label("!  "+alarm,text);
    GUILayout.Space(10);GUILayout.Label(measurement?"MEASUREMENT RUN • CONTROLS HELD":"PRESENTER TOOLS • SIMULATOR ONLY",small);GUI.enabled=!measurement;
    if(GUILayout.Button("Outfeed restriction",button))Sim.PresenterFault("outfeed");
    if(GUILayout.Button("Filling-head drift",button))Sim.PresenterFault("fill");
    if(GUILayout.Button("Cap-placement problem",button))Sim.PresenterFault("cap");GUI.enabled=true;
    GUILayout.Space(10);GUILayout.Label("INSPECT: "+Selected.ToUpperInvariant(),heading);
    GUILayout.Label(Selected=="line"?"Click a machine to focus. Right-drag to orbit; scroll to zoom. Home restores overview.":"Synthetic equipment. Measurements do not establish a physical cause.",text);
    GUILayout.Space(10);GUILayout.Label("YOUR NEXT INSPECTION",heading);GUILayout.Label(Sim.Alarms.Count==0?"Monitor flow and measurement quality. Explore Evidence or request Local AI in an edge mode.":"Compare alarm history with current observed values, then inspect the associated station using your approved site procedure. Demo advice is not an operating instruction.",text);
    GUILayout.Space(10);GUILayout.Label("All three profiles use this same A395. PLC owns sequence and interlocks. No AI control or real equipment.",small);
   }else if(tab==1){
    GUILayout.Label("OBSERVED EVIDENCE • "+Selected.ToUpperInvariant(),heading);GUILayout.Label("Synthetic measurements • simulation time "+Sim.Time.ToString("0.0")+" s",small);
    GUI.enabled=!measurement;Sim.ObservationLoss=GUILayout.Toggle(Sim.ObservationLoss,"Presenter: delayed / missing observations",toggle,GUILayout.Width(278));GUI.enabled=true;
    technical=GUILayout.Toggle(technical,"Expand telemetry records",toggle,GUILayout.Width(278));
    if(technical){int shown=0;for(int i=Sim.Observations.Count-1;i>=0&&shown<5;i--){var o=Sim.Observations[i];if(Selected!="line"&&o.asset_id!=Selected)continue;shown++;
      GUILayout.Label(o.asset_id+" • "+o.name+" = "+(o.has_value?o.value.ToString("0.0")+" "+o.unit:"MISSING")+"\nseq "+o.sequence+" • sim "+o.timestamp.ToString("0.00")+"s • "+o.quality+" • age "+(Sim.Time-o.timestamp).ToString("0.0")+"s"+((Sim.Time-o.timestamp)>3?" • HISTORICAL / STALE":""),small);}}
    AdditionalPanel();
   }else AdditionalPanel();
   ComputePanel();
   GUILayout.EndScrollView();
   GUILayout.EndArea();
   GUI.DrawTexture(new Rect(18,h-56,w-391,38),panel);GUI.Label(new Rect(32,h-49,w-419,30),(measurement?"MEASUREMENT RUN • scenario / profile held  |  ":"All process data synthetic  |  Seed 42  |  Space: pause  |  ")+"Wall frame interval: "+(dtMean()).ToString("0.0")+" ms",small);
   GUI.matrix=Matrix4x4.identity;
  }
  void ComputePanel(){
   if(focused!=null){GUILayout.Space(10);GUILayout.Label("RENDERING / MEASURED",heading);GUILayout.Label((1000/Mathf.Max(.001f,dtMean())).ToString("0.0")+" FPS • GPU scene rendering\nFocused sklearn classifier executes on CPU; no GPU/NPU claim.",small);return;}
   GUILayout.Space(12);GUILayout.Label("COMPUTE ACTIVITY",heading);
   GUILayout.Label("Rendering: running • GPU / "+SystemInfo.graphicsDeviceType+"\nMeasured "+(1000/Mathf.Max(.001f,dtMean())).ToString("0.0")+" FPS • frame "+dtMean().ToString("0.0")+" ms\nTarget "+Application.targetFrameRate+" FPS (-1 uncapped); VSync "+QualitySettings.vSyncCount+"\nCamera acquisition: "+(Profile>=2?"running • scene GPU render / CPU PNG encode":"idle")+"\nCamera render rate "+edge.CameraRate.ToString("0.0")+" frames/s (measured recent window)\n"+(edge.CapturedFrames>0?"PNG capture "+edge.CaptureMs.ToString("0.0")+" ms (measured last encoded frame)":"PNG capture unavailable: no encoded frame yet"),small);
   GUILayout.Label(string.IsNullOrEmpty(edge.View.compute_summary)?"Host/model instrumentation unavailable":edge.View.compute_summary,small);
   computeTechnical=GUILayout.Toggle(computeTechnical,"Compute technical details",toggle);
   if(computeTechnical)GUILayout.Label(edge.View.compute_technical,small);
  }
  float dtMean(){int n=Math.Min(frames.Count,120);if(n==0)return 0;float sum=0;for(int i=frames.Count-n;i<frames.Count;i++)sum+=frames[i];return sum/n;}
  void AdditionalPanel(){
   if(focused!=null){FocusedPanel();return;}
   GUILayout.Space(8);GUILayout.Label("EDGE WORKLOAD • MODE "+Profile,heading);
   GUILayout.Label(Profile==1?"PLC only — analytics and inference disabled":Profile==2?"Illustrative entry: per-head statistics, one camera view, on-demand assistant":"Illustrative higher: flow analysis, two alternating views and more frequent camera inference",small);
   if(edge==null)return;GUILayout.Label(edge.Status,small);
   if(Profile>=2&&tab==1){
    if(edge.View.analysis!=null)foreach(var a in edge.View.analysis)GUILayout.Label((a.flagged?"!  ":"•  ")+a.title,small);
    GUILayout.Label("LIVE CAMERA • SYNTHETIC PIXELS",heading);GUILayout.Label("Live image is separate from the classified frame below",small);
    if(edge.Feed!=null)GUILayout.Label(edge.Feed,GUILayout.Width(270),GUILayout.Height(145));
    var v=edge.View.vision;if(v!=null&&!string.IsNullOrEmpty(v.state)){GUILayout.Label("Vision: "+v.state+" • "+v.model,small);if(v.state=="complete"){GUILayout.Label("EXACT CLASSIFIED FRAME",heading);if(edge.ClassifiedFrame!=null&&edge.ClassifiedFrameId==v.frame_id)GUILayout.Label(edge.ClassifiedFrame,GUILayout.Width(270),GUILayout.Height(180));GUILayout.Label(v.cap_result+" • bottle "+v.bottle_id+" • "+v.camera_id+"\n"+v.observation+"\n"+v.capture_utc+" → "+v.completed_utc+"\nFrame "+v.frame_id,small);}if(v.state=="failed")GUILayout.Label(v.error,small);}
    GUILayout.Label("Actual vision model, unvalidated hypothesis. Pixels cannot establish secure attachment or equipment cause. No automated action.",small);
   }
   if(Profile>=2&&tab==2){
    GUILayout.Label("LOCAL MODEL: "+edge.View.assistant_model,small);
    GUI.enabled=!measurement;if(GUILayout.Button("Explain observed evidence",button))edge.RequestAssistant();GUI.enabled=true;
    GUILayout.Label(edge.RequestStatus,small);var ai=edge.View.assistant;
    if(ai!=null&&!string.IsNullOrEmpty(ai.state)){GUILayout.Label("AI DRAFT • "+ai.state,heading);if(ai.state=="complete")GUILayout.Label(ai.text+"\nWall latency "+ai.latency_seconds.ToString("0.00")+" s • evidence age "+ai.evidence_age_sim_seconds.ToString("0.0")+" simulated seconds — statements require review",text);if(ai.state=="failed")GUILayout.Label(ai.error,small);}
    showProcedures=GUILayout.Toggle(showProcedures,"Show cited demo procedure sections",toggle,GUILayout.Width(278));
    if(showProcedures){var p=JsonUtility.FromJson<ProcedureSet>("{\"items\":"+File.ReadAllText(Path.Combine(Application.streamingAssetsPath,"procedures.json"))+"}");foreach(var item in p.items)GUILayout.Label(item.id+" • "+item.section+"\n"+item.text,small);}
   }
   GUILayout.Space(8);GUILayout.Label("MEASURED WORK / PERFORMANCE",heading);GUILayout.Label("Queue "+edge.View.queue_depth+" • running "+edge.View.running_task+"\nDropped work "+edge.View.dropped_work+" • completed calls "+edge.View.actual_calls+"\nTelemetry round trip "+edge.RoundTripMs.ToString("0.0")+" ms\nService processing "+edge.View.telemetry_processing_ms.ToString("0.00")+" ms\nPNG capture "+edge.CaptureMs.ToString("0.0")+" ms",small);
   GUILayout.Label("Same A395 in every mode; not three appliance benchmarks. Physical cause and remaining life unknown. Demo procedures require qualified review.",small);
  }
  void FocusedPanel(){
   GUILayout.Label("FOCUSED CAP INSPECTION",heading);GUILayout.Label("SYNTHETIC • simulator-assisted target association",small);
   GUILayout.Label(Profile<2?"Select Entry to run focused inspection":"Inspection triggers at neck crossing; camera refresh is not inspection throughput",small);
   var view=focused.View;GUILayout.Label(focused.Status,small);GUILayout.Label("Backend: "+view.backend+" • "+view.state,small);
   if(view.result!=null){var r=view.result;double age=0;DateTime utc;if(DateTime.TryParse(r.capture_utc,out utc))age=(DateTime.UtcNow-utc.ToUniversalTime()).TotalSeconds;
    GUILayout.Label(age>2?"HISTORICAL RESULT • current evidence stale":r.wording,heading);
    GUILayout.Label("Target "+r.target_id+" • age "+age.ToString("0.00")+" wall seconds\n"+r.association+" • frame "+r.frame_id,small);
    if(focused.Crop!=null&&focused.CropFrameId==r.frame_id)GUILayout.Label(focused.Crop,GUILayout.Width(270),GUILayout.Height(190));
    GUILayout.Label("Recorded assessment: "+r.wording+"\n"+r.reason+"\nCapture → result "+(r.latency_seconds*1000).ToString("0.0")+" ms; queue "+(r.queue_seconds*1000).ToString("0.0")+" ms\nUncalibrated classifier score "+r.score.ToString("0.00"),small);
   }else GUILayout.Label("Unable to assess — no completed target evidence",text);
   GUILayout.Label("Replay captured "+focused.Captured+"; service totals queued "+view.queued+" • inspected "+view.inspected+"\nUncertain "+view.uncertain+" • dropped "+(view.dropped+focused.Dropped)+" • stale "+view.stale+"\nQueue "+view.queue_depth+" • completed "+view.inspection_rate.ToString("0.00")+" inspections/s\nBudget 1000 per session • used "+focused.Captured,small);
   GUILayout.Label(view.evaluation_summary,small);
   GUILayout.Label("Pixels cannot establish attachment security, torque, seal integrity or leak-tightness. No physical reject/control. Synthetic evaluation is not real-camera validation.",small);
   if(tab==2){if(GUILayout.Button("Explain inspected evidence",button))focused.Explain();GUILayout.Label("LOCAL qwen3:8b • "+view.assistant_state+" • calls "+view.explanation_calls+"/6",small);GUILayout.Label("Explanation evidence: target "+view.assistant_target_id+" • "+view.assistant_frame_id+"\nCapture "+view.assistant_capture_utc+" • age "+view.assistant_age_seconds.ToString("0.0")+" wall seconds\nHistorical evidence; does not describe every current bottle. Request wall "+view.assistant_wall_seconds.ToString("0.00")+" s",small);GUILayout.Label(view.assistant_text,text);}
   GUILayout.Label("Old Gemma inspector retained only in original baseline; not run by this launch.",small);
  }
  void OnApplicationQuit(){
   string stamp=DateTime.UtcNow.ToString("yyyyMMddTHHmmssZ");
   File.WriteAllLines(Path.Combine(dataPath,"frames-"+stamp+".csv"),FrameLines());
   File.WriteAllLines(Path.Combine(dataPath,"telemetry-"+stamp+".csv"),TickLines());
   File.WriteAllText(Path.Combine(dataPath,"run-"+stamp+".json"),"{\"unity\":\""+Application.unityVersion+"\",\"graphics\":\""+SystemInfo.graphicsDeviceName+"\",\"api\":\""+SystemInfo.graphicsDeviceType+"\",\"width\":"+Screen.width+",\"height\":"+Screen.height+",\"vsync\":0,\"frame_cap\":"+Application.targetFrameRate+",\"profile\":"+Profile+",\"wall_seconds\":"+(Time.realtimeSinceStartupAsDouble-started).ToString("0.000",System.Globalization.CultureInfo.InvariantCulture)+",\"sim_time\":"+Sim.Time.ToString("0.000",System.Globalization.CultureInfo.InvariantCulture)+",\"packed\":"+Sim.Packed+",\"rejected\":"+Sim.Rejected+",\"process_rss_bytes\":"+Process.GetCurrentProcess().WorkingSet64+"}");
  }
  IEnumerable<string> FrameLines(){yield return "frame,wall_seconds,wall_frame_interval_ms";for(int i=0;i<frames.Count;i++)yield return i+","+frameWall[i].ToString("F6",System.Globalization.CultureInfo.InvariantCulture)+","+frames[i].ToString("F6",System.Globalization.CultureInfo.InvariantCulture);}
  IEnumerable<string> TickLines(){yield return "tick,processing_ms";for(int i=0;i<tickTimes.Count;i++)yield return i+","+tickTimes[i].ToString("F6",System.Globalization.CultureInfo.InvariantCulture);}
 }
}
