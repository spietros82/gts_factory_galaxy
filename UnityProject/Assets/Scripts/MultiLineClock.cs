using System;
using System.Collections.Generic;
namespace Braemac.Factory {
 public sealed class IndependentLine {
  public readonly string Id,Instance,Product;public readonly LineSimulation Sim;public readonly SimulatedPlcAdapter Adapter;public readonly PlcMapping Mapping=new PlcMapping();
  public IndependentLine(int index,int seed=42){Id="Line"+(index+1).ToString("00");Instance=Guid.NewGuid().ToString("N");Product=new[]{"LAGER","IPA","STOUT"}[index%3];Sim=new LineSimulation(seed+index);Adapter=new SimulatedPlcAdapter(Id);for(int i=0;i<800;i++)Sim.Step();}
 }
 // Exactly one fixed-step scheduler advances each independent process once per coordinated tick.
 public sealed class MultiLineClock {
  public readonly int Seed;public MultiLineClock(int seed=42){Seed=seed;}public const int MaximumLines=48;public readonly List<IndependentLine> Lines=new List<IndependentLine>();public long Ticks;public double Time{get{return Ticks*LineSimulation.TickSeconds;}}
  public void Resize(int count){if(count<1||count>MaximumLines)throw new ArgumentOutOfRangeException("count");while(Lines.Count>count)Lines.RemoveAt(Lines.Count-1);while(Lines.Count<count)Lines.Add(new IndependentLine(Lines.Count,Seed));}
  public void Step(double wall){foreach(var line in Lines){line.Sim.Step();line.Mapping.Receive(line.Adapter.Capture(line.Sim,false),wall);}Ticks++;}
  public void Heartbeat(double wall,bool paused){foreach(var line in Lines)line.Mapping.Receive(line.Adapter.Capture(line.Sim,paused),wall);}
  public void Reset(int index){Lines[index]=new IndependentLine(index,Seed);}
 }
}
