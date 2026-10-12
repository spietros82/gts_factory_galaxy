using System;
using System.IO;
using UnityEngine;
using Braemac.Factory;
public static class VerifyFactory {
 static int passed;static void Check(bool good,string label){if(!good)throw new Exception("FAILED: "+label);passed++;Debug.Log("FACTORY_CHECK PASS "+label);}
 static LineSimulation Run(string scenario,int ticks){var s=new LineSimulation(42);if(scenario!=null)s.PresenterFault(scenario);for(int i=0;i<ticks;i++)s.Step();return s;}
 public static void RunChecks(){
  passed=0;var a=Run(null,4000);var b=Run(null,4000);
  Check(a.Packed>80&&a.Alarms.Count==0,"Healthy seeded production and conventional alarms");
  Check(a.Packed==b.Packed&&a.Produced==b.Produced&&a.Sequence==b.Sequence,"Seeded replay deterministic");
  Check(a.Produced==a.Packed+a.Rejected+a.Bottles.Count,"Bottle conservation and finite population");
  var flow=Run("outfeed",4000);Check(flow.BufferCount>=15&&flow.Packed<a.Packed&&flow.Bottles.Count<=72,"Outfeed restriction accumulates with bounded buffer");
  Check(flow.Alarms.Contains("PLC accumulation high: packing buffer occupied"),"PLC accumulation alarm distinct from analytics");
  var fill=Run("fill",6000);bool low=false;foreach(var o in fill.Observations)if(o.name=="fill_ml"&&o.head==2&&o.value<490)low=true;
  Check(low&&fill.Alarms.Count>0,"Head drift produces measured low fill and PLC quality alarm");
  var cap=Run("cap",6000);Check(cap.Rejected>0&&cap.Alarms.Contains("PLC cap-presence switch: cap absent"),"Missing cap presence switch rejection");
  bool displaced=false;foreach(var bottle in cap.Bottles)if(bottle.CapDisplaced)displaced=true;Check(displaced,"Visible displaced cap state");
  var missing=new LineSimulation(42){ObservationLoss=true};for(int i=0;i<1200;i++)missing.Step();
  bool absent=false;foreach(var o in missing.Observations)if(!o.has_value&&o.quality=="missing")absent=true;
  Check(absent&&missing.LostObservations>0,"Missing observations explicitly flagged");
  var json=JsonUtility.ToJson(new ObservationBatch{session="test",sim_time=missing.Time,profile=2,observations=missing.Observations.ToArray()});
  Check(!json.Contains("scenario")&&!json.Contains("fault")&&!json.Contains("cap_displaced")&&!json.Contains("driftStarted"),"Observed payload excludes injected state");
  var reset=Run(null,4000);Check(reset.Packed==a.Packed,"Reset reconstructed replay matches seed");
  File.WriteAllText(FactoryApp.Argument("--check-output","../reports/unity-core-checks.json"),"{\"passed\":"+passed+",\"method\":\"Unity Editor executes actual C# simulation; not standalone visual QA\",\"unity\":\""+Application.unityVersion+"\"}");
 }
}
