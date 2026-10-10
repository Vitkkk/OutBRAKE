// Extract training predictors with the SAME AGL/Bunkers/SRH code as the app.
const fs=require('fs'),vm=require('vm'),path=require('path');
const project=path.resolve(__dirname,'..'),root=fs.existsSync(path.join(project,'dist'))?path.join(project,'dist'):project;
const context={console,Math,Date,JSON,Number,String,Array,Object,Set,Map,Error,URLSearchParams,AbortController,setTimeout,clearTimeout,matchMedia:()=>({matches:false}),document:{getElementById:()=>({getContext:()=>({})})},window:{OUTBRAKE_HEADLESS:true}};
vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'app.js'),'utf8'),context);
const app=context.window.OutBRAKE,source=JSON.parse(fs.readFileSync(path.join(__dirname,'sources.json'))),rows=[],rejected=[];
for(const year of [2024,2025]){
 const weather=JSON.parse(fs.readFileSync(path.join(__dirname,'cache',`gfs-${year}.json`)));
 weather.forEach((d,j)=>{const g=source.grid[j];for(let i=0;i<d.hourly.time.length;i+=6){
  const time=d.hourly.time[i]+'Z';
  // Single-hour view avoids repeated full-series searches and preserves nulls.
  const one={...d,hourly:Object.fromEntries(Object.entries(d.hourly).map(([k,v])=>[k,[v[i]]]))};
  try{const e=app.envFromData(one,time,'gfs',g.lat);if(e.cin===null)throw Error('Missing CIN');
   rows.push({year,point:g.id,lat:g.lat,lon:g.lon,time,cape:e.cape,cin:e.cin,shear:e.shear,srh:e.srh,lcl:e.lcl,t:e.t,td:e.td,motion_u:e.motion.u,motion_v:e.motion.v,favor:e.favor});
  }catch(err){rejected.push({point:g.id,time,reason:err.message});}
 }});
}
fs.writeFileSync(path.join(__dirname,'cache','features.json'),JSON.stringify(rows));fs.writeFileSync(path.join(__dirname,'rejected.json'),JSON.stringify(rejected,null,2));console.log({rows:rows.length,rejected:rejected.length});
