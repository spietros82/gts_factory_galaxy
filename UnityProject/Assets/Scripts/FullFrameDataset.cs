using System;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
namespace Braemac.Factory {
 [Serializable] public class FullDatasetPlan { public FullDatasetCase[] items; }
 [Serializable] public class FullDatasetCase { public string id,split,sequence_id,product,appearance; public int seed,frames,view; public float camera_x,camera_y,camera_size,light_scale,bg_r,bg_g,bg_b; }
 [Serializable] public class FullDatasetBox { public int simulator_bottle_id,class_id=39; public float[] xyxy; public bool partial_view; }
 [Serializable] public class FullDatasetLabel { public string image_id,sequence_id,split,product_for_evaluator,capture_utc; public FullDatasetBox[] boxes; }
 public sealed partial class MultiLineFactory {
  string evaluatorMaskDebugPath="";
  FullDatasetBox[] ProjectDatasetBoxes(LineVisual line,Camera camera) {
   // Evaluator-only visible-pixel masks. The detector never receives these colors,
   // labels, IDs, or this second render. Replacing bottle materials for one render
   // preserves normal depth occlusion by the line machinery and other bottles.
   var ids=new Dictionary<int,Color32>();var restore=new List<KeyValuePair<Renderer,Material[]>>();var debugMaterials=new List<Material>();
   var target=new RenderTexture(640,640,24,RenderTextureFormat.ARGB32){antiAliasing=1};target.Create();var pixelsTexture=new Texture2D(640,640,TextureFormat.RGBA32,false);
   var priorTarget=camera.targetTexture;var priorActive=RenderTexture.active;
   try {
    var baseMaterial=Resources.Load<Material>("Stage5IdMask");if(baseMaterial==null)throw new InvalidOperationException("Stage5 evaluator mask material was not included in build");
    int code=1;
    foreach(var b in line.State.Sim.Bottles){if(b.Rejected)continue;var visual=line.Brewery.BottleById(b.Id);if(visual==null)continue;
     var color=new Color32((byte)(32+(code%96)*2),(byte)(180+(code/96)*2),240,255);ids[b.Id]=color;var mat=new Material(baseMaterial){name="Evaluator-only bottle mask"};mat.SetColor("_Color",color);debugMaterials.Add(mat);code++;
     foreach(var renderer in visual.Root.GetComponentsInChildren<Renderer>(true))if(renderer.enabled&&renderer.gameObject.activeInHierarchy){restore.Add(new KeyValuePair<Renderer,Material[]>(renderer,renderer.sharedMaterials));var replacements=renderer.sharedMaterials;for(int i=0;i<replacements.Length;i++)replacements[i]=mat;renderer.sharedMaterials=replacements;}
    }
    camera.targetTexture=target;camera.aspect=1f;camera.Render();RenderTexture.active=target;pixelsTexture.ReadPixels(new Rect(0,0,640,640),0,0,false);pixelsTexture.Apply(false,false);
   } finally {
    RenderTexture.active=priorActive;camera.targetTexture=priorTarget;
    foreach(var entry in restore)if(entry.Key!=null)entry.Key.sharedMaterials=entry.Value;
   }
   if(evaluatorMaskDebugPath!="")File.WriteAllBytes(evaluatorMaskDebugPath,pixelsTexture.EncodeToPNG());var redIds=new Dictionary<int,int>();foreach(var pair in ids)redIds[pair.Value.r]=pair.Key;var source=pixelsTexture.GetPixels32();var minsX=new Dictionary<int,int>();var minsY=new Dictionary<int,int>();var maxsX=new Dictionary<int,int>();var maxsY=new Dictionary<int,int>();var counts=new Dictionary<int,int>();
   for(int i=0;i<source.Length;i++){var p=source[i];int id;if(!redIds.TryGetValue(p.r,out id)||Mathf.Abs(p.g-180)>2||Mathf.Abs(p.b-240)>2)continue;int x=i%640,y=639-i/640;if(!minsX.ContainsKey(id)){minsX[id]=maxsX[id]=x;minsY[id]=maxsY[id]=y;}else{minsX[id]=Math.Min(minsX[id],x);maxsX[id]=Math.Max(maxsX[id],x);minsY[id]=Math.Min(minsY[id],y);maxsY[id]=Math.Max(maxsY[id],y);}counts[id]=counts.ContainsKey(id)?counts[id]+1:1;}
   var result=new List<FullDatasetBox>();foreach(var pair in counts){if(pair.Value<24)continue;int id=pair.Key;int x0=minsX[id],y0=minsY[id],x1=maxsX[id]+1,y1=maxsY[id]+1;result.Add(new FullDatasetBox{simulator_bottle_id=id,xyxy=new[]{(float)x0,(float)y0,(float)x1,(float)y1},partial_view=x0==0||y0==0||x1>=639||y1>=639});}
   pixelsTexture.Apply(false,false);UnityEngine.Object.Destroy(pixelsTexture);target.Release();UnityEngine.Object.Destroy(target);foreach(var m in debugMaterials)UnityEngine.Object.Destroy(m);return result.ToArray();
  }
  IEnumerator FullDataset(string planPath){
   if(!fullFrame.AsyncSupported)throw new InvalidOperationException("Unity reports asynchronous GPU readback unavailable; dataset capture cancelled");
   var plan=JsonUtility.FromJson<FullDatasetPlan>(File.ReadAllText(planPath));if(plan==null||plan.items==null||plan.items.Length==0)throw new InvalidDataException("Dataset plan has no cases");
   int total=0;foreach(var item in plan.items){if(item.frames<1||item.frames>100)throw new InvalidDataException("Per-sequence frame bound exceeded");total+=item.frames;}if(total>5000)throw new InvalidDataException("Stage5 dataset exceeds 5,000-frame bound");
   string root=Arg("--dataset-output",Path.Combine(dataPath,"dataset"));if(Directory.Exists(root)&&Directory.GetFiles(root,"*",SearchOption.AllDirectories).Length>0)throw new IOException("Refusing to overwrite existing dataset output");Directory.CreateDirectory(root);evaluatorMaskDebugPath=Arg("--dataset-mask-debug","");File.WriteAllText(Path.Combine(root,"capture-start.json"),JsonUtility.ToJson(new FullDatasetPlan{items=plan.items}));
   var started=Wall;string trace=Path.Combine(root,"capture-events.jsonl");int saved=0,failed=0;paused=false;
   for(int ci=0;ci<plan.items.Length;ci++){
    var item=plan.items[ci];if(item.split!="development"&&item.split!="locked-test")throw new InvalidDataException("Unknown frozen split");
    if(visuals.Count!=1)Resize(1);visuals[0].Dispose();Clock=new MultiLineClock(item.seed);Clock.Resize(1);visuals[0]=Create(Clock.Lines[0]);visuals[0].Origin=Vector3.zero;visuals[0].Geometry.Root.transform.position=Vector3.zero;visuals[0].Brewery.Root.transform.position=Vector3.zero;capture.Position(visuals[0]);ApplyStage5Layers();visuals[0].Brewery.SetProduct(item.product);Clock.Heartbeat(Wall,false);paused=false;fullGeneration++;
    fullFrame.CameraCenterX=item.camera_x;fullFrame.CameraCenterY=item.camera_y;fullFrame.CameraSize=item.camera_size;fullFrame.CameraBackground=new Color(item.bg_r,item.bg_g,item.bg_b);
    foreach(var light in FindObjectsOfType<Light>(true))if(light.name=="Presentation industrial key")light.intensity=1.05f*item.light_scale;else if(light.name=="Presentation cool skylight")light.intensity=.48f*item.light_scale;
    GameObject occluder=null;if(item.appearance=="partial-occlusion"){occluder=GameObject.CreatePrimitive(PrimitiveType.Cube);occluder.name="Evaluator-only neutral partial occluder";occluder.layer=9;Destroy(occluder.GetComponent<Collider>());occluder.transform.position=new Vector3(item.camera_x,1.50f,-1.30f);occluder.transform.localScale=new Vector3(.27f,.75f,.06f);occluder.GetComponent<Renderer>().sharedMaterial=new Material(Shader.Find("Standard")){color=new Color(.15f,.17f,.18f)};}
    string seq=Path.Combine(root,item.split,item.sequence_id);Directory.CreateDirectory(seq);int done=0,seqFailed=0;double due=Wall;var gate=new object();FullFramePacket resultPacket=null;FullDatasetBox[] resultBoxes=null;string resultImageId="";int resultIndex=0;
    while(done<item.frames&&Wall-started<900){yield return new WaitForEndOfFrame();if(resultPacket!=null){FullFramePacket packet;FullDatasetBox[] boxes;string imageId;int index;lock(gate){packet=resultPacket;boxes=resultBoxes;imageId=resultImageId;index=resultIndex;resultPacket=null;}
      if(packet.Error==null&&packet.Pixels!=null){string stem=String.Format("{0}_{1:D2}",imageId,index);File.WriteAllBytes(Path.Combine(seq,stem+".png"),packet.Pixels);var label=new FullDatasetLabel{image_id=stem,sequence_id=item.sequence_id,split=item.split,product_for_evaluator=item.product,capture_utc=packet.Metadata.capture_utc,boxes=boxes};File.WriteAllText(Path.Combine(seq,stem+".json"),JsonUtility.ToJson(label));saved++;done++;File.AppendAllText(trace,"{\"event\":\"saved\",\"sequence\":\""+item.sequence_id+"\",\"frame\":\""+stem+"\",\"boxes\":"+boxes.Length+"}\n");}
      else{failed++;seqFailed++;File.AppendAllText(trace,"{\"event\":\"failed\",\"sequence\":\""+item.sequence_id+"\",\"reason\":\""+(packet.Error??"missing pixels")+"\"}\n");}
     }
     if(done+seqFailed>=item.frames||Wall<due)continue;due=Wall+.20;int frameIndex=done+seqFailed;int view=Mathf.Clamp(item.view,0,2);Camera camera=fullFrame.CameraFor(visuals[0],view);var boxesAtCapture=ProjectDatasetBoxes(visuals[0],camera);string imageIdValue=item.sequence_id;
     bool requested=fullFrame.Request(visuals[0],view,packet=>{lock(gate){resultPacket=packet;resultBoxes=boxesAtCapture;resultImageId=imageIdValue;resultIndex=frameIndex;}});
     if(!requested){seqFailed++;failed++;File.AppendAllText(trace,"{\"event\":\"dropped\",\"sequence\":\""+item.sequence_id+"\",\"reason\":\"readback-ring-full-or-unavailable\"}\n");}
    }
    if(occluder!=null)Destroy(occluder);paused=true;yield return new WaitForEndOfFrame();
   }
   File.WriteAllText(Path.Combine(root,"capture-summary.json"),"{\"planned\":"+total+",\"saved\":"+saved+",\"failed\":"+failed+",\"wall_seconds\":"+(Wall-started).ToString("F3",System.Globalization.CultureInfo.InvariantCulture)+"}");Debug.Log("STAGE5_DATASET_CAPTURE saved="+saved+" failed="+failed);Application.Quit();
  }
 }
}
