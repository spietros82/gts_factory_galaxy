using System;
using System.Collections.Generic;
using System.Globalization;
namespace Braemac.Factory {
 [Serializable] public sealed class PlcTag {
  public string name,asset,type,unit,quality="good",origin="simulated",text;
  public double source_time,number;public bool boolean,has_value=true;
  public string Value {get{return !has_value?"Unknown":type=="bool"?(boolean?"True":"False"):type=="string"?text:number.ToString(type=="int"?"0":"0.00",CultureInfo.InvariantCulture);}}
 }
 [Serializable] public sealed class PlcFrame {
  public string schema="gts.plc/2.0",session;public long sequence;public double source_time;public bool simulation_paused;public PlcTag[] tags;
  public PlcTag Find(string name){foreach(var t in tags)if(t.name==name)return t;return null;}
 }
 // A replaceable local adapter, not a PLC driver. All process values originate in the one LineSimulation.
 public sealed class SimulatedPlcAdapter {
  public string Session {get;private set;}=Guid.NewGuid().ToString("N");long sequence;
  public PlcFrame Capture(LineSimulation s,bool paused){
   var tags=new List<PlcTag>();
   Action<string,string,string,double,string> num=(asset,name,unit,v,type)=>tags.Add(new PlcTag{asset=asset,name="Line01."+name,type=type,unit=unit,number=v,source_time=s.Time,origin="calculated from simulator"});
   Action<string,string,bool,string> flag=(asset,name,v,origin)=>tags.Add(new PlcTag{asset=asset,name="Line01."+name,type="bool",unit="boolean",boolean=v,source_time=s.Time,origin=origin});
   double moved=0;int moving=0;
   foreach(var b in s.Bottles)if(!b.Rejected&&b.X>b.PreviousX+.00001){moved+=(b.X-b.PreviousX)/LineSimulation.TickSeconds;moving++;}
   flag("conveyor","Conveyor.Running",moving>0,"calculated from simulator motion");num("conveyor","Conveyor.Speed","scene units/s",moving==0?0:moved/moving,"float");
   num("infeed","BottleCount","bottles on line",s.ActiveCount,"int");num("infeed","Infeed.ProducedTotal","bottles",s.Produced,"int");
   num("packer","Outfeed.BufferCount","bottles",s.BufferCount,"int");num("packer","Outfeed.PackedTotal","bottles",s.Packed,"int");
   flag("packer","Outfeed.Blocked",s.OutfeedRestricted,"simulated presenter command");flag("packer","Outfeed.AccumulationHigh",s.BufferCount>=15,"calculated conventional threshold");
   foreach(string asset in new[]{"infeed","filler","capper","inspection","packer"}){
    bool present=false,active=false,queued=false;
    foreach(var b in s.Bottles){if(b.Rejected)continue;
     bool here=asset=="infeed"?b.X<-7:asset=="filler"?b.Stage==1:asset=="capper"?b.Stage==3:asset=="inspection"?b.X>=2&&b.X<5:b.X>=5;
     if(!here)continue;present=true;
     if(b.Stage==1||b.Stage==3||b.X>b.PreviousX+.00001)active=true;else queued=true;
    }
    string state=active?"Running":queued?"Blocked":present?"Stopped":"Waiting";
    if(asset=="packer"&&s.OutfeedRestricted)state="Blocked";
    tags.Add(new PlcTag{asset=asset,name="Line01."+char.ToUpperInvariant(asset[0])+asset.Substring(1)+".State",type="string",unit="state",text=state,source_time=s.Time,origin="calculated activity / queue state"});
   }
   for(int h=0;h<4;h++){double stroke=0;foreach(var b in s.Bottles)if(b.Stage==1&&b.Head==h)stroke=Math.Sin(Math.PI*b.Dwell/.7);num("filler","Filler.Head"+(h+1)+".PositionY","scene units",1.95-stroke*.12,"float");}
   num("capper","Capper.Angle","degrees",s.CapperRotation,"float");
   num("packer","Packer.PusherZ","scene units",Math.Sin(Math.PI*Math.Min(1,Math.Max(0,(s.Time-s.LastPackedTime)/.45)))*.4,"float");
   return new PlcFrame{session=Session,sequence=++sequence,source_time=s.Time,simulation_paused=paused,tags=tags.ToArray()};
  }
 }
 // This is the presentation boundary. Unknown values are never defaulted to running or zero.
 public sealed class PlcMapping {
  public PlcFrame Frame {get;private set;}public double ReceivedAt {get;private set;}public const double StaleSeconds=1.5;
  public void Receive(PlcFrame f,double wall){Frame=f;ReceivedAt=wall;}
  public bool Fresh(double wall){return Frame!=null&&wall-ReceivedAt<=StaleSeconds;}
  public string Quality(PlcTag t,double wall){return Frame==null||t==null||!t.has_value?"Missing":!Fresh(wall)?"Stale":t.quality;}
  public string State(string asset,double wall){if(Frame==null)return "Unknown";foreach(var t in Frame.tags)if(t.asset==asset&&t.name.EndsWith(".State"))return Quality(t,wall)=="good"?t.text:Quality(t,wall)=="Stale"?"Stale":"Unknown";return "Unknown";}
  public bool Number(string name,double wall,out float value){value=0;if(!Fresh(wall))return false;var t=Frame.Find(name);if(t==null||!t.has_value||t.quality!="good")return false;value=(float)t.number;return true;}
 }
}
