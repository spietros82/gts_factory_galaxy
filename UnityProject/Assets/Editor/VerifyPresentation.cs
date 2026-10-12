using System;
using System.IO;
using UnityEngine;
using Braemac.Factory;
public static class VerifyPresentation {
 static int passed;static void Check(bool good,string text){if(!good)throw new Exception("STAGE1_CHECK FAILED "+text);passed++;Debug.Log("STAGE1_CHECK PASS "+text);}
 public static void RunAll(){VerifyFactory.RunChecks();RunChecks();}
 public static void RunChecks(){
  var scene=UnityEditor.SceneManagement.EditorSceneManager.NewScene(UnityEditor.SceneManagement.NewSceneSetup.EmptyScene,UnityEditor.SceneManagement.NewSceneMode.Single);
  var sim=new LineSimulation(42);for(int i=0;i<800;i++)sim.Step();var original=new FactoryGeometry();original.SetRenderLayer(BreweryPresentation.LegacyLayer);
  var camera=new GameObject("Presentation test camera").AddComponent<Camera>();camera.transform.position=new Vector3(0,12,-24);
  var presentation=new BreweryPresentation(original);original.Update(sim,1,camera);presentation.Update(sim,camera);
  int produced=sim.Produced,packed=sim.Packed;long seq=sim.Sequence;double time=sim.Time;int count=sim.Bottles.Count;Bottle first=sim.Bottles[0];var originalBottle=original.Products[first.Id];var capMaterial=originalBottle.Cap.GetComponent<Renderer>().sharedMaterial;Color capColor=capMaterial.color;Vector3 capScale=originalBottle.Cap.transform.localScale;
  foreach(string product in new[]{"LAGER","IPA","STOUT"}){Check(presentation.SetProduct(product)&&presentation.Product==product,"Selectable product "+product);presentation.Update(sim,camera);}
  Check(sim.Produced==produced&&sim.Packed==packed&&sim.Sequence==seq&&sim.Time==time&&sim.Bottles.Count==count,"Product changes do not advance/mutate production state");
  Check(capMaterial.color==capColor&&originalBottle.Cap.transform.localScale==capScale,"Original cap materials and geometry preserved");
  bool separate=true;foreach(var t in original.Root.GetComponentsInChildren<Transform>(true))separate&=t.gameObject.layer==BreweryPresentation.LegacyLayer;foreach(var t in presentation.Root.GetComponentsInChildren<Transform>(true))separate&=t.gameObject.layer==BreweryPresentation.PresentationLayer;
  Check(separate,"Dynamic bottles and decoration remain in separate render layers");Check(presentation.VisibleBottles==sim.Bottles.Count,"Presentation bottles match simulation identities/population");Check(!presentation.SetProduct("UNKNOWN"),"Unsupported identity rejected without changing process");
  Directory.CreateDirectory("../reports/stage1/raw");File.WriteAllText("../reports/stage1/presentation-checks.json","{\"passed\":"+passed+",\"scope\":\"Editor runs real geometry and product implementation; native visual QA separate\"}");
 }
}
