using System;
using System.IO;
using System.Collections.Generic;
using UnityEngine;
using Braemac.Factory;
public static class VerifyMultiLine {
 static int passed;static void Check(bool value,string label){if(!value)throw new Exception("MULTILINE FAIL "+label);passed++;Debug.Log("MULTILINE PASS "+label);}
 public static void RunAll(){VerifyFactory.RunChecks();VerifyPresentation.RunChecks();VerifyTelemetry.RunChecks();RunChecks();}
 public static void RunChecks(){var c=new MultiLineClock();c.Resize(3);c.Heartbeat(0,false);Check(c.Lines.Count==3&&c.Lines[0].Product=="LAGER"&&c.Lines[1].Product=="IPA"&&c.Lines[2].Product=="STOUT","Independent cyclic product instances");
  var ids=new HashSet<string>();bool unique=true;foreach(var line in c.Lines)unique&=ids.Add(line.Adapter.Session);Check(unique,"Distinct sessions");Check(!object.ReferenceEquals(c.Lines[0].Sim,c.Lines[1].Sim)&&c.Lines[0].Sim.Seed!=c.Lines[1].Sim.Seed,"Separate state and seeds");
  bool tagged=true;foreach(var line in c.Lines)foreach(var t in line.Mapping.Frame.tags)tagged &= t.name.StartsWith(line.Id+".");Check(tagged,"All tags scoped to their originating line");
  c.Lines[0].Sim.PresenterFault("outfeed");for(int i=0;i<6000;i++)c.Step(i*.05);Check(c.Lines[0].Sim.OutfeedRestricted&&!c.Lines[1].Sim.OutfeedRestricted&&!c.Lines[2].Sim.OutfeedRestricted,"Fault local to one line");Check(c.Lines[0].Sim.Packed<c.Lines[1].Sim.Packed&&c.Lines[0].Sim.BufferCount>=15&&c.Lines[1].Sim.BufferCount<15,"Independent accumulation and healthy counter");Check(Math.Abs(c.Lines[0].Sim.Time-c.Lines[2].Sim.Time)<1e-9&&c.Ticks==6000,"One coordinated fixed-step clock");
  c.Lines[0].Sim.ClearOutfeed();for(int i=0;i<3000;i++)c.Step(i*.05);Check(c.Lines[0].Sim.BufferCount<15,"Clearing restores actual flow");var first=c.Lines[0];var removed=c.Lines[2];c.Resize(1);c.Resize(3);Check(object.ReferenceEquals(first,c.Lines[0])&&c.Lines[2].Adapter.Session!=removed.Adapter.Session,"Resize preserves survivors and retires removed sessions");var old=c.Lines[0].Adapter.Session;c.Reset(0);Check(c.Lines[0].Adapter.Session!=old,"Reset identity generation");double before=c.Lines[0].Sim.Time;c.Heartbeat(100,true);Check(c.Lines[0].Sim.Time==before&&c.Lines[0].Mapping.Frame.simulation_paused,"Pause heartbeat no second process clock");bool guard=false;try{c.Resize(49);}catch(ArgumentOutOfRangeException){guard=true;}Check(guard,"Upper allocation guard");
  File.WriteAllText(FactoryApp.Argument("--check-output"),"{\"passed\":"+passed+",\"scope\":\"C# scheduler, identities, telemetry, independent faults and recovery; no inference\"}");
 }
}
