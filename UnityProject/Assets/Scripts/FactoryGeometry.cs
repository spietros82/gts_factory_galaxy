using System;
using System.Collections.Generic;
using UnityEngine;
namespace Braemac.Factory {
 public sealed class MachinePick:MonoBehaviour {public string Asset;public Vector3 Focus;}
 public sealed class BottleVisual {public GameObject Root,Cap,Fluid;}
 public sealed class FactoryGeometry {
  public readonly Dictionary<int,BottleVisual> Products=new Dictionary<int,BottleVisual>();
  public readonly Dictionary<string,Transform> Moving=new Dictionary<string,Transform>();
  readonly Material steel,navy,cyan,rubber,yellow,glass,liquid,white,cardboard;
  readonly List<TextMesh> labels=new List<TextMesh>();
  readonly GameObject root;
  public GameObject Root {get{return root;}}
  public void SetRenderLayer(int layer){foreach(var t in root.GetComponentsInChildren<Transform>(true))t.gameObject.layer=layer;}
  public FactoryGeometry(){
   root=new GameObject("Braemac bottling line — procedural assets");
   steel=Mat("Brushed stainless",new Color(.5f,.58f,.66f),.82f,.72f);
   navy=Mat("GTS navy",new Color(.018f,.045f,.085f),.4f,.4f);
   cyan=Mat("Cyan status trim",new Color(.02f,.7f,.85f),.3f,.5f);
   rubber=Mat("Conveyor belt",new Color(.055f,.085f,.1f),.1f,.2f);
   yellow=Mat("Safety marking",new Color(.98f,.68f,.06f),.2f,.45f);
   glass=Mat("Synthetic PET",new Color(.25f,.64f,.68f),.15f,.85f);
   liquid=Mat("Product",new Color(.05f,.45f,.6f),.2f,.7f);
   white=Mat("White label",new Color(.83f,.93f,.96f),0,.3f);
   cardboard=Mat("Carton",new Color(.57f,.35f,.14f),0,.1f);
   Build();
  }
  static void Dispose(UnityEngine.Object value){if(Application.isPlaying)UnityEngine.Object.Destroy(value);else UnityEngine.Object.DestroyImmediate(value);}
  static Material Mat(string name,Color c,float metallic,float smooth){var m=new Material(Shader.Find("Standard"));m.name=name;m.color=c;m.SetFloat("_Metallic",metallic);m.SetFloat("_Glossiness",smooth);return m;}
  GameObject Shape(string name,PrimitiveType type,Vector3 p,Vector3 scale,Material mat,Transform parent=null){
   var o=GameObject.CreatePrimitive(type);o.name=name;o.layer=parent==null?root.layer:parent.gameObject.layer;o.transform.SetParent(parent==null?root.transform:parent,false);
   o.transform.localPosition=p;o.transform.localScale=scale;o.GetComponent<Renderer>().sharedMaterial=mat;
   Dispose(o.GetComponent<Collider>());return o;
  }
  GameObject Box(string name,Vector3 p,Vector3 size,Material m,Transform parent=null){return Shape(name,PrimitiveType.Cube,p,size,m,parent);}
  void Rod(string name,Vector3 from,Vector3 to,float radius,Material m,Transform parent=null){var o=Shape(name,PrimitiveType.Cylinder,(from+to)/2,new Vector3(radius,(to-from).magnitude/2,radius),m,parent);o.transform.up=(to-from).normalized;}
  void Text(string title,Vector3 p,int size=30){var obj=new GameObject(title);obj.transform.SetParent(root.transform);obj.transform.position=p;
   var t=obj.AddComponent<TextMesh>();t.text=title;t.anchor=TextAnchor.MiddleCenter;t.alignment=TextAlignment.Center;t.characterSize=.10f;t.fontSize=size;t.color=new Color(.77f,.92f,1);labels.Add(t);}
  void Selectable(string asset,Vector3 p,Vector3 size){var o=new GameObject(asset+" hit target");o.transform.SetParent(root.transform);o.transform.position=p;
   o.AddComponent<BoxCollider>().size=size;var pick=o.AddComponent<MachinePick>();pick.Asset=asset;pick.Focus=new Vector3(p.x,1,0);}
  void Conveyor(float x,float length,float z=0){
   Box("Belt",new Vector3(x,.93f,z),new Vector3(length,.14f,.9f),rubber);
   for(int side=-1;side<=1;side+=2){Box("Stainless guard rail",new Vector3(x,1.17f,z+side*.51f),new Vector3(length,.06f,.05f),steel);
    Box("Cyan rail fascia",new Vector3(x,.78f,z+side*.52f),new Vector3(length,.1f,.07f),cyan);}
   for(float pos=x-length/2+.3f;pos<x+length/2;pos+=1.3f){
    for(int side=-1;side<=1;side+=2)Rod("Adjustable conveyor leg",new Vector3(pos,.15f,z+side*.33f),new Vector3(pos,.86f,z+side*.33f),.06f,steel);
    var roller=Shape("Roller",PrimitiveType.Cylinder,new Vector3(pos,.93f,z),new Vector3(.16f,.45f,.16f),steel);roller.transform.rotation=Quaternion.Euler(90,0,0);
   }
  }
  void Frame(float x,float width){
   for(int side=-1;side<=1;side+=2){for(int end=-1;end<=1;end+=2)Box("Stainless post",new Vector3(x+end*width/2,1.55f,side*.85f),new Vector3(.12f,2.6f,.12f),steel);
    Box("Bridge",new Vector3(x,2.86f,side*.85f),new Vector3(width+.2f,.15f,.15f),steel);}
  }
  void Build(){
   Box("Factory floor",new Vector3(0,-.12f,0),new Vector3(40,.24f,25),Mat("Floor",new Color(.065f,.10f,.15f),.12f,.45f));
   for(int i=-16;i<=16;i+=2)Box("Floor expansion joint",new Vector3(i,.008f,0),new Vector3(.015f,.009f,22),rubber);
   for(int i=-10;i<=10;i+=2)Box("Floor expansion joint",new Vector3(0,.008f,i),new Vector3(36,.009f,.015f),rubber);
   for(int side=-1;side<=1;side+=2){Box("Walkway boundary",new Vector3(0,.018f,side*2.3f),new Vector3(29,.008f,.08f),yellow);
    for(int x=-14;x<=14;x+=2)Box("Walkway dash",new Vector3(x,.02f,side*3.8f),new Vector3(.75f,.01f,.07f),white);}
   Conveyor(0,27);Conveyor(4,3.4f,2.2f);
   Rod("Reject branch",new Vector3(3,.99f,.4f),new Vector3(4,.99f,2.2f),.12f,cyan);
   Text("01  INFEED",new Vector3(-11,3.8f,0));Text("02  MULTI-HEAD FILLER",new Vector3(-7,4.7f,0));
   Text("03  CAPPER",new Vector3(-2,4,0));Text("04  INSPECTION",new Vector3(3,3.9f,0));Text("05  PACK / OUTFEED",new Vector3(10,4,0));
   Text("FLOW  →",new Vector3(-11,1.8f,-1.8f));Text("FLOW  →",new Vector3(1,1.8f,-1.8f));Text("FINITE BUFFER",new Vector3(7,1.8f,-1.8f));
   Text("REJECT LANE",new Vector3(5,1.7f,3.4f));
   for(int i=0;i<5;i++)Box("Infeed magazine",new Vector3(-12+i*.3f,1.3f,1.3f),new Vector3(.22f,.6f,.45f),glass);
   Frame(-7,3.7f);Box("Filler lower housing",new Vector3(-7,.6f,0),new Vector3(3.5f,.9f,2),navy);
   Shape("Product tank",PrimitiveType.Cylinder,new Vector3(-7,3.4f,0),new Vector3(1.3f,.5f,1.3f),steel);
   Shape("Tank top dome",PrimitiveType.Sphere,new Vector3(-7,3.93f,0),new Vector3(1.3f,.45f,1.3f),steel);
   for(int h=0;h<4;h++){float x=-8.1f+h*.7f;
    var nozzle=Shape("Filling head "+(h+1),PrimitiveType.Cylinder,new Vector3(x,1.85f,0),new Vector3(.11f,.27f,.11f),steel);
    Moving["head"+h]=nozzle.transform;Rod("Feed pipe",new Vector3(x,2.6f,0),new Vector3(-7,3.2f,0),.08f,steel);}
   Box("Filler control cabinet",new Vector3(-8.7f,1.7f,-1.2f),new Vector3(.5f,1.1f,.4f),navy);
   Box("Filler HMI",new Vector3(-8.7f,1.9f,-1.43f),new Vector3(.34f,.35f,.04f),cyan);
   Frame(-2,2.1f);Box("Capper housing",new Vector3(-2,.6f,0),new Vector3(1.8f,.9f,1.6f),navy);
   var capper=Shape("Rotary capper turret",PrimitiveType.Cylinder,new Vector3(-2,2.25f,0),new Vector3(1.25f,.2f,1.25f),steel);Moving["capper"]=capper.transform;
   for(int i=0;i<6;i++){float a=i*Mathf.PI/3;Rod("Cap spindle",new Vector3(Mathf.Cos(a)*.48f,-.2f,Mathf.Sin(a)*.48f),new Vector3(Mathf.Cos(a)*.48f,-.6f,Mathf.Sin(a)*.48f),.08f,steel,capper.transform);}
   Shape("Cap hopper",PrimitiveType.Cylinder,new Vector3(-2,3.05f,1.1f),new Vector3(.9f,.3f,.9f),navy);
   Rod("Cap chute",new Vector3(-2,2.8f,1.1f),new Vector3(-2,2.1f,0),.13f,steel);
   Frame(3,1.8f);Box("Inspection light bar",new Vector3(3,2.75f,0),new Vector3(1.5f,.1f,1.5f),white);
   Box("Inspection camera housing",new Vector3(3,2.1f,-1),new Vector3(.5f,.4f,.45f),navy);
   var lens=Shape("Optical lens",PrimitiveType.Cylinder,new Vector3(3,2.1f,-.73f),new Vector3(.18f,.15f,.18f),cyan);lens.transform.rotation=Quaternion.Euler(90,0,0);
   Box("PLC / edge cabinet",new Vector3(4.6f,.85f,-1.6f),new Vector3(.7f,1.6f,.7f),navy);
   Text("PLC • CONTROL\nEDGE • OBSERVE / ADVISE",new Vector3(4.7f,2.15f,-2),24);
   Frame(10,3);Box("Packing base",new Vector3(10,.6f,0),new Vector3(2.6f,.9f,1.7f),navy);
   var pack=Box("Carton pusher",new Vector3(10,1.75f,0),new Vector3(1.5f,.2f,.25f),steel);Moving["packer"]=pack.transform;
   for(int i=0;i<3;i++){float x=11+i*1.2f;
    Box("Outfeed carton",new Vector3(x,1.17f,1.5f),new Vector3(.9f,.55f,.8f),cardboard);
    Box("Carton label",new Vector3(x,1.21f,1.09f),new Vector3(.55f,.18f,.01f),white);}

   Selectable("infeed",new Vector3(-11,1.6f,0),new Vector3(3,3,2));Selectable("filler",new Vector3(-7,2,0),new Vector3(4,4,2));
   Selectable("capper",new Vector3(-2,2,0),new Vector3(2.3f,3.3f,2));Selectable("inspection",new Vector3(3,1.8f,0),new Vector3(2,3,2));Selectable("packer",new Vector3(10,1.8f,0),new Vector3(3.2f,3,2));
  }
  static Mesh BottleMesh(){
   float[] heights={0,.03f,.06f,.44f,.54f,.61f,.69f,.73f};float[] radii={.12f,.16f,.17f,.17f,.16f,.10f,.07f,.07f};int n=20;
   var v=new List<Vector3>();var t=new List<int>();
   for(int j=0;j<heights.Length;j++)for(int i=0;i<n;i++){float a=i*2*Mathf.PI/n;v.Add(new Vector3(Mathf.Cos(a)*radii[j],heights[j],Mathf.Sin(a)*radii[j]));}
   for(int j=0;j<heights.Length-1;j++)for(int i=0;i<n;i++){int a=j*n+i,b=j*n+(i+1)%n,c=a+n,d=b+n;t.Add(a);t.Add(c);t.Add(b);t.Add(b);t.Add(c);t.Add(d);}
   var mesh=new Mesh();mesh.name="Lathed synthetic PET bottle";mesh.SetVertices(v);mesh.SetTriangles(t,0);mesh.RecalculateNormals();mesh.RecalculateBounds();return mesh;
  }
  Mesh bottleMesh;
  BottleVisual CreateBottle(int id){
   if(bottleMesh==null)bottleMesh=BottleMesh();
   var o=new GameObject("Bottle "+id);o.layer=root.layer;o.transform.SetParent(root.transform);
   o.AddComponent<MeshFilter>().sharedMesh=bottleMesh;o.AddComponent<MeshRenderer>().sharedMaterial=glass;
   Shape("Printed sleeve",PrimitiveType.Cylinder,new Vector3(0,.28f,0),new Vector3(.344f,.095f,.344f),white,o.transform);
   var fluid=Shape("Fill-level marker",PrimitiveType.Cylinder,new Vector3(0,.51f,0),new Vector3(.315f,.018f,.315f),liquid,o.transform);
   var cap=Shape("Cap",PrimitiveType.Cylinder,new Vector3(0,.76f,0),new Vector3(.18f,.04f,.18f),cyan,o.transform);
   return new BottleVisual{Root=o,Cap=cap,Fluid=fluid};
  }
  public void Update(LineSimulation sim,float alpha,Camera camera,PlcMapping telemetry=null,double wall=0){
   var alive=new HashSet<int>();
   foreach(var b in sim.Bottles){alive.Add(b.Id);if(!Products.ContainsKey(b.Id))Products[b.Id]=CreateBottle(b.Id);
    var v=Products[b.Id];float x=Mathf.Lerp(b.PreviousX,b.X,alpha);float z=b.Rejected?Mathf.Min(2.3f,b.RejectTravel):0;
    v.Root.transform.position=new Vector3(x,1.01f,z);v.Cap.SetActive(b.Stage>=4&&b.CapPresent);
    v.Cap.transform.localPosition=new Vector3(b.CapDisplaced?.075f:0,.76f,0);v.Cap.transform.localRotation=Quaternion.Euler(0,0,b.CapDisplaced?18:0);
    v.Fluid.SetActive(b.Stage>=2);v.Fluid.transform.localPosition=new Vector3(0,.51f*(b.Fill/500f),0);
   }
   foreach(var id in new List<int>(Products.Keys))if(!alive.Contains(id)){Dispose(Products[id].Root);Products.Remove(id);}
   if(telemetry==null){
    for(int h=0;h<4;h++){float stroke=0;foreach(var b in sim.Bottles)if(b.Stage==1&&b.Head==h)stroke=Mathf.Sin(Mathf.PI*b.Dwell/.7f);Moving["head"+h].localPosition=new Vector3(-8.1f+h*.7f,1.95f-stroke*.12f,0);}
    Moving["capper"].localRotation=Quaternion.Euler(0,sim.CapperRotation,0);
    Moving["packer"].localPosition=new Vector3(10,1.75f,Mathf.Sin(Mathf.PI*Mathf.Clamp01((float)(sim.Time-sim.LastPackedTime)/.45f))*.4f);
   }else{
    float v;
    for(int h=0;h<4;h++)if(telemetry.Number("Line01.Filler.Head"+(h+1)+".PositionY",wall,out v))Moving["head"+h].localPosition=new Vector3(-8.1f+h*.7f,v,0);
    if(telemetry.Number("Line01.Capper.Angle",wall,out v))Moving["capper"].localRotation=Quaternion.Euler(0,v,0);
    if(telemetry.Number("Line01.Packer.PusherZ",wall,out v))Moving["packer"].localPosition=new Vector3(10,1.75f,v);
   }
   foreach(var text in labels){text.transform.rotation=Quaternion.LookRotation(text.transform.position-camera.transform.position);}
  }
 }
}
