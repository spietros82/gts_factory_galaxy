using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using UnityEngine;
using UnityEngine.Networking;
using Debug=UnityEngine.Debug;
namespace Braemac.Factory {
 // All three station views are isolated by layer10 AND far clip. A single controlled light
 // and sequential Render protect the frozen illumination from multi-line light accumulation.
 public sealed class LineVisual {
  public IndependentLine State;public FactoryGeometry Geometry;public BreweryPresentation Brewery;public Vector3 Origin;
  public Camera[] Cameras=new Camera[3];public HashSet<int> Seen=new HashSet<int>();public int Captured,Accepted,Dropped;public bool Sending;public double NextCapture,PendingAt;public Bottle PendingBottle;public string Example="Healthy";
  public readonly List<UnityEngine.Object> Owned=new List<UnityEngine.Object>();
  public void Dispose(){foreach(var root in new[]{Geometry.Root,Brewery.Root})if(root!=null)foreach(var filter in root.GetComponentsInChildren<MeshFilter>(true)){var mesh=filter.sharedMesh;if(mesh!=null&&(mesh.name.StartsWith("Lathed synthetic")||mesh.name.StartsWith("Procedural amber"))&&!Owned.Contains(mesh))Owned.Add(mesh);}UnityEngine.Object.Destroy(Geometry.Root);UnityEngine.Object.Destroy(Brewery.Root);foreach(var c in Cameras)if(c!=null)UnityEngine.Object.Destroy(c.gameObject);foreach(var a in Owned)UnityEngine.Object.Destroy(a);}
 }
 public sealed class MultiLineCapture {
  public readonly StationCameraSet Config;readonly RenderTexture[] targets=new RenderTexture[3];readonly Texture2D[] readers=new Texture2D[3];readonly GameObject cover;
  public MultiLineCapture(){Config=JsonUtility.FromJson<StationCameraSet>(File.ReadAllText(Path.Combine(Application.streamingAssetsPath,"stage3-cameras.json")));
   var light=new GameObject("Shared frozen inspection light").AddComponent<Light>();light.type=LightType.Directional;light.intensity=1.2f;light.color=Color.white;light.cullingMask=1<<10;light.transform.rotation=Quaternion.Euler(12,-10,0);
   cover=GameObject.CreatePrimitive(PrimitiveType.Cube);cover.layer=10;UnityEngine.Object.Destroy(cover.GetComponent<Collider>());cover.GetComponent<Renderer>().material=new Material(Shader.Find("Standard"));cover.GetComponent<Renderer>().material.color=new Color(.18f,.18f,.18f);cover.transform.localScale=new Vector3(.7f,1.3f,.03f);cover.SetActive(false);
   for(int i=0;i<3;i++){targets[i]=new RenderTexture(256,256,24);readers[i]=new Texture2D(256,256,TextureFormat.RGB24,false);}
  }
  public void Configure(LineVisual line){for(int i=0;i<3;i++){var c=new GameObject(line.State.Id+" "+Config.stations[i].station_id+" station camera").AddComponent<Camera>();c.enabled=false;c.cullingMask=1<<10;c.orthographic=true;c.orthographicSize=Config.stations[i].orthographic_size;c.nearClipPlane=.02f;c.farClipPlane=4;c.backgroundColor=new Color(.72f,.75f,.76f);c.clearFlags=CameraClearFlags.SolidColor;c.targetTexture=targets[i];line.Cameras[i]=c;}Position(line);}
  public void Position(LineVisual line){for(int i=0;i<3;i++){float y=1.01f+Config.stations[i].center_y;line.Cameras[i].transform.position=line.Origin+new Vector3(Config.trigger_x,y,-.8f);line.Cameras[i].transform.LookAt(line.Origin+new Vector3(Config.trigger_x,y,0));}}
  static void Layer(GameObject root,int value){foreach(var t in root.GetComponentsInChildren<Transform>(true))t.gameObject.layer=value;}
  public void Examples(LineVisual line){foreach(var b in line.State.Sim.Bottles){if(b.Stage<4)continue;var v=line.Brewery.BottleById(b.Id);if(v==null)continue;var label=v.Root.transform.Find("Readable wrap label");
   if(line.Example=="Cap missing")v.Cap.SetActive(false);if(line.Example=="Cap displaced"){v.Cap.SetActive(true);v.Cap.transform.localPosition=new Vector3(.08f,.76f,0);v.Cap.transform.localRotation=Quaternion.Euler(0,0,20);}
   if(line.Example=="Underfill"||line.Example=="Overfill"){float f=line.Example=="Underfill"?.84f:1.14f;v.Fluid.transform.localScale=new Vector3(.305f,.43f*f/2,.305f);v.Fluid.transform.localPosition=new Vector3(0,.04f+.43f*f/2,0);}
   label.gameObject.SetActive(line.Example!="Label missing");label.localPosition=new Vector3(0,line.Example=="Label tilted"?.33f:.27f,0);label.localRotation=Quaternion.Euler(0,0,line.Example=="Label tilted"?22:0);
  }}
  public ThreeBatch Capture(LineVisual line,Bottle bottle,bool posed,out double renderMs,out double readMs,out double encodeMs){
   var visual=line.Brewery.BottleById(bottle.Id);if(visual==null)throw new InvalidOperationException("Target disappeared");var begin=DateTime.UtcNow;var previous=visual.Root.transform.position;int count=0;
   foreach(var b in line.State.Sim.Bottles)if(Math.Abs(b.X-bottle.X)<.36f&&b.RejectTravel<.1f)count++;
   if(posed)visual.Root.transform.position=line.Origin+new Vector3(Config.trigger_x,1.01f,0);
   renderMs=readMs=encodeMs=0;var frames=new ThreeFrame[3];Layer(visual.Root,10);cover.SetActive(line.Example=="Poor image");cover.transform.position=line.Origin+new Vector3(3,1.45f,-.3f);
   try{for(int i=0;i<3;i++){var sw=Stopwatch.StartNew();line.Cameras[i].Render();renderMs+=sw.Elapsed.TotalMilliseconds;sw.Restart();var old=RenderTexture.active;try{RenderTexture.active=targets[i];readers[i].ReadPixels(new Rect(0,0,256,256),0,0);readers[i].Apply();}finally{RenderTexture.active=old;}readMs+=sw.Elapsed.TotalMilliseconds;sw.Restart();var png=readers[i].EncodeToPNG();encodeMs+=sw.Elapsed.TotalMilliseconds;frames[i]=new ThreeFrame{station_id=Config.stations[i].station_id,frame_id=Guid.NewGuid().ToString("N"),image=Convert.ToBase64String(png),roi=new[]{Mathf.Clamp(Mathf.RoundToInt(line.Cameras[i].WorldToScreenPoint(visual.Root.transform.position+Vector3.up*Config.stations[i].center_y).x)-80,0,96),48,160,160}};}}
   finally{Layer(visual.Root,9);visual.Root.transform.position=previous;cover.SetActive(false);}
   return new ThreeBatch{line_id=line.State.Id,session_id=line.State.Adapter.Session,bottle_id=bottle.Id.ToString(),batch_id=Guid.NewGuid().ToString("N"),capture_utc=begin.ToString("o"),source_time=line.State.Sim.Time,product=line.Brewery.Product,target_count=count,frames=frames};
  }
  public void Dispose(){foreach(var r in readers)UnityEngine.Object.Destroy(r);foreach(var t in targets){t.Release();UnityEngine.Object.Destroy(t);}UnityEngine.Object.Destroy(cover);}
 }
}
