using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
namespace Braemac.Factory {
 [Serializable] public class FactoryConfig {public string service_endpoint="http://127.0.0.1:8800";public int frame_cap=60,camera_width=640,camera_height=480;public float entry_capture_seconds=12,higher_capture_seconds=6;}
 [Serializable] public class ObservationBatch {public string contract="gts.observation-batch/1",session;public double sim_time;public int profile;public Observation[] observations;}
 [Serializable] public class AnalysisView {public string id,category,title,uncertainty;public bool flagged;public string[] evidence_ids;}
 [Serializable] public class AssistantView {public string state,request_id,model,text,error,completed_utc;public double latency_seconds,evidence_age_sim_seconds,evidence_sim_time;}
 [Serializable] public class VisionView {public string state,request_id,model,error,cap_result,observation,frame_id,capture_utc,completed_utc,camera_id,unvalidated;public int bottle_id;public double latency_seconds,evidence_age_sim_seconds,evidence_sim_time;}
 [Serializable] public class ServiceView {public string contract,session,running_task,assistant_model,vision_model,compute_summary,compute_technical;public int profile,queue_depth,dropped_work,actual_calls;public AnalysisView[] analysis;public AssistantView assistant;public VisionView vision;public double telemetry_processing_ms,sim_time;public bool inference_enabled;}
 [Serializable] public class CameraFrame {public string contract="gts.camera-frame/1",frame_id,capture_utc,camera_id,image,session;public int bottle_id;}
 [Serializable] public class ScoringTruth {public string frame_id;public int bottle_id;public bool cap_present,cap_displaced;public double sim_time;}
 [Serializable] public class ErrorView {public string error;}
 [Serializable] public class Procedure {public string id,section,text,review_status,version;}
 [Serializable] public class ProcedureSet {public Procedure[] items;}
 public sealed class EdgeClient:MonoBehaviour {
  public ServiceView View=new ServiceView();public string Status="Local service connecting",RequestStatus="No model request",Session=Guid.NewGuid().ToString("N");
  public int TransportDropped,CapturedFrames,RenderedCameraFrames;public double RoundTripMs,CaptureMs,CameraRate;float cameraWindow;int cameraInWindow;public RenderTexture Feed;public Texture2D ClassifiedFrame;public string ClassifiedFrameId="";string requestedFrame="";public FactoryConfig Config;
  FactoryApp app;Camera inspect;Texture2D capture;bool busy;float nextTelemetry,nextCapture,nextFeed;long lastSequence;LineSimulation current;
  double nextAssistant;float assistantEvery;int viewIndex;string endpoint;
  void Start(){
   app=GetComponent<FactoryApp>();Config=JsonUtility.FromJson<FactoryConfig>(File.ReadAllText(Path.Combine(Application.streamingAssetsPath,"factory-config.json")));
   endpoint=FactoryApp.Argument("--service-endpoint",Config.service_endpoint).TrimEnd('/');Application.targetFrameRate=int.Parse(FactoryApp.Argument("--frame-target",Config.frame_cap.ToString()));
   var uri=new Uri(endpoint);if(uri.Host!="127.0.0.1"&&uri.Host!="localhost")throw new Exception("Companion must remain local");
   inspect=new GameObject("Synthetic inspection camera").AddComponent<Camera>();inspect.enabled=false;inspect.fieldOfView=38;inspect.nearClipPlane=.02f;inspect.farClipPlane=40;
   Feed=new RenderTexture(Config.camera_width,Config.camera_height,24);inspect.targetTexture=Feed;inspect.backgroundColor=new Color(.025f,.045f,.07f);inspect.clearFlags=CameraClearFlags.SolidColor;
   capture=new Texture2D(Config.camera_width,Config.camera_height,TextureFormat.RGB24,false);float.TryParse(FactoryApp.Argument("--assistant-every","0"),out assistantEvery);
   nextAssistant=Time.realtimeSinceStartupAsDouble+15;nextCapture=12;cameraWindow=Time.realtimeSinceStartup;
  }
  void Update(){
   if(app==null)return;
   if(current!=app.Sim){current=app.Sim;Session=Guid.NewGuid().ToString("N");lastSequence=0;View=new ServiceView();requestedFrame="";if(ClassifiedFrame!=null)Destroy(ClassifiedFrame);ClassifiedFrame=null;ClassifiedFrameId="";RequestStatus="New replay; previous advice withheld";}
   if(Time.realtimeSinceStartup>=nextTelemetry){nextTelemetry=Time.realtimeSinceStartup+.5f;
    if(!busy)StartCoroutine(SendObservations());else TransportDropped++;}
   if(app.Profile>=2&&Time.realtimeSinceStartup>=nextFeed){nextFeed=Time.realtimeSinceStartup+.2f;RenderInspection(false);}
   if(!app.Paused&&app.Profile>=2&&Time.realtimeSinceStartup>=nextCapture){
    nextCapture=Time.realtimeSinceStartup+(app.Profile>=3?Config.higher_capture_seconds:Config.entry_capture_seconds);
    if(View.inference_enabled)RenderInspection(true);
   }
   if(!app.Paused&&assistantEvery>0&&app.Profile>=2&&Time.realtimeSinceStartupAsDouble>=nextAssistant){nextAssistant=Time.realtimeSinceStartupAsDouble+assistantEvery;RequestAssistant();}
  }
  IEnumerator SendObservations(){
   busy=true;var rows=new List<Observation>();foreach(var o in app.Sim.Observations)if(o.sequence>lastSequence)rows.Add(o);
   long sentMax=lastSequence;foreach(var o in rows)sentMax=Math.Max(sentMax,o.sequence);
   var body=new ObservationBatch{session=Session,sim_time=app.Sim.Time,profile=app.Profile,observations=rows.ToArray()};string session=Session;
   double started=Time.realtimeSinceStartupAsDouble;
   using(var request=Post("/observations",JsonUtility.ToJson(body))){request.timeout=3;yield return request.SendWebRequest();RoundTripMs=(Time.realtimeSinceStartupAsDouble-started)*1000;
    if(request.result==UnityWebRequest.Result.Success){var result=JsonUtility.FromJson<ServiceView>(request.downloadHandler.text);if(session==Session){View=result;lastSequence=sentMax;if(View.vision!=null&&View.vision.state=="complete"&&View.vision.frame_id!=requestedFrame){requestedFrame=View.vision.frame_id;StartCoroutine(RecordedFrame(requestedFrame));}}Status="Local observation service online";}
    else {Status="Service unavailable • current analytics withheld; line remains interactive";View=new ServiceView();}
   }
   File.AppendAllText(Path.Combine(app.DataPath,"transport.csv"),DateTime.UtcNow.ToString("o")+","+RoundTripMs.ToString("F4",System.Globalization.CultureInfo.InvariantCulture)+","+View.telemetry_processing_ms.ToString("F5",System.Globalization.CultureInfo.InvariantCulture)+","+TransportDropped+","+View.queue_depth+","+View.dropped_work+"\n");
   busy=false;
  }
  IEnumerator RecordedFrame(string id){
   using(var r=UnityWebRequest.Get(endpoint+"/frame/"+UnityWebRequest.EscapeURL(id))){r.timeout=3;yield return r.SendWebRequest();
    if(r.result==UnityWebRequest.Result.Success&&id==requestedFrame){var image=new Texture2D(2,2,TextureFormat.RGB24,false);if(image.LoadImage(r.downloadHandler.data)){if(ClassifiedFrame!=null)Destroy(ClassifiedFrame);ClassifiedFrame=image;ClassifiedFrameId=id;}else Destroy(image);}
   }
  }
  UnityWebRequest Post(string path,string json){var r=new UnityWebRequest(endpoint+path,"POST");r.uploadHandler=new UploadHandlerRaw(Encoding.UTF8.GetBytes(json));r.downloadHandler=new DownloadHandlerBuffer();r.SetRequestHeader("Content-Type","application/json");return r;}
  public void RequestAssistant(){
   if(app.Profile==1){RequestStatus="PLC-only mode: local AI not enabled";return;}
   if(View.assistant!=null&&(View.assistant.state=="queued"||View.assistant.state=="running")){RequestStatus="Request already pending";return;}
   StartCoroutine(Submit("/assistant","{}"));
  }
  string FailureText(string body){try{var error=JsonUtility.FromJson<ErrorView>(body);return string.IsNullOrEmpty(error.error)?"Local service unavailable":error.error;}catch{return "Local service unavailable";}}
  IEnumerator Submit(string path,string json){
   using(var r=Post(path,json)){r.timeout=3;yield return r.SendWebRequest();
    RequestStatus=r.result==UnityWebRequest.Result.Success?"Accepted by local service; inference asynchronous":"Request not accepted: "+FailureText(r.downloadHandler.text);
   }
  }
  void RenderInspection(bool submit){
   Bottle b=null;foreach(var candidate in app.Sim.Bottles)if(!candidate.Rejected&&candidate.Stage>=4&&candidate.X>1.8f&&candidate.X<4.4f&&(b==null||Mathf.Abs(candidate.X-3)<Mathf.Abs(b.X-3)))b=candidate;
   if(b==null)return;
   Vector3 p=new Vector3(b.X,1.55f,0);int camera=app.Profile>=3?viewIndex++%2:0;
   inspect.transform.position=p+new Vector3(camera==0?.1f:.22f,.4f,camera==0?-1.5f:1.4f);inspect.transform.LookAt(p);
   double start=Time.realtimeSinceStartupAsDouble;inspect.Render();RenderedCameraFrames++;cameraInWindow++;if(Time.realtimeSinceStartup-cameraWindow>=2){CameraRate=cameraInWindow/(Time.realtimeSinceStartup-cameraWindow);cameraWindow=Time.realtimeSinceStartup;cameraInWindow=0;}
   if(!submit)return;
   var old=RenderTexture.active;RenderTexture.active=Feed;capture.ReadPixels(new Rect(0,0,Feed.width,Feed.height),0,0);capture.Apply();RenderTexture.active=old;
   byte[] png=capture.EncodeToPNG();CaptureMs=(Time.realtimeSinceStartupAsDouble-start)*1000;CapturedFrames++;File.AppendAllText(Path.Combine(app.DataPath,"capture.csv"),DateTime.UtcNow.ToString("o")+","+CaptureMs.ToString("F4",System.Globalization.CultureInfo.InvariantCulture)+","+CapturedFrames+"\n");
   string id=Session+"-F"+CapturedFrames;string utc=DateTime.UtcNow.ToString("o");
   var frame=new CameraFrame{frame_id=id,capture_utc=utc,camera_id=camera==0?"side-A":"side-B",bottle_id=b.Id,image=Convert.ToBase64String(png),session=Session};
   File.AppendAllText(Path.Combine(app.DataPath,"camera-ground-truth.jsonl"),JsonUtility.ToJson(new ScoringTruth{frame_id=id,bottle_id=b.Id,cap_present=b.CapPresent,cap_displaced=b.CapDisplaced,sim_time=app.Sim.Time})+"\n");
   // Ground truth stays in a separate scoring file; only PNG pixels and association go to inference.
   StartCoroutine(Submit("/vision",JsonUtility.ToJson(frame)));
  }
 }
}
