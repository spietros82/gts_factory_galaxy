using System;
using System.Collections.Generic;
using System.Diagnostics;
using UnityEngine;
using UnityEngine.Rendering;
namespace Braemac.Factory {
 [Serializable] public class FullFrameMetadata {public string line_id,session_id,camera_id,frame_id,capture_utc;public int sequence,width=640,height=640;public double source_time;}
 public sealed class FullFramePacket {public FullFrameMetadata Metadata;public byte[] Pixels;public double RenderMs,ReadbackMs,EncodeMs;public string Error;}
 // RenderTextures are exclusively owned until GPU completion and copy. Never recycle a pending target.
 public sealed class FullFrameCapture:IDisposable {
  sealed class Slot {public RenderTexture Target;public Texture2D Encoder;public bool Busy;}
  readonly Slot[] slots=new Slot[4];readonly Dictionary<string,Camera> cameras=new Dictionary<string,Camera>();readonly Dictionary<string,int> sequences=new Dictionary<string,int>();
  bool disposed;public readonly bool AsyncSupported=SystemInfo.supportsAsyncGPUReadback;public float CameraCenterX=3,CameraCenterY=2.05f,CameraSize=1.35f;public Color CameraBackground=new Color(.24f,.29f,.32f);public int Busy {get{int n=0;foreach(var s in slots)if(s.Busy)n++;return n;}}
  public string Backend{get{return AsyncSupported?"Unity AsyncGPUReadback RGBA32":"Unavailable: renderer has no async GPU readback";}}
  public FullFrameCapture(){for(int i=0;i<4;i++){var rt=new RenderTexture(640,640,24,RenderTextureFormat.ARGB32){antiAliasing=1};rt.Create();slots[i]=new Slot{Target=rt,Encoder=new Texture2D(640,640,TextureFormat.RGBA32,false)};}}
  static int LineLayer(LineVisual line){int index=0;int.TryParse(line.State.Id.Substring(4),out index);return 9+Mathf.Clamp(index-1,0,2);}
  public Camera CameraFor(LineVisual line,int view){string key=line.State.Id+":"+view;Camera c;if(!cameras.TryGetValue(key,out c)){c=new GameObject("Full-frame neutral camera "+key).AddComponent<Camera>();c.enabled=false;c.orthographic=true;c.nearClipPlane=.05f;c.farClipPlane=8;c.clearFlags=CameraClearFlags.SolidColor;c.cullingMask=1<<LineLayer(line);cameras[key]=c;}
   float x=CameraCenterX+(view-1)*.60f;c.aspect=1f;c.orthographicSize=CameraSize;c.backgroundColor=CameraBackground;c.cullingMask=1<<LineLayer(line);
   c.transform.position=line.Origin+new Vector3(x,CameraCenterY,-3.0f);c.transform.LookAt(line.Origin+new Vector3(x,CameraCenterY,0));return c;
  }
  public bool Request(LineVisual line,int view,Action<FullFramePacket> done){if(disposed||!AsyncSupported)return false;Slot slot=null;foreach(var s in slots)if(!s.Busy){slot=s;break;}if(slot==null)return false;slot.Busy=true;var c=CameraFor(line,view);string key=line.State.Id+":"+line.State.Adapter.Session+":"+view;int sequence=sequences.ContainsKey(key)?sequences[key]+1:0;sequences[key]=sequence;
   var packet=new FullFramePacket{Metadata=new FullFrameMetadata{line_id=line.State.Id,session_id=line.State.Adapter.Session,camera_id="View"+(view+1),frame_id=Guid.NewGuid().ToString("N"),capture_utc=DateTime.UtcNow.ToString("o"),sequence=sequence,source_time=line.State.Sim.Time}};
   var sw=Stopwatch.StartNew();c.targetTexture=slot.Target;try{c.Render();packet.RenderMs=sw.Elapsed.TotalMilliseconds;}catch(Exception e){slot.Busy=false;packet.Error="camera-render: "+e.Message;done(packet);return true;}finally{c.targetTexture=null;}
   sw.Restart();var owned=slot;AsyncGPUReadback.Request(slot.Target,0,TextureFormat.RGBA32,request=>{packet.ReadbackMs=sw.Elapsed.TotalMilliseconds;try{if(request.hasError)packet.Error="async-readback-error";else{var rgba=request.GetData<byte>().ToArray();var encode=Stopwatch.StartNew();owned.Encoder.LoadRawTextureData(rgba);owned.Encoder.Apply(false,false);packet.Pixels=owned.Encoder.EncodeToPNG();packet.EncodeMs=encode.Elapsed.TotalMilliseconds;if(packet.Pixels==null||packet.Pixels.Length>2*1024*1024)packet.Error="encoded-frame-too-large";}}catch(Exception e){packet.Error="readback-copy-or-encode: "+e.Message;}finally{owned.Busy=false;if(disposed){owned.Target.Release();UnityEngine.Object.Destroy(owned.Target);UnityEngine.Object.Destroy(owned.Encoder);}}
    if(!disposed)done(packet);
   });return true;
  }
  public void Dispose(){disposed=true;foreach(var c in cameras.Values)if(c!=null)UnityEngine.Object.Destroy(c.gameObject);foreach(var slot in slots)if(!slot.Busy){slot.Target.Release();UnityEngine.Object.Destroy(slot.Target);UnityEngine.Object.Destroy(slot.Encoder);}cameras.Clear();}
 }
}
