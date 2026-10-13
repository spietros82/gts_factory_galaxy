using System;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
namespace Braemac.Factory {
 public sealed class PlcPresentation {
  readonly FactoryApp app;SimulatedPlcAdapter adapter=new SimulatedPlcAdapter();public readonly PlcMapping Mapping=new PlcMapping();
  public string Mode="combined";public bool Suspended,Missing;bool lastPaused;double auditAt,pausedPublishAt;
  readonly List<string> timeline=new List<string>();readonly Dictionary<string,string> previous=new Dictionary<string,string>();
  readonly Dictionary<string,TextMesh> signs=new Dictionary<string,TextMesh>();Vector2 scroll;bool raw;
  GUIStyle title,text,small,button;Texture2D panel,backdrop;
  public PlcPresentation(FactoryApp app){this.app=app;Mode=FactoryApp.Argument("--telemetry-view","combined");if(Mode!="data"&&Mode!="twin"&&Mode!="combined")Mode="combined";
   int i=0;foreach(string asset in new[]{"infeed","filler","capper","inspection","packer"}){
    var o=new GameObject("Telemetry status "+asset);o.layer=BreweryPresentation.PresentationLayer;o.transform.position=new Vector3(new[]{-11f,-7f,-2f,3f,10f}[i++],1.65f,-1.2f);
    var t=o.AddComponent<TextMesh>();t.anchor=TextAnchor.MiddleCenter;t.characterSize=.045f;t.fontSize=48;t.color=Color.white;signs[asset]=t;
   }Capture();Event("New session • healthy seeded line (40 s pre-roll)");}
  public void Event(string value){timeline.Add(app.Sim.Time.ToString("0.00")+" s  "+value);if(timeline.Count>32)timeline.RemoveAt(0);}
  public void Reset(){adapter=new SimulatedPlcAdapter();timeline.Clear();previous.Clear();Suspended=false;Missing=false;Capture();Event("New session • reset to healthy seeded line (40 s pre-roll)");}
  public void Capture(){if(Suspended)return;var f=adapter.Capture(app.Sim,app.Paused);
   if(Missing)foreach(var t in f.tags)if(t.asset=="filler"){t.has_value=false;t.quality="missing";}
   Mapping.Receive(f,Time.realtimeSinceStartupAsDouble);
   foreach(var t in f.tags)if(t.name.EndsWith(".AccumulationHigh")){
    string v=t.Value;if(previous.ContainsKey(t.name)&&previous[t.name]!=v)Event(t.boolean?"PLC accumulation high • buffer ≥15":"PLC accumulation signal cleared • buffer <15");previous[t.name]=v;
   }
  }
  public void StartScenario(){app.Sim.PresenterFault("outfeed");Capture();Event("Presenter started outfeed blockage • packing restricted, not instant line stop");}
  public void Clear(){app.Sim.ClearOutfeed();Capture();Event("Presenter cleared blockage • flow recovering; historical alarms retained");}
  public void Update(){
   if(lastPaused!=app.Paused){lastPaused=app.Paused;Capture();Event(app.Paused?"Simulation paused • clock held, not a machine fault":"Simulation resumed");}
   if(app.Paused&&!Suspended&&Time.realtimeSinceStartupAsDouble>=pausedPublishAt){pausedPublishAt=Time.realtimeSinceStartupAsDouble+.05;Capture();}
   if(Input.GetKeyDown(KeyCode.Alpha1))Mode="data";if(Input.GetKeyDown(KeyCode.Alpha2))Mode="twin";if(Input.GetKeyDown(KeyCode.Alpha3))Mode="combined";
   if(!app.Measurement){if(Input.GetKeyDown(KeyCode.B))StartScenario();if(Input.GetKeyDown(KeyCode.C))Clear();if(Input.GetKeyDown(KeyCode.R))app.ResetLine();}
   if(FactoryApp.Argument("--telemetry-dev","false")=="true"){
    if(Input.GetKeyDown(KeyCode.F9)){Suspended=!Suspended;Event(Suspended?"Development test: adapter publication suspended":"Development test: adapter publication resumed");if(!Suspended)Capture();}
    if(Input.GetKeyDown(KeyCode.F10)){Missing=!Missing;Capture();Event(Missing?"Development test: filler values missing":"Development test: filler values restored");}
   }
   if(FactoryApp.Argument("--comparison-camera","false")!="true"){
    float s=Mathf.Max(.7f,Screen.width/1600f);app.MainCamera.enabled=true;app.MainCamera.cullingMask=Mode=="data"?0:~(1<<BreweryPresentation.LegacyLayer);app.MainCamera.rect=Mode=="data"?new Rect(0,0,1,1):new Rect(0,65*s/Screen.height,Mode=="combined"?.63f:.77f,1-302*s/Screen.height);
   }
   foreach(var p in signs){p.Value.text=(app.Selected==p.Key?"▶ ":"")+p.Key.ToUpperInvariant()+"\n"+Mapping.State(p.Key,Time.realtimeSinceStartupAsDouble);p.Value.color=app.Selected==p.Key?new Color(.5f,1,1):Color.white;p.Value.transform.rotation=Quaternion.LookRotation(p.Value.transform.position-app.MainCamera.transform.position);}
  }
  public void AfterVisual(){if(FactoryApp.Argument("--telemetry-audit","false")=="true"&&Time.realtimeSinceStartupAsDouble>=auditAt){auditAt=Time.realtimeSinceStartupAsDouble+.2;WriteAudit();}}
  [Serializable] class Audit {public string mode,selected,product,filler_state,capper_state,infeed_state,session;public bool paused,suspended,missing,blocked,fresh;public double sim_time;public int buffer,packed,produced;public float capper_angle,head_y,filler_screen_x,filler_screen_y;public PlcFrame frame;public string[] timeline;}
  void WriteAudit(){var f=Mapping.Frame;var screen=app.MainCamera.WorldToScreenPoint(new Vector3(-7,2,0));var a=new Audit{filler_screen_x=screen.x,filler_screen_y=Screen.height-screen.y,mode=Mode,selected=app.Selected,product=app.PresentationProduct,paused=app.Paused,sim_time=app.Sim.Time,buffer=app.Sim.BufferCount,packed=app.Sim.Packed,produced=app.Sim.Produced,blocked=app.Sim.OutfeedRestricted,suspended=Suspended,missing=Missing,fresh=Mapping.Fresh(Time.realtimeSinceStartupAsDouble),filler_state=Mapping.State("filler",Time.realtimeSinceStartupAsDouble),capper_state=Mapping.State("capper",Time.realtimeSinceStartupAsDouble),infeed_state=Mapping.State("infeed",Time.realtimeSinceStartupAsDouble),capper_angle=app.Geometry.Moving["capper"].eulerAngles.y,head_y=app.Geometry.Moving["head0"].localPosition.y,session=f==null?"":f.session,frame=f,timeline=timeline.ToArray()};File.WriteAllText(Path.Combine(app.DataPath,"telemetry-audit.json"),JsonUtility.ToJson(a));}
  void Styles(){if(title!=null)return;panel=new Texture2D(1,1);panel.SetPixel(0,0,new Color(.025f,.055f,.09f,.97f));panel.Apply();title=new GUIStyle(GUI.skin.label){fontSize=21,fontStyle=FontStyle.Bold,normal={textColor=new Color(.83f,.96f,1)},wordWrap=true};text=new GUIStyle(GUI.skin.label){fontSize=14,wordWrap=true,normal={textColor=new Color(.88f,.94f,.98f)}};small=new GUIStyle(text){fontSize=12};button=new GUIStyle(GUI.skin.button){fontSize=14,fixedHeight=32};}
  void Select(string asset){if(asset=="line"){app.Overview();return;}if(asset=="conveyor"){app.Overview();app.Selected="conveyor";return;}app.RemoteAction("machine",asset);}
  void ModeButton(string label,string value){GUI.backgroundColor=Mode==value?new Color(.25f,.62f,.67f):Color.white;if(GUILayout.Button(label,button))Mode=value;GUI.backgroundColor=Color.white;}
  string Value(string key){var t=Mapping.Frame==null?null:Mapping.Frame.Find("Line01."+key);return Mapping.Quality(t,Time.realtimeSinceStartupAsDouble)=="good"?t.Value:Mapping.Quality(t,Time.realtimeSinceStartupAsDouble);}
  void ClearMargins(float scale){
   // The camera clears only its viewport. Repaint every outside pixel each GUI
   // frame so old panels cannot survive a mode change or window resize.
   if(backdrop==null){backdrop=new Texture2D(1,1);var color=app.MainCamera.backgroundColor;color.a=1;backdrop.SetPixel(0,0,color);backdrop.Apply();}
   Rect pixels=app.MainCamera.pixelRect;
   float w=Screen.width/scale,h=Screen.height/scale,left=pixels.xMin/scale,right=pixels.xMax/scale,top=(Screen.height-pixels.yMax)/scale,bottom=(Screen.height-pixels.yMin)/scale;
   if(top>0)GUI.DrawTexture(new Rect(0,0,w,top),backdrop);
   if(bottom<h)GUI.DrawTexture(new Rect(0,bottom,w,h-bottom),backdrop);
   if(left>0)GUI.DrawTexture(new Rect(0,top,left,bottom-top),backdrop);
   if(right<w)GUI.DrawTexture(new Rect(right,top,w-right,bottom-top),backdrop);
  }
  public void Draw(){Styles();float scale=Mathf.Max(.7f,Screen.width/1600f);GUI.matrix=Matrix4x4.Scale(new Vector3(scale,scale,1));float w=Screen.width/scale,h=Screen.height/scale;ClearMargins(scale);
   GUI.DrawTexture(new Rect(18,18,w-36,212),panel);GUILayout.BeginArea(new Rect(34,25,w-68,202));
   GUILayout.Label("BRAEMAC  /  BREWERY MACHINE DATA → DIGITAL TWIN",title);
   GUILayout.Label("Simulated PLC telemetry — no physical equipment connected. No AI dependency.",text);
   GUILayout.BeginHorizontal();ModeButton("1  Machine data","data");ModeButton("2  Digital twin","twin");ModeButton("3  Combined view","combined");GUILayout.EndHorizontal();
   GUILayout.BeginHorizontal();GUI.enabled=!app.Measurement;if(GUILayout.Button(app.Paused?"Play · Space":"Pause · Space",button,GUILayout.Width(130)))app.TogglePause();if(GUILayout.Button("Reset · R",button,GUILayout.Width(110)))app.ResetLine();if(GUILayout.Button("Start blockage · B",button,GUILayout.Width(180)))StartScenario();if(GUILayout.Button("Clear blockage · C",button,GUILayout.Width(185)))Clear();GUILayout.Label("Speed",text,GUILayout.Width(60));app.SimulationSpeed=GUILayout.HorizontalSlider(app.SimulationSpeed,.25f,8,GUILayout.Width(90));GUILayout.Label(app.SimulationSpeed.ToString("0.0")+"×",text,GUILayout.Width(40));GUI.enabled=true;GUILayout.FlexibleSpace();GUILayout.Label((app.Paused?"SIMULATION PAUSED • not a fault":"SIMULATION RUNNING")+"  "+app.Sim.Time.ToString("0.00")+" s",text);GUILayout.EndHorizontal();
   GUILayout.BeginHorizontal();foreach(string p in new[]{"LAGER","IPA","STOUT"})if(GUILayout.Button((app.PresentationProduct==p?"● ":"")+p,button,GUILayout.Width(90)))app.SelectProduct(p);GUILayout.Space(20);if(GUILayout.Button("Overview · F5",button))app.Overview();if(GUILayout.Button("Filler · F6",button))app.SelectPresentationView("filler");if(GUILayout.Button("Capper · F7",button))app.SelectPresentationView("capper");if(GUILayout.Button("Inspection · F8",button))app.SelectPresentationView("inspection");GUILayout.EndHorizontal();
   GUILayout.EndArea();
   float left=Mode=="data"?18:Mode=="combined"?w*.63f+8:w-355;float width=w-left-18;
   GUI.DrawTexture(new Rect(left,240,width,h-310),panel);GUILayout.BeginArea(new Rect(left+14,250,width-28,h-333));
   GUILayout.Label(Mode=="twin"?"MACHINE STATUS":"LIVE MACHINE DATA",title);
   GUILayout.Label("Buffer "+Value("Outfeed.BufferCount")+" • packed "+Value("Outfeed.PackedTotal")+" • restricted "+Value("Outfeed.Blocked"),text);
   GUILayout.Label("Source sim "+(Mapping.Frame==null?"unknown":Mapping.Frame.source_time.ToString("0.00"))+" s • "+(Mapping.Fresh(Time.realtimeSinceStartupAsDouble)?"Good / 20 Hz":"STALE / unknown current state")+(Missing?" • filler MISSING":""),small);
   scroll=GUILayout.BeginScrollView(scroll,false,false,GUILayout.ExpandHeight(true));
   if(Mode=="twin")foreach(string asset in new[]{"infeed","filler","capper","inspection","packer"}){if(GUILayout.Button((app.Selected==asset?"▶ ":"")+asset.ToUpperInvariant()+"  ·  "+Mapping.State(asset,Time.realtimeSinceStartupAsDouble),button))Select(asset);}
   else{
    GUILayout.BeginHorizontal();foreach(string asset in new[]{"line","infeed","filler","capper"})if(GUILayout.Button(asset=="line"?"All":asset,button))Select(asset);GUILayout.EndHorizontal();GUILayout.BeginHorizontal();foreach(string asset in new[]{"inspection","packer","conveyor"})if(GUILayout.Button(asset,button))Select(asset);GUILayout.EndHorizontal();
    GUILayout.Label("Click a tag to locate its machine. Calculated values marked [calc].",small);
    if(Mapping.Frame!=null)foreach(var t in Mapping.Frame.tags){if(app.Selected!="line"&&app.Selected!=t.asset)continue;
     string q=Mapping.Quality(t,Time.realtimeSinceStartupAsDouble);string value=q=="good"?t.Value:q=="Stale"?"Stale (last "+t.Value+")":"Unknown";
     GUILayout.BeginHorizontal();if(GUILayout.Button(t.name.Substring(7),button,GUILayout.Width(Mode=="data"?310:Mathf.Max(145,width*.43f))))Select(t.asset);GUILayout.Label(value+"  "+t.unit,text);GUILayout.EndHorizontal();
     GUILayout.Label(t.name+" • "+t.source_time.ToString("0.00")+" s • "+q+(t.origin.StartsWith("calculated")?" • [calc]":" • simulated"),small);
    }
    raw=GUILayout.Toggle(raw,"Presenter: compact raw contract",small);if(raw&&Mapping.Frame!=null)GUILayout.TextArea(JsonUtility.ToJson(Mapping.Frame),small);
   }
   GUILayout.EndScrollView();GUILayout.Space(10);GUILayout.Label("EVENT TIMELINE • SIMULATION TIME",title);for(int i=Math.Max(0,timeline.Count-3);i<timeline.Count;i++)GUILayout.Label(timeline[i],small);
   GUILayout.Space(8);GUILayout.Label("Locally Blocked means queued, not a diagnosed fault. Packing cadence: restricted 3.4 s → cleared 0.5 s. Alarm history retained.",small);
   GUILayout.Label("Contract drives station status + mechanisms. Simulator directly drives bottle travel, fill and cap appearance.",small);
   GUILayout.Label("Frozen old cyan-cap inspection configuration preserved; new brewery appearance unvalidated. No model requests.",small);
   if(FactoryApp.Argument("--telemetry-dev","false")=="true")GUILayout.Label("DEVELOPMENT ONLY • F9 suspend/resume publication; F10 missing/restore filler. No equipment commands.",small);
   GUILayout.EndArea();
   GUI.DrawTexture(new Rect(18,h-58,w-36,42),panel);GUI.Label(new Rect(30,h-53,w-60,22),"SIMULATED • One process clock • Session "+(Mapping.Frame==null?"unknown":Mapping.Frame.session.Substring(0,8))+" • "+app.PresentationProduct+" • "+(app.Paused?"Clock held":"Flow live")+" • Rendering "+app.FrameMilliseconds.ToString("0.0")+" ms • F12 screenshot",text);GUI.Label(new Rect(30,h-32,w-60,20),"Frozen cyan-cap inspection configuration preserved • Brewery appearance unvalidated • No AI or inspection inference",small);GUI.matrix=Matrix4x4.identity;
  }
 }
}
