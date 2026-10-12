using System;
using System.IO;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using UnityEngine;
using UnityEngine.Networking;
namespace Braemac.Factory {
 [Serializable] public class InspectionInput {
  public string contract="gts.focused-frame/1",frame_id,capture_utc,target_id,session,association="simulator-assisted",image;
  public int target_count;public bool observations_available=true;public int[] roi;
 }
 [Serializable] public class InspectionResult {
  public string frame_id,capture_utc,target_id,decision,wording,reason,backend,association,completed_utc,crop_url,status;
  public double latency_seconds,queue_seconds,classifier_seconds,score;
 }
 [Serializable] public class InspectionSnapshot {
  public string session,state,backend,summary,evaluation_summary,assistant_text,assistant_state,assistant_capture_utc,assistant_frame_id,assistant_target_id;
  public InspectionResult result; public int captured,queued,inspected,uncertain,dropped,stale,queue_depth,explanation_calls;
  public double elapsed_seconds,inspection_rate,assistant_wall_seconds,assistant_age_seconds;
 }
 [Serializable] public class DatasetItem {
  public string id,sequence,group,split,label;public int seed,adjacent,quality_mode;
  public bool cap_present,cap_displaced;public float light,ambient,camera_x,camera_y,position_x,rotation,cap_color,offset,tilt;
 }
 [Serializable] public class DatasetPlan {public DatasetItem[] items;}
 public sealed class FocusedInspection:MonoBehaviour {
  public InspectionSnapshot View=new InspectionSnapshot();public Texture2D Crop;public string CropFrameId="";public string Status="Inspection service connecting";
  public int Captured,Dropped;public double CaptureMs;public string Session=Guid.NewGuid().ToString("N");
  FactoryApp app;Camera camera;RenderTexture feed;Texture2D pixels;HashSet<int> seen=new HashSet<int>();string endpoint,knownFrame="",dataset;float pollAt;bool sending,polling;
  void Start(){
   app=GetComponent<FactoryApp>();endpoint=FactoryApp.Argument("--inspection-endpoint","http://127.0.0.1:8810");
   var uri=new Uri(endpoint);if(uri.Host!="127.0.0.1"&&uri.Host!="localhost")throw new Exception("Inspection must remain local");
   camera=new GameObject("Fixed synthetic inspection view").AddComponent<Camera>();camera.enabled=false;camera.fieldOfView=38;camera.nearClipPlane=.02f;camera.farClipPlane=40;
   camera.transform.position=new Vector3(3,2.25f,-.58f);camera.transform.LookAt(new Vector3(3,1.74f,0));
   feed=new RenderTexture(512,384,24);camera.targetTexture=feed;camera.clearFlags=CameraClearFlags.SolidColor;camera.backgroundColor=new Color(.025f,.045f,.07f);
   pixels=new Texture2D(512,384,TextureFormat.RGB24,false);dataset=FactoryApp.Argument("--inspection-dataset");
   if(dataset!="")StartCoroutine(Dataset());
  }
  void Update(){
   if(app==null||dataset!="")return;
   if(Time.realtimeSinceStartup>=pollAt&&!polling){pollAt=Time.realtimeSinceStartup+.2f;StartCoroutine(Poll());}
   if(app.Paused||app.Profile<2)return;
   // Position/identity trigger only. No cap flags, presence switch or injected state used.
   foreach(var b in app.Sim.Bottles){
    if(b.X>=2.92f&&b.X<=3.08f&&!seen.Contains(b.Id)){
     seen.Add(b.Id);int count=0;foreach(var other in app.Sim.Bottles)if(Mathf.Abs(other.X-b.X)<.36f&&other.RejectTravel<.1f)count++;
     if(sending||Captured>=1000){Dropped++;continue;}
     StartCoroutine(CaptureAndSend(b,count));break;
    }
   }
  }
  int[] Region(Vector3 center){
   Vector3 lo=camera.WorldToScreenPoint(center+new Vector3(-.18f,-.17f,0)),hi=camera.WorldToScreenPoint(center+new Vector3(.18f,.17f,0));
   int x=Mathf.Clamp(Mathf.FloorToInt(Mathf.Min(lo.x,hi.x)),0,511),right=Mathf.Clamp(Mathf.CeilToInt(Mathf.Max(lo.x,hi.x)),1,512);
   int bottom=Mathf.Clamp(Mathf.FloorToInt(Mathf.Min(lo.y,hi.y)),0,383),top=Mathf.Clamp(Mathf.CeilToInt(Mathf.Max(lo.y,hi.y)),1,384);
   return new int[]{x,384-top,right-x,top-bottom}; // PNG top-left coordinates; geometric neck ROI
  }
  byte[] Read(){camera.Render();var old=RenderTexture.active;RenderTexture.active=feed;pixels.ReadPixels(new Rect(0,0,512,384),0,0);pixels.Apply();RenderTexture.active=old;return pixels.EncodeToPNG();}
  IEnumerator CaptureAndSend(Bottle target,int count){
   sending=true;yield return new WaitForEndOfFrame();
   string utc=DateTime.UtcNow.ToString("o");double start=Time.realtimeSinceStartupAsDouble;byte[] png=Read();CaptureMs=(Time.realtimeSinceStartupAsDouble-start)*1000;Captured++;
   Vector3 position=app.Geometry.Products.ContainsKey(target.Id)?app.Geometry.Products[target.Id].Root.transform.position:new Vector3(target.X,1.01f,0);
   bool observed=false;foreach(var o in app.Sim.Observations)if(o.bottle_id==target.Id){observed=true;if(!o.has_value||o.quality!="good"){observed=false;break;}}
   var input=new InspectionInput{frame_id=Session+"-"+Captured,capture_utc=utc,target_id=target.Id.ToString(),session=Session,target_count=count,
    observations_available=observed&&app.Geometry.Products.ContainsKey(target.Id),roi=Region(position+new Vector3(0,.75f,0)),image=Convert.ToBase64String(png)};
   File.AppendAllText(Path.Combine(app.DataPath,"focused-capture.jsonl"),"{\"frame_id\":\""+input.frame_id+"\",\"capture_ms\":"+CaptureMs.ToString("F3",System.Globalization.CultureInfo.InvariantCulture)+",\"target_id\":\""+input.target_id+"\",\"target_count\":"+count+"}\n");
   using(var request=Post("/frame",JsonUtility.ToJson(input))){request.timeout=3;yield return request.SendWebRequest();if(request.result!=UnityWebRequest.Result.Success){Dropped++;Status="Frame not accepted: "+request.downloadHandler.text;}else Status="Local focused inspector online";}
   sending=false;
  }
  UnityWebRequest Post(string path,string json){var r=new UnityWebRequest(endpoint+path,"POST");r.uploadHandler=new UploadHandlerRaw(Encoding.UTF8.GetBytes(json));r.downloadHandler=new DownloadHandlerBuffer();r.SetRequestHeader("Content-Type","application/json");return r;}
  IEnumerator Poll(){
   polling=true;using(var r=UnityWebRequest.Get(endpoint+"/state")){r.timeout=2;yield return r.SendWebRequest();if(r.result==UnityWebRequest.Result.Success){var snapshot=JsonUtility.FromJson<InspectionSnapshot>(r.downloadHandler.text);if(snapshot.session==Session)View=snapshot;if(View.result!=null&&View.result.frame_id!=knownFrame){knownFrame=View.result.frame_id;StartCoroutine(GetCrop(knownFrame));}}else {Status="Focused inspector unavailable; evidence withheld";View=new InspectionSnapshot();}}
   polling=false;
  }
  IEnumerator GetCrop(string id){using(var r=UnityWebRequest.Get(endpoint+"/crop/"+id)){r.timeout=2;yield return r.SendWebRequest();if(r.result==UnityWebRequest.Result.Success&&id==knownFrame){var t=new Texture2D(2,2);if(t.LoadImage(r.downloadHandler.data)){if(Crop!=null)Destroy(Crop);Crop=t;CropFrameId=id;}else Destroy(t);}}}
  public void Explain(){if(View.result==null||!View.result.frame_id.StartsWith(Session+"-")){Status="Wait for fresh evidence in this replay; no model request sent";return;}StartCoroutine(Explanation());}
  IEnumerator Explanation(){using(var r=Post("/explain","{}")){r.timeout=3;yield return r.SendWebRequest();Status=r.result==UnityWebRequest.Result.Success?"Explanation queued; inspection remains authoritative":"Explanation not accepted: "+r.downloadHandler.text;}}
  public void NewSession(){Session=Guid.NewGuid().ToString("N");seen.Clear();Captured=0;Dropped=0;knownFrame="";View=new InspectionSnapshot();if(Crop!=null)Destroy(Crop);Crop=null;CropFrameId="";}
  IEnumerator Dataset(){
   string path=Path.GetFullPath(dataset);Directory.CreateDirectory(Path.Combine(path,"frames"));
   var plan=JsonUtility.FromJson<DatasetPlan>(File.ReadAllText(Path.Combine(path,"capture-plan.json")));
   yield return new WaitForEndOfFrame();BottleVisual visual=null;foreach(var v in app.Geometry.Products.Values){visual=v;break;}
   if(visual==null)throw new Exception("Existing scene bottle unavailable");
   var cover=GameObject.CreatePrimitive(PrimitiveType.Cube);cover.GetComponent<Collider>().enabled=false;cover.GetComponent<Renderer>().material=new Material(Shader.Find("Standard"));cover.GetComponent<Renderer>().material.color=new Color(.15f,.18f,.19f);cover.transform.localScale=new Vector3(.4f,.32f,.03f);
   foreach(var item in plan.items){
    yield return new WaitForEndOfFrame();foreach(var v in app.Geometry.Products.Values)v.Root.SetActive(false);visual.Root.SetActive(true);
    visual.Root.transform.position=new Vector3(item.position_x+(item.adjacent-1.5f)*.008f,1.01f,0);visual.Root.transform.rotation=Quaternion.Euler(0,item.rotation,0);
    visual.Cap.SetActive(item.cap_present);visual.Cap.transform.localPosition=new Vector3(item.offset,.76f,0);visual.Cap.transform.localRotation=Quaternion.Euler(0,0,item.tilt);
    visual.Cap.GetComponent<Renderer>().material.color=new Color(.02f,item.cap_color*.8f,item.cap_color);
    foreach(var light in FindObjectsByType<Light>(FindObjectsSortMode.None))if(light.name.Contains("key"))light.intensity=item.light;
    RenderSettings.ambientLight=new Color(item.ambient,item.ambient*1.1f,item.ambient*1.2f);
    camera.transform.position=new Vector3(3+item.camera_x,2.25f+item.camera_y,-.58f);camera.transform.LookAt(new Vector3(3,1.74f,0));
    cover.SetActive(item.quality_mode==0);cover.transform.position=new Vector3(visual.Root.transform.position.x,1.8f,-.10f);
    byte[] png=Read();File.WriteAllBytes(Path.Combine(path,"frames",item.id+".png"),png);
    var metadata=new InspectionInput{frame_id=item.id,capture_utc=DateTime.UtcNow.ToString("o"),target_id="dataset-target",session="dataset",target_count=1,roi=Region(visual.Root.transform.position+new Vector3(0,.75f,0)),image=""};
    File.AppendAllText(Path.Combine(path,"acquisition.jsonl"),JsonUtility.ToJson(metadata)+"\n");
   }
   Debug.Log("FOCUSED_DATASET_CAPTURED "+plan.items.Length);Application.Quit();
  }
 }
}
