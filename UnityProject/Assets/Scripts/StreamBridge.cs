using System;
using System.IO;
using System.Collections;
using System.Text;
using UnityEngine;
namespace Braemac.Factory {
 // Opt-in capture of this Unity framebuffer only. No X11/desktop capture or input.
 public sealed class StreamBridge:MonoBehaviour {
  [Serializable]public sealed class Command {public string id,action,value;public long expires_ms;}
  [Serializable]public sealed class Ack {public string id,result,selected;public long applied_ms;public bool paused;public int profile;}
  [Serializable]public sealed class State {public long sequence,utc_ms;public int width,height,target_fps,profile;public double capture_ms;public bool paused;public string selected;}
  string folder,lastId="";Texture2D frame;FactoryApp app;long sequence;int fps;double nextCapture;
  long Now(){return DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();}
  void Start(){app=GetComponent<FactoryApp>();folder=FactoryApp.Argument("--stream-path");fps=Mathf.Clamp(int.Parse(FactoryApp.Argument("--stream-fps","30")),1,60);Directory.CreateDirectory(folder);StartCoroutine(Capture());}
  void Replace(string from,string to){if(File.Exists(to))File.Replace(from,to,null);else File.Move(from,to);}
  void Write(string name,string text){string tmp=Path.Combine(folder,name+".tmp");File.WriteAllText(tmp,text);Replace(tmp,Path.Combine(folder,name));}
  void Update(){
   string path=Path.Combine(folder,"command.json");
   if(!File.Exists(path))return;
   try{var c=JsonUtility.FromJson<Command>(File.ReadAllText(path));if(c==null||c.id==lastId||string.IsNullOrEmpty(c.id))return;
    lastId=c.id;string result=c.expires_ms<Now()?"rejected: expired":app.RemoteAction(c.action,c.value);
    Write("ack.json",JsonUtility.ToJson(new Ack{id=c.id,result=result,selected=app.Selected,paused=app.Paused,profile=app.Profile,applied_ms=Now()}));
   }catch(Exception e){Debug.LogWarning("Stream command unavailable: "+e.GetType().Name);}
  }
  IEnumerator Capture(){
   while(true){yield return new WaitForEndOfFrame();
    string lease=Path.Combine(folder,"capture.lease");
    if(!File.Exists(lease)||(DateTime.UtcNow-File.GetLastWriteTimeUtc(lease)).TotalSeconds>3||Time.realtimeSinceStartupAsDouble<nextCapture)continue;
    nextCapture=Math.Max(nextCapture+1.0/fps,Time.realtimeSinceStartupAsDouble);var watch=System.Diagnostics.Stopwatch.StartNew();
    if(frame==null||frame.width!=Screen.width||frame.height!=Screen.height){if(frame!=null)Destroy(frame);frame=new Texture2D(Screen.width,Screen.height,TextureFormat.RGB24,false);}
    frame.ReadPixels(new Rect(0,0,Screen.width,Screen.height),0,0,false);var pixels=frame.GetRawTextureData();long ms=Now();sequence++;
    string tmp=Path.Combine(folder,"frame.tmp");
    using(var file=new BinaryWriter(File.Open(tmp,FileMode.Create,FileAccess.Write,FileShare.Read))){
     file.Write(Encoding.ASCII.GetBytes("GTSFRM01"));file.Write(sequence);file.Write(ms);file.Write(Screen.width);file.Write(Screen.height);file.Write(watch.Elapsed.TotalMilliseconds);file.Write(new byte[24]);file.Write(pixels);
    }
    Replace(tmp,Path.Combine(folder,"frame.rgb"));watch.Stop();
    Write("state.json",JsonUtility.ToJson(new State{sequence=sequence,utc_ms=ms,width=Screen.width,height=Screen.height,target_fps=fps,capture_ms=watch.Elapsed.TotalMilliseconds,paused=app.Paused,profile=app.Profile,selected=app.Selected}));
   }
  }
 }
}
