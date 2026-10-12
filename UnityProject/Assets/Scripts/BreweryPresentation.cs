using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;
namespace Braemac.Factory {
 // Presentation-only layer. Legacy geometry remains the sole inspection scene.
 public sealed class BreweryPresentation {
  public const int LegacyLayer=8,PresentationLayer=9;
  public string Product {get;private set;}="LAGER";
  public readonly GameObject Root;
  readonly FactoryGeometry original;
  readonly Dictionary<int,BottleVisual> bottles=new Dictionary<int,BottleVisual>();
  readonly Dictionary<string,Transform> machinery=new Dictionary<string,Transform>();
  readonly List<Transform> billboards=new List<Transform>();
  readonly List<TextMesh> productSigns=new List<TextMesh>();
  readonly Material steel,trim,glass,liquid,sleeve,cap,cream,ink,black;
  Mesh bottleMesh;Texture2D lagerLabel,ipaLabel,stoutLabel;
  public int VisibleBottles{get{return bottles.Count;}}
  public BreweryPresentation(FactoryGeometry source){
   original=source;Root=new GameObject("Stage 1 brewery presentation");Root.layer=PresentationLayer;
   steel=Material("Procedural brushed stainless steel",new Color(.65f,.68f,.7f),.78f,.48f,Texture("steel",128,64));
   trim=Material("Restrained powder coated navy",new Color(.025f,.065f,.085f),.25f,.33f);
   black=Material("Industrial matte black",new Color(.035f,.042f,.04f),0,.2f);
   cream=Material("Warm white paint",new Color(.88f,.87f,.79f),.05f,.25f);
   ink=Material("Demo product accent",new Color(.9f,.59f,.14f),.2f,.32f);
   glass=Material("Amber glass presentation only",new Color(.39f,.18f,.055f,.27f),.06f,.79f);
   glass.SetFloat("_Mode",3);glass.SetInt("_SrcBlend",(int)BlendMode.SrcAlpha);glass.SetInt("_DstBlend",(int)BlendMode.OneMinusSrcAlpha);glass.SetInt("_ZWrite",0);glass.EnableKeyword("_ALPHAPREMULTIPLY_ON");glass.renderQueue=3000;
   liquid=Material("Visible synthetic beer",new Color(.73f,.36f,.06f),0,.58f);
   sleeve=Material("Fictional Braemac beer label",Color.white,0,.15f);cap=Material("Demo crown cap",new Color(.88f,.63f,.15f),.65f,.42f);
   // Clone only static geometry at construction, before the original bottles exist.
   var clone=UnityEngine.Object.Instantiate(source.Root,Root.transform);clone.name="Presentation machinery";
   foreach(var t in clone.GetComponentsInChildren<Transform>(true))t.gameObject.layer=PresentationLayer;
   foreach(var c in clone.GetComponentsInChildren<Collider>(true))Dispose(c);
   foreach(var label in clone.GetComponentsInChildren<TextMesh>(true))Dispose(label.gameObject);
   var floor=Material("Seeded industrial epoxy floor",new Color(.24f,.29f,.3f),.02f,.22f,Texture("floor",128,128));floor.mainTextureScale=new Vector2(24,16);
   var belt=Material("Textured conveyor polymer belt",new Color(.105f,.135f,.13f),0,.18f,Texture("belt",128,128));belt.mainTextureScale=new Vector2(8,1);
   var carton=Material("Corrugated carton",new Color(.65f,.44f,.24f),0,.1f,Texture("carton",64,64));
   foreach(var r in clone.GetComponentsInChildren<Renderer>()){
    if(r.GetComponent<TextMesh>()!=null)continue;
    string n=r.sharedMaterial.name;
    if(n=="Brushed stainless")r.sharedMaterial=steel;
    else if(n=="Floor")r.sharedMaterial=floor;
    else if(n=="Conveyor belt")r.sharedMaterial=belt;
    else if(n=="GTS navy")r.sharedMaterial=trim;
    else if(n=="Cyan status trim")r.sharedMaterial=MaterialCachedCyan();
    else if(n=="Synthetic PET")r.sharedMaterial=glass;
    else if(n=="Carton")r.sharedMaterial=carton;
    else if(n=="White label")r.sharedMaterial=cream;
   }
   foreach(var t in clone.GetComponentsInChildren<Transform>()){
    if(t.name=="Rotary capper turret")machinery["capper"]=t;
    if(t.name=="Carton pusher")machinery["packer"]=t;
    for(int h=0;h<4;h++)if(t.name=="Filling head "+(h+1))machinery["head"+h]=t;
   }
   AddDetails();lagerLabel=LabelTexture("LAGER",new Color(.8f,.46f,.065f));ipaLabel=LabelTexture("IPA",new Color(.13f,.48f,.34f));stoutLabel=LabelTexture("STOUT",new Color(.28f,.15f,.36f));
   SetProduct("LAGER");
  }
  static void Dispose(UnityEngine.Object value){if(Application.isPlaying)UnityEngine.Object.Destroy(value);else UnityEngine.Object.DestroyImmediate(value);}
  Material cyan;
  Material MaterialCachedCyan(){if(cyan==null)cyan=Material("Muted GTS cyan trim",new Color(.045f,.37f,.42f),.2f,.38f);return cyan;}
  static Material Material(string name,Color color,float metallic,float smooth,Texture2D texture=null){var m=new Material(Shader.Find("Standard")){name=name,color=color};m.SetFloat("_Metallic",metallic);m.SetFloat("_Glossiness",smooth);if(texture!=null)m.mainTexture=texture;return m;}
  // Tiny reusable textures, generated locally with fixed mathematical patterns.
  static Texture2D Texture(string kind,int w,int h){var tex=new Texture2D(w,h,TextureFormat.RGB24,true){name="Braemac procedural "+kind,wrapMode=TextureWrapMode.Repeat};
   var random=new System.Random(1742);for(int y=0;y<h;y++)for(int x=0;x<w;x++){
    float noise=(float)random.NextDouble();float v=.84f+noise*.16f;
    if(kind=="steel")v=.92f+.035f*Mathf.Sin(y*1.9f)+noise*.03f;
    if(kind=="belt")v=(y%16<2||x%32<1)?.58f:.87f+noise*.08f;
    if(kind=="carton")v=.82f+(y%4)*.025f+noise*.07f;
    tex.SetPixel(x,y,new Color(v,v,v));
   }tex.Apply();return tex;}
  GameObject Shape(string name,PrimitiveType type,Vector3 pos,Vector3 size,Material mat,Transform parent=null){var o=GameObject.CreatePrimitive(type);o.name=name;o.layer=PresentationLayer;o.transform.SetParent(parent==null?Root.transform:parent,false);o.transform.localPosition=pos;o.transform.localScale=size;o.GetComponent<Renderer>().sharedMaterial=mat;Dispose(o.GetComponent<Collider>());return o;}
  GameObject Box(string n,Vector3 p,Vector3 s,Material m,Transform parent=null){return Shape(n,PrimitiveType.Cube,p,s,m,parent);}
  void Rod(string n,Vector3 a,Vector3 b,float diameter,Material m){var o=Shape(n,PrimitiveType.Cylinder,(a+b)/2,new Vector3(diameter,(b-a).magnitude/2,diameter),m);o.transform.up=(b-a).normalized;}
  TextMesh Text(string name,string value,Transform parent,Vector3 p,float size,Color color){var o=new GameObject(name);o.layer=PresentationLayer;o.transform.SetParent(parent,false);o.transform.localPosition=p;var t=o.AddComponent<TextMesh>();t.text=value;t.anchor=TextAnchor.MiddleCenter;t.alignment=TextAlignment.Center;t.characterSize=size;t.fontSize=64;t.color=color;t.GetComponent<Renderer>().shadowCastingMode=ShadowCastingMode.Off;return t;}
  static void Fit(TextMesh t,float width){if(t.font==null)return;t.font.RequestCharactersInTexture(t.text,t.fontSize,FontStyle.Normal);int advance=0;foreach(char c in t.text){CharacterInfo info;if(t.font.GetCharacterInfo(c,out info,t.fontSize,FontStyle.Normal))advance+=info.advance;}if(advance>0)t.characterSize=Mathf.Min(t.characterSize,width*10/advance);}
  void Sign(string number,string station,string operation,Vector3 pos,float width=3.7f){
   var board=new GameObject(station+" readable station sign");board.layer=PresentationLayer;board.transform.SetParent(Root.transform);board.transform.position=pos;billboards.Add(board.transform);
   Box("Sign face",Vector3.zero,new Vector3(width,1.12f,.04f),trim,board.transform);
   Box("Sign accent",new Vector3(-width/2+.05f,0,-.04f),new Vector3(.07f,1.04f,.035f),MaterialCachedCyan(),board.transform);
   Fit(Text("Station title",number+"   "+station,board.transform,new Vector3(0,.19f,-.055f),.058f,Color.white),width-.28f);
   Fit(Text("Operation",operation,board.transform,new Vector3(0,-.24f,-.055f),.035f,new Color(.71f,.89f,.88f)),width-.3f);
  }
  void AddDetails(){
   Sign("01","INFEED","EMPTY BOTTLES",new Vector3(-11,3.5f,.8f),3.5f);
   Sign("02","FILLER","FOUR HEADS • 500 mL DEMO",new Vector3(-7,5.12f,.8f),4.2f);
   Sign("03","CAPPER","CAP APPLICATION",new Vector3(-2,4.15f,.8f),3.3f);
   Sign("04","INSPECTION","VISUAL CAP CHECK",new Vector3(3,3.95f,.8f),3.5f);
   Sign("05","PACK / OUTFEED","CARTONS → DISPATCH",new Vector3(10,4.05f,.8f),4.3f);
   Sign("↗","REJECT LANE","SIMULATOR ONLY",new Vector3(5.9f,1.8f,3.4f),3.1f);
   var brand=new GameObject("Fictional brewery product sign");brand.layer=PresentationLayer;brand.transform.SetParent(Root.transform);brand.transform.position=new Vector3(-10.6f,1.7f,-2.1f);billboards.Add(brand.transform);
   Box("Product placard",Vector3.zero,new Vector3(3.8f,.98f,.04f),trim,brand.transform);
   Fit(Text("Brand","BRAEMAC DEMO BREWERY",brand.transform,new Vector3(0,.22f,-.035f),.039f,Color.white),3.5f);
   productSigns.Add(Text("Selected product","",brand.transform,new Vector3(0,-.2f,-.035f),.07f,new Color(.98f,.8f,.38f)));
   // Brewery utilities and visible connections; decorative, not another production line.
   for(int k=0;k<2;k++){float x=-8.9f+k*2.1f;
    Shape("Brewery holding vessel",PrimitiveType.Cylinder,new Vector3(x,1.75f,3.7f),new Vector3(1.45f,1.15f,1.45f),steel);
    Shape("Dished tank top",PrimitiveType.Sphere,new Vector3(x,2.96f,3.7f),new Vector3(1.43f,.34f,1.43f),steel);
    for(int i=0;i<3;i++){float a=i*Mathf.PI*2/3;Rod("Tank foot",new Vector3(x+Mathf.Cos(a)*.52f,.12f,3.7f+Mathf.Sin(a)*.52f),new Vector3(x+Mathf.Cos(a)*.52f,.65f,3.7f+Mathf.Sin(a)*.52f),.09f,steel);}
    Rod("Sanitary feed pipe",new Vector3(x,2,3),new Vector3(-7,2.7f,1),.095f,steel);
    var gauge=Shape("Local gauge face",PrimitiveType.Cylinder,new Vector3(x,2.1f,2.94f),new Vector3(.22f,.035f,.22f),cream);gauge.transform.rotation=Quaternion.Euler(90,0,0);
   }
   // Rails, feet, cross braces, valves, guarded station boundaries.
   for(float x=-12.5f;x<13;x+=1.3f)for(int side=-1;side<=1;side+=2){Box("Adjustable foot pad",new Vector3(x,.07f,side*.33f),new Vector3(.25f,.08f,.23f),black);Rod("Rail standoff",new Vector3(x,.85f,side*.51f),new Vector3(x,1.19f,side*.51f),.04f,steel);}
   for(int h=0;h<4;h++){float x=-8.1f+h*.7f;Shape("Feed manifold clamp",PrimitiveType.Cylinder,new Vector3(x,2.58f,0),new Vector3(.15f,.08f,.15f),black);Box("Head accent",new Vector3(x,2.73f,0),new Vector3(.2f,.05f,.18f),ink);}
   for(int k=0;k<5;k++){float x=-10+k*5;FloorArrow(new Vector3(x,.025f,-1.7f));}
   for(float x=-13.5f;x<14;x+=.9f){var mark=Box("Restricted lane hatch",new Vector3(x,.025f,2.33f),new Vector3(.045f,.01f,.28f),cream);mark.transform.rotation=Quaternion.Euler(0,-40,0);}
   for(int i=0;i<3;i++){float x=11+i*1.2f;Box("Carton seam",new Vector3(x,1.455f,1.5f),new Vector3(.06f,.012f,.82f),cream);var t=Text("Fictional carton label","BRAEMAC",Root.transform,new Vector3(x,1.22f,1.075f),.031f,new Color(.04f,.09f,.1f));productSigns.Add(t);}
   // Fixture forms stay outside the inspection layer; no extra camera or inference.
   for(int i=0;i<4;i++){float x=-10+i*6.5f;Box("Industrial luminaire",new Vector3(x,6.4f,2.5f),new Vector3(2.8f,.08f,.28f),steel);Box("Diffuser",new Vector3(x,6.34f,2.5f),new Vector3(2.65f,.035f,.23f),cream);}
  }
  void FloorArrow(Vector3 p){Box("Flow shaft",p,new Vector3(.65f,.015f,.10f),cream);for(int s=-1;s<=1;s+=2){var arm=Box("Flow arrowhead",p+new Vector3(.33f,0,s*.11f),new Vector3(.32f,.015f,.08f),cream);arm.transform.rotation=Quaternion.Euler(0,s*45,0);}}
  static readonly Dictionary<char,string> Font=new Dictionary<char,string>{
   {'A',"01110100011000111111100011000110001"},{'B',"11110100011000111110100011000111110"},{'C',"01111100001000010000100001000001111"},{'D',"11110100011000110001100011000111110"},{'E',"11111100001000011110100001000011111"},{'G',"01111100001000010111100011000101111"},{'I',"11111001000010000100001000010011111"},{'L',"10000100001000010000100001000011111"},{'M',"10001110111010110101100011000110001"},{'O',"01110100011000110001100011000101110"},{'P',"11110100011000111110100001000010000"},{'R',"11110100011000111110101001001010001"},{'S',"01111100001000001110000010000111110"},{'T',"11111001000010000100001000010000100"},{'U',"10001100011000110001100011000101110"}};
  static void PixelsText(Texture2D texture,string text,int y,int scale,Color color){int start=(texture.width-text.Length*6*scale)/2;for(int k=0;k<text.Length;k++){if(!Font.ContainsKey(text[k]))continue;string glyph=Font[text[k]];for(int j=0;j<7;j++)for(int i=0;i<5;i++)if(glyph[j*5+i]=='1')for(int yy=0;yy<scale;yy++)for(int xx=0;xx<scale;xx++)texture.SetPixel(start+(k*6+i)*scale+xx,y+(6-j)*scale+yy,color);}}
  static Texture2D LabelTexture(string product,Color accent){var t=new Texture2D(256,128,TextureFormat.RGB24,true){name="Original fictional Braemac "+product+" label",wrapMode=TextureWrapMode.Repeat};for(int y=0;y<128;y++)for(int x=0;x<256;x++)t.SetPixel(x,y,y<9||y>119?accent:new Color(.92f,.88f,.74f));PixelsText(t,"BRAEMAC",89,3,new Color(.055f,.08f,.07f));PixelsText(t,product,39,5,accent);PixelsText(t,"DEMO",14,2,new Color(.13f,.15f,.13f));t.Apply();return t;}
  public bool SetProduct(string name){name=(name??"").ToUpperInvariant();if(name!="LAGER"&&name!="IPA"&&name!="STOUT")return false;Product=name;
   Color accent=name=="LAGER"?new Color(.8f,.46f,.065f):name=="IPA"?new Color(.13f,.48f,.34f):new Color(.28f,.15f,.36f);
   liquid.color=name=="LAGER"?new Color(.78f,.43f,.08f):name=="IPA"?new Color(.55f,.27f,.055f):new Color(.07f,.027f,.014f);
   sleeve.mainTexture=name=="LAGER"?lagerLabel:name=="IPA"?ipaLabel:stoutLabel;cap.color=accent;ink.color=accent;
   foreach(var t in productSigns){t.characterSize=t.name=="Selected product"?.07f:.013f;t.text=t.name=="Selected product"?name+" • DEMO BEER": "BRAEMAC / "+name;Fit(t,t.name=="Selected product"?3.45f:.52f);}
   return true;
  }
  static Mesh GlassMesh(){float[] heights={0,.035f,.055f,.44f,.52f,.59f,.66f,.73f};float[] radii={.12f,.16f,.17f,.17f,.15f,.08f,.068f,.068f};int n=24;var vertices=new List<Vector3>();var uv=new List<Vector2>();var triangles=new List<int>();for(int j=0;j<heights.Length;j++)for(int i=0;i<=n;i++){float a=i*2*Mathf.PI/n;vertices.Add(new Vector3(Mathf.Cos(a)*radii[j],heights[j],Mathf.Sin(a)*radii[j]));uv.Add(new Vector2((float)i/n,(heights[j]/.73f)));}for(int j=0;j<heights.Length-1;j++)for(int i=0;i<n;i++){int a=j*(n+1)+i,b=a+1,c=a+n+1,d=c+1;triangles.AddRange(new[]{a,c,b,b,c,d});}var m=new Mesh{name="Procedural amber beer bottle"};m.SetVertices(vertices);m.SetUVs(0,uv);m.SetTriangles(triangles,0);m.RecalculateNormals();return m;}
  BottleVisual Bottle(int id){if(bottleMesh==null)bottleMesh=GlassMesh();var o=new GameObject("Presentation bottle "+id);o.layer=PresentationLayer;o.transform.SetParent(Root.transform);o.AddComponent<MeshFilter>().sharedMesh=bottleMesh;o.AddComponent<MeshRenderer>().sharedMaterial=glass;
   var label=Shape("Readable wrap label",PrimitiveType.Cylinder,new Vector3(0,.27f,0),new Vector3(.347f,.105f,.347f),sleeve,o.transform);
   // Two readable faces remain attached to the bottle; not overview billboards.
   Text("Bottle product",Product,o.transform,new Vector3(0,.28f,-.179f),.022f,Color.white).gameObject.SetActive(false); // Texture is the primary reusable label.
   var fill=Shape("Visible beer contents",PrimitiveType.Cylinder,new Vector3(0,.22f,0),new Vector3(.305f,.18f,.305f),liquid,o.transform);
   var top=Shape("Crown cap",PrimitiveType.Cylinder,new Vector3(0,.76f,0),new Vector3(.18f,.04f,.18f),cap,o.transform);
   return new BottleVisual{Root=o,Cap=top,Fluid=fill};
  }
  public void Update(LineSimulation sim,Camera camera){var alive=new HashSet<int>();foreach(var b in sim.Bottles){alive.Add(b.Id);if(!bottles.ContainsKey(b.Id))bottles[b.Id]=Bottle(b.Id);var styled=bottles[b.Id];BottleVisual old;if(!original.Products.TryGetValue(b.Id,out old))continue;
    styled.Root.transform.position=old.Root.transform.position;styled.Root.transform.rotation=old.Root.transform.rotation;styled.Cap.SetActive(old.Cap.activeSelf);styled.Cap.transform.localPosition=old.Cap.transform.localPosition;styled.Cap.transform.localRotation=old.Cap.transform.localRotation;
    float fraction=b.Stage==0?0:b.Stage==1?Mathf.Clamp01(b.Dwell/.7f):Mathf.Clamp01(b.Fill/500f);styled.Fluid.SetActive(fraction>.01f);float height=.43f*fraction;styled.Fluid.transform.localScale=new Vector3(.305f,height/2,.305f);styled.Fluid.transform.localPosition=new Vector3(0,.04f+height/2,0);
   }
   foreach(int id in new List<int>(bottles.Keys))if(!alive.Contains(id)){Dispose(bottles[id].Root);bottles.Remove(id);}
   foreach(var pair in machinery){pair.Value.localPosition=original.Moving[pair.Key].localPosition;pair.Value.localRotation=original.Moving[pair.Key].localRotation;}
   foreach(var sign in billboards)sign.rotation=Quaternion.LookRotation(sign.position-camera.transform.position);
  }
  public static void ConfigureLights(Light key,Light rim){key.cullingMask=1<<LegacyLayer;rim.cullingMask=1<<LegacyLayer;
   var warm=new GameObject("Presentation industrial key").AddComponent<Light>();warm.type=LightType.Directional;warm.intensity=1.05f;warm.color=new Color(1,.93f,.81f);warm.transform.rotation=Quaternion.Euler(54,-30,0);warm.shadows=LightShadows.Soft;warm.cullingMask=1<<PresentationLayer;
   var fill=new GameObject("Presentation cool skylight").AddComponent<Light>();fill.type=LightType.Directional;fill.intensity=.48f;fill.color=new Color(.77f,.9f,1);fill.transform.rotation=Quaternion.Euler(30,145,0);fill.cullingMask=1<<PresentationLayer;
  }
 }
}
