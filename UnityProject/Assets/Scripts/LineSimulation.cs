using System;
using System.Collections.Generic;
namespace Braemac.Factory {
 [Serializable] public class Observation {
  public string contract="gts.telemetry/1", asset_id, name, unit, quality, machine_state;
  public long sequence; public double timestamp; public float value; public bool has_value;
  public int bottle_id=-1, head=-1;
 }
 public sealed class Bottle {
  public int Id, Head, Stage; public float X=-13, PreviousX=-13, Fill, Dwell, RejectTravel;
  public bool CapPresent=true, CapDisplaced, Rejected; public double Born;
 }
 // The sole process clock is Time. Fault state is private and never serialized into observation payloads.
 public sealed class LineSimulation {
  public const double TickSeconds=.05;
  public double Time {get;private set;} public long Sequence {get;private set;}
  public int Packed {get;private set;} public int Rejected {get;private set;}
  public double LastPackedTime {get;private set;}=-100;public float CapperRotation {get;private set;}
  public int Produced {get;private set;} public int LostObservations {get;private set;}
  public readonly List<Bottle> Bottles=new List<Bottle>();
  public readonly List<Observation> Observations=new List<Observation>();
  public readonly List<string> Alarms=new List<string>();
  readonly List<Pending> pending=new List<Pending>();
  readonly Random noise; readonly Random qualityNoise; readonly Random defectNoise;
  bool restrictOutfeed, capProblem, drift; double driftStarted, nextBottle, nextPacked, nextTelemetry;
  int nextId; public bool ObservationLoss {get;set;} public int Seed {get;private set;}
  struct Pending {public double due;public Observation value;}
  public LineSimulation(int seed=42){Seed=seed;noise=new Random(seed);qualityNoise=new Random(seed+19);defectNoise=new Random(seed+71);}
  public void PresenterFault(string scenario){
   if(scenario=="outfeed")restrictOutfeed=true;
   else if(scenario=="fill"){drift=true;driftStarted=Time;}
   else if(scenario=="cap")capProblem=true;
   else throw new ArgumentException("Unsupported presenter scenario");
  }
  public int BufferCount {get{int n=0;foreach(var b in Bottles)if(!b.Rejected&&b.X>=5)n++;return n;}}
  public int ActiveCount {get{int n=0;foreach(var b in Bottles)if(!b.Rejected)n++;return n;}}
  public void Step(){
   Time+=TickSeconds;bool capCycling=false;foreach(var bottle in Bottles)if(bottle.Stage==3)capCycling=true;if(capCycling)CapperRotation+=(float)TickSeconds*180;
   foreach(var b in Bottles)b.PreviousX=b.X;
   if(Time>=nextBottle){nextBottle=Time+.65;
    bool free=Bottles.Count<72;foreach(var b in Bottles)if(!b.Rejected&&b.X<-12.5)free=false;
    if(free){Bottles.Add(new Bottle{Id=++nextId,Head=(nextId-1)%4,Born=Time});Produced++;}
   }
   Bottles.Sort((a,b)=>b.X.CompareTo(a.X)); float leader=100;
   for(int i=0;i<Bottles.Count;i++){
    var b=Bottles[i]; if(b.Rejected){b.RejectTravel+=(float)TickSeconds*.8f;continue;}
    float limit=leader-.46f;
    if(b.Stage==0&&b.X>=-7){b.Stage=1;b.Dwell=0;}
    if(b.Stage==1){b.Dwell+=(float)TickSeconds;
     if(b.Dwell>=.7f){double amount=drift&&b.Head==2?Math.Min(24,(Time-driftStarted)*.08):0;
      double variation=drift&&b.Head==2?Math.Min(3,(Time-driftStarted)*.012):0;
      b.Fill=(float)(500-amount+Gaussian()*(1.3+variation));b.Stage=2;
      Emit("filler","fill_ml",b.Fill,"mL",b,"cycling");
      if(b.Fill<490||b.Fill>510)AddAlarm("PLC fill check outside 490–510 mL");}
    }
    else if(b.Stage==3){b.Dwell+=(float)TickSeconds;
     if(b.Dwell>=.45f){double trial=defectNoise.NextDouble();b.CapPresent=!(capProblem&&trial<.16);b.CapDisplaced=capProblem&&trial>=.16&&trial<.32;b.Stage=4;}
    }
    else {
     float desired=b.X+(float)TickSeconds*1.1f;
     if(b.Stage==0)desired=Math.Min(desired,-7);
     if(b.Stage==2)desired=Math.Min(desired,-2);
     if(b.Stage==4)desired=Math.Min(desired,3);
     if(b.Stage==6)desired=Math.Min(desired,12.5f);
     b.X=Math.Max(b.X,Math.Min(desired,limit));
     if(b.Stage==2&&b.X>=-2){b.Stage=3;b.Dwell=0;}
     if(b.Stage==4&&b.X>=3){
      Emit("inspection","cap_presence_switch",b.CapPresent?1:0,"boolean",b,"checking");
      if(!b.CapPresent){AddAlarm("PLC cap-presence switch: cap absent");b.Rejected=true;}
      // Scripted presence switch rejects missing caps only; placement requires independent inspection.
      b.Stage=6;
     }
     if(b.Stage==6&&b.X>=12.5f&&Time>=nextPacked){
      nextPacked=Time+(restrictOutfeed?3.4:.5);Packed++;LastPackedTime=Time;Bottles.RemoveAt(i--);continue;
     }
    }
    leader=b.X;
   }
   for(int i=Bottles.Count-1;i>=0;i--)if(Bottles[i].Rejected&&Bottles[i].RejectTravel>3.3){Rejected++;Bottles.RemoveAt(i);}
   if(BufferCount>=15)AddAlarm("PLC accumulation high: packing buffer occupied");
   if(Time>=nextTelemetry){nextTelemetry=Time+.5;
    Emit("packer","buffer_count",BufferCount,"bottles",null,BufferCount>=15?"interlocked upstream hold":"cycling");
    Emit("packer","packed_total",Packed,"bottles",null,"cycling");
    Emit("infeed","active_bottles",ActiveCount,"bottles",null,ActiveCount>=55?"blocked":"cycling");
   }
   for(int i=pending.Count-1;i>=0;i--)if(pending[i].due<=Time){
    Observations.Add(pending[i].value);pending.RemoveAt(i);
   }
   if(Observations.Count>400)Observations.RemoveRange(0,Observations.Count-400);
  }
  double Gaussian(){double a=Math.Max(1e-9,noise.NextDouble());return Math.Sqrt(-2*Math.Log(a))*Math.Cos(2*Math.PI*noise.NextDouble());}
  void AddAlarm(string text){if(!Alarms.Contains(text))Alarms.Add(text);}
  void Emit(string asset,string name,float value,string unit,Bottle b,string state){
   bool missing=ObservationLoss&&qualityNoise.NextDouble()<.12;
   var o=new Observation{asset_id=asset,name=name,value=missing?0:value,has_value=!missing,quality=missing?"missing":"good",unit=unit,
    timestamp=Time,sequence=++Sequence,bottle_id=b==null?-1:b.Id,head=b==null?-1:b.Head,machine_state=state};
   if(missing)LostObservations++;
   pending.Add(new Pending{due=Time+(ObservationLoss?.8:.15),value=o});
  }
 }
}
