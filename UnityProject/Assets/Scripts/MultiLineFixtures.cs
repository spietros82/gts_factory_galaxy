using System;
using System.IO;
using System.Collections;
using UnityEngine;
namespace Braemac.Factory {
 [Serializable] public class MultiFixture {public string id,product,example;public int line;}
 [Serializable] public class MultiFixtureSet {public MultiFixture[] items;}
 // Explicit offline integration authoring, separate from normal capture and never included
 // in inference payloads. This is new synthetic integration evidence, not a held-out retest.
 public sealed partial class MultiLineFactory {
  IEnumerator CaptureFixtures(string path){while(!registered)yield return null;yield return new WaitForEndOfFrame();var set=JsonUtility.FromJson<MultiFixtureSet>(File.ReadAllText(path));
   foreach(var fixture in set.items){yield return new WaitForEndOfFrame();var line=visuals[fixture.line];line.Brewery.SetProduct(fixture.product);line.Example=fixture.example;Bottle target=null;foreach(var b in line.State.Sim.Bottles)if(b.Stage>=4&&!b.Rejected){target=b;break;}if(target==null)throw new Exception("Fixture target absent");var visual=line.Brewery.BottleById(target.Id);visual.Root.transform.rotation=Quaternion.identity;visual.Cap.SetActive(true);visual.Cap.transform.localPosition=new Vector3(0,.76f,0);visual.Cap.transform.localRotation=Quaternion.identity;visual.Fluid.SetActive(true);visual.Fluid.transform.localScale=new Vector3(.305f,.43f/2,.305f);visual.Fluid.transform.localPosition=new Vector3(0,.04f+.43f/2,0);capture.Examples(line);double a,bms,c;var input=capture.Capture(line,target,true,out a,out bms,out c);File.WriteAllText(Path.Combine(dataPath,fixture.id+".json"),JsonUtility.ToJson(input));yield return Command("/batch",JsonUtility.ToJson(input));yield return new WaitForSecondsRealtime(.12f);
   }Debug.Log("STAGE4_FIXTURES_COMPLETE "+set.items.Length);Application.Quit();
  }
 }
}
