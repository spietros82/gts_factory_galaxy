using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using Braemac.Factory;
public static class VerifyTelemetry {
 static int passed;static void Check(bool b,string label){if(!b)throw new Exception("TELEMETRY FAIL "+label);passed++;Debug.Log("TELEMETRY PASS "+label);}
 static void Run(LineSimulation s,int n){for(int i=0;i<n;i++)s.Step();}
 public static void RunChecks(){passed=0;var s=new LineSimulation(42);Run(s,800);var p=new SimulatedPlcAdapter();var f=p.Capture(s,false);var m=new PlcMapping();m.Receive(f,10);
  var names=new HashSet<string>();bool valid=true;foreach(var t in f.tags)valid&=names.Add(t.name)&&t.name.StartsWith("Line01.")&&t.unit!=null&&t.source_time==s.Time&&t.has_value;
  Check(valid&&f.schema=="gts.plc/2.0"&&f.tags.Length==19&&f.Find("Line01.Conveyor.Running").origin.StartsWith("calculated")&&f.Find("Line01.Outfeed.AccumulationHigh").origin.StartsWith("calculated"),"Typed unique tags with actual source times, units and origin");
  Check(f.Find("Line01.Outfeed.BufferCount").number==s.BufferCount&&f.Find("Line01.Outfeed.PackedTotal").number==s.Packed,"Counts map actual process state");
  float value;Check(m.Number("Line01.Capper.Angle",10,out value)&&value==s.CapperRotation,"Turret position passes contract mapping");
  Check(m.Fresh(11.5)&&!m.Fresh(11.501)&&m.State("filler",12)=="Stale"&&!m.Number("Line01.Capper.Angle",12,out value),"Wall-time stale gate withholds current states and motion");
  Check(new PlcMapping().State("capper",0)=="Unknown"&&!new PlcMapping().Number("x",0,out value),"Absent frame stays Unknown");
  f.Find("Line01.Filler.State").has_value=false;Check(m.State("filler",10)=="Unknown","Missing tag never means Running");
  var held=p.Capture(s,true);Check(held.source_time==f.source_time&&held.sequence>f.sequence&&held.simulation_paused&&held.session==f.session,"Pause heartbeat retains process timestamp and session");
  var fresh=new SimulatedPlcAdapter().Capture(s,false);Check(fresh.session!=f.session&&fresh.sequence==1,"Reset adapter creates distinct session and sequence");
  var control=new LineSimulation(42);Run(control,800);s.PresenterFault("outfeed");var start=p.Capture(s,false);Check(start.Find("Line01.Outfeed.Blocked").boolean&&s.BufferCount==control.BufferCount,"Restriction flag changes before queue; no invented instant stop");
  Run(s,3200);Run(control,3200);var blocked=p.Capture(s,false);Check(s.BufferCount>=15&&s.Packed<control.Packed&&s.Produced<control.Produced&&s.Bottles.Count<=72,"Existing bounded process accumulates and upstream admissions slow against same-time healthy replay");
  bool waiting=false;for(int i=0;i<3000;i++){s.Step();var g=p.Capture(s,false);if(g.Find("Line01.Infeed.State").text=="Blocked"||g.Find("Line01.Filler.State").text=="Waiting")waiting=true;}
  Check(waiting,"Upstream delayed backpressure / waiting emerges from real bottle motion");
  int before=s.Packed;s.ClearOutfeed();Run(s,3000);Check(!s.OutfeedRestricted&&s.Packed>before+40&&s.BufferCount<15,"Clear restores flow and queue recovers");
  Check(s.Alarms.Contains("PLC accumulation high: packing buffer occupied"),"Recovered process retains alarm history");
  var healthy=p.Capture(control,false);Check(!healthy.Find("Line01.Outfeed.Blocked").boolean&&!healthy.Find("Line01.Outfeed.AccumulationHigh").boolean,"Healthy line is not falsely blocked");
  Check(JsonUtility.FromJson<PlcFrame>(JsonUtility.ToJson(healthy)).Find("Line01.Outfeed.PackedTotal").number==control.Packed,"Contract JSON round-trip preserves typed readings");
  File.WriteAllText(FactoryApp.Argument("--check-output"),"{\"passed\":"+passed+",\"scope\":\"actual C# telemetry adapter/mapping/process, offline; no inference\"}");
 }
}
