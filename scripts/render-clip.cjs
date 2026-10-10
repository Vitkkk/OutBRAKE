const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const {spawn}=require('child_process');
const {createCanvas,loadImage}=require(process.env.OUTBRAKE_CANVAS_MODULE||'/opt/codex/runtimes/codex-primary-runtime/dependencies/node/node_modules/@napi-rs/canvas');
const project=path.resolve(__dirname,'..');
const root=fs.existsSync(path.join(project,'dist'))?path.join(project,'dist'):project,main=createCanvas(1280,720),sounding=createCanvas(620,250),elements=new Map();
function el(id){if(!elements.has(id))elements.set(id,{textContent:'',innerHTML:'',value:'',disabled:false,classList:{add(){},remove(){},toggle(){}},setAttribute(){},append(){},getContext:()=>sounding.getContext('2d')});return elements.get(id);}
elements.set('map',main);main.getBoundingClientRect=()=>({width:1280,height:720});
const context={console,Math,Date,JSON,Number,String,Array,Object,Set,Map,Error,URLSearchParams,AbortController,setTimeout,clearTimeout,matchMedia:()=>({matches:false}),document:{getElementById:el,createElement:name=>name==='canvas'?createCanvas(1,1):el(name)},window:{OUTBRAKE_HEADLESS:true,devicePixelRatio:1},requestAnimationFrame(){}};
vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(root,'app.js'),'utf8'),context);
const app=context.window.OutBRAKE,boot=JSON.parse(fs.readFileSync(process.argv.includes('--snapshot')?process.argv[process.argv.indexOf('--snapshot')+1]:path.join(root,'bootstrap.json'),'utf8'));
Object.assign(app.state,{world:JSON.parse(fs.readFileSync(path.join(root,'world.json'),'utf8')),region:boot.region,ranking:boot.ranking,retrievedAt:boot.retrievedAt,env:app.envFromData(boot.data,boot.region.time,'gfs',boot.region.lat)});
(async()=>{
app.generate();app.drawSounding();
const satelliteMeta=JSON.parse(fs.readFileSync(path.join(root,'satellite.json'),'utf8'));
app.state.satellite={...satelliteMeta,image:await loadImage(fs.readFileSync(path.join(root,satelliteMeta.file)))};

if(process.env.OUTBRAKE_TEST_ECMWF){const d=JSON.parse(fs.readFileSync(process.env.OUTBRAKE_TEST_ECMWF,'utf8'));const e=app.envFromData(d,boot.region.time,'ecmwf',boot.region.lat);assert(Number.isFinite(e.shear)&&Number.isFinite(e.srh));console.log('ECMWF profile parsed successfully');}
assert(app.state.env.profile.every(x=>x.z>=0));assert(Number.isFinite(app.state.env.shear));assert(Number.isFinite(app.state.env.srh));assert(app.state.env.profile.at(-1).z>6000);
const baseline=JSON.stringify(app.state.tornadoes);app.generate();assert.equal(JSON.stringify(app.state.tornadoes),baseline,'Seed must reproduce the same tornadoes');
const p=app.state.env.profile,mNorth=app.stormMotion(p,30),mSouth=app.stormMotion(p,-30);assert(Math.hypot(mNorth.u-mSouth.u,mNorth.v-mSouth.v)>14.9,'Hemispheric storm-motion branches must differ');
for(const tor of app.state.tornadoes){assert(tor.end>tor.start);const cell=app.state.cells.find(c=>c.id===tor.cell);assert(tor.start>=cell.start&&tor.end<=cell.end);assert(Number.isFinite(app.torPosition(tor,tor.start).x));}
const cape=app.state.env.cape;app.state.env.cape=0;app.generate();assert.equal(app.state.tornadoes.length,0);app.state.env.cape=cape;app.generate();
assert.equal(app.efRating(217),2);assert.equal(app.efRating(300),4);assert.equal(app.efRating(350),5);
app.render(main.getContext('2d'),1280,720,240);fs.writeFileSync(path.join(__dirname,'summary.png'),main.toBuffer('image/png'));
app.render(main.getContext('2d'),1280,720,105);fs.writeFileSync(path.join(__dirname,'preview.png'),main.toBuffer('image/png'));fs.writeFileSync(path.join(__dirname,'profile.png'),sounding.toBuffer('image/png'));
console.log(JSON.stringify({verification:'passed',region:boot.region.name,environment:{cape:app.state.env.cape,shear:app.state.env.shear,srh:app.state.env.srh,lcl:app.state.env.lcl,motion:app.state.env.motion,favor:app.state.env.favor},cells:app.state.cells.length,tornadoes:app.state.tornadoes.length,peak:Math.max(0,...app.state.tornadoes.map(t=>t.peak))}));
if(process.argv.includes('--video')){
 const output=process.argv[process.argv.indexOf('--video')+1]||path.join(__dirname,'OutBRAKE_USA_2026-10-10.mp4'),fps=24,duration=36;
 const encoder=spawn('ffmpeg',['-y','-f','rawvideo','-pix_fmt','rgba','-s','1280x720','-r',String(fps),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',output],{stdio:['pipe','ignore','pipe']});let error='';encoder.stderr.on('data',d=>error+=d.toString());
 const done=new Promise((resolve,reject)=>{encoder.on('error',reject);encoder.on('exit',code=>code===0?resolve():reject(Error(error)));});
 (async()=>{for(let f=0;f<fps*duration;f++){const t=Math.min(240,f/(fps*30-1)*240),c=main.getContext('2d');app.render(c,1280,720,t);if(t<240){c.fillStyle='#090f17dc';c.fillRect(16,15,640,43);c.fillStyle='#ace58b';c.font='bold 13px monospace';c.fillText('SURTO FICTÍCIO / '+boot.region.name.toUpperCase(),29,34);c.fillStyle='#b0c0cd';c.font='11px monospace';c.fillText('GFS real · CAPE '+app.state.env.cape+' J/kg · shear '+app.state.env.shear.toFixed(1)+' m/s · +'+String(Math.floor(t/60)).padStart(2,'0')+':'+String(Math.floor(t%60)).padStart(2,'0'),29,49);}const buffer=c.getImageData(0,0,1280,720).data;if(!encoder.stdin.write(buffer))await new Promise(r=>encoder.stdin.once('drain',r));}encoder.stdin.end();await done;console.log('Video written: '+output);})().catch(e=>{console.error(e);process.exitCode=1;});
}

})().catch(e=>{console.error(e);process.exitCode=1;});
