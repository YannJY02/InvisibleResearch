import {mkdirSync,writeFileSync} from 'node:fs';
import {homedir} from 'node:os';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const here=dirname(fileURLToPath(import.meta.url));
const out=join(here,'artifacts/interactive');
const skill=resolve(process.env.ANATOMY_HOME||join(homedir(),'.agents/skills/anatomy'));
mkdirSync(out,{recursive:true});
const assert=(condition,message)=>['eval',`(()=>{if(!(${condition}))throw Error(${JSON.stringify(message)});return ${JSON.stringify(message+' passed')}})()`];
const checkVector=(vector)=>assert(`JSON.stringify(window.featureDemo.state.result.vector)===${JSON.stringify(JSON.stringify(vector))}`,'expected feature vector '+vector);
// Headless Chrome on macOS does not open native select menus with End.
// Native selects are also exercised in the visible in-app browser.
const select=(id,value)=>['eval',`(()=>{const el=document.getElementById(${JSON.stringify(id)});el.value=${JSON.stringify(value)};el.dispatchEvent(new Event('input',{bubbles:true}));return el.value})()`];
function run(name,actions,args=[]){
  const file=join(out,name+'.json');writeFileSync(file,JSON.stringify(actions,null,2));
  const r=spawnSync(process.execPath,[join(skill,'scripts/drive.mjs'),join(out,args.includes('--light')?'index-light.html':'index.html'),'--actions',file,'--height','2200',...args.filter(a=>a!=='--light')],{encoding:'utf8'});
  const log=(r.stdout||'')+(r.stderr||'');writeFileSync(join(out,name+'.log'),log);process.stdout.write(log);
  if(r.status!==0||/exception:|console error:|timed out/i.test(log)||!log.includes('console: clean'))throw Error(name+' failed');
}
const actions=[
  ['wait',800],['click','#tour'],checkVector([.5,2,40,0,0,1,0]),
  ['key','End','#area'],['wait',1400],checkVector([1.75,2,90,0,0,1,0]),
  assert('window.featureDemo.state.positions.every((v,i)=>Math.abs(v-window.featureDemo.state.targets[i])<.3)','sliders settle at outputs'),
  ['lines'],['shot',join(out,'max-dark.png'),'.iso-stage',4],
  ['key',' ','#missing'],checkVector([.5,2,40,1,0,1,0]),
  assert('document.querySelector("#area").disabled','missing input disabled'),
  select('district','远郊'),checkVector([.5,2,40,1,0,0,1]),
  select('rooms','5'),checkVector([.5,5,16,1,0,0,1]),
  ['key','ArrowRight','.iso-stage'],assert('window.featureDemo.state.stage===1','keyboard selects explanation'),
  ['click','[data-preset="reset"]'],checkVector([.5,2,40,0,0,1,0]),
  ['key','Home','#area'],select('rooms','5'),checkVector([-.25,5,4,0,0,1,0]),['wait',1400],['lines'],
  ['click','[data-preset="reset"]'],['wait',1400],
  ['move','[data-step="2"]',.5,.5],['shot',join(out,'hover-dark.png'),'.iso-plate',1],
  ['click','[data-preset="large"]'],['sheet',join(out,'motion.png'),100,6,'.iso-stage',1,null,3],
  select('rooms','1'),checkVector([1.75,1,180,0,0,1,0]),
  ['click','#theme'],['wait',1400],['shot',join(out,'max-light.png'),'.iso-stage',4],['lines'],
  assert('window.featureDemo.state.fitted.min===40 && window.featureDemo.state.fitted.max===120 && window.featureDemo.state.fitted.median===80','training calibration unchanged'),
  ['click','#tour'],['wait',9400],assert('window.featureDemo.state.stage===2','idle tour advances'),
  ['eval','document.body.style.paddingBottom="100vh";document.querySelector("footer").scrollIntoView()'],['wait',400],
  assert('!window.featureDemo.state.visible','offscreen observer stops animation'),
  assert('document.documentElement.scrollWidth===innerWidth','no horizontal overflow'),
];
run('browser-desktop',actions,['--height','1000']);
run('browser-reduced',[
  ['wait',300],assert('!window.featureDemo.state.tour','reduced motion starts still'),
  ['click','[data-preset="large"]'],checkVector([1.75,2,90,0,0,1,0]),
  assert('window.featureDemo.state.positions.every((v,i)=>v===window.featureDemo.state.targets[i])','reduced motion immediate position'),
  ['click','#tour'],assert('window.featureDemo.state.stage===2 && !window.featureDemo.state.tour','reduced motion manual step'),
  ['click','[data-preset="reset"]'],['lines'],['shot',join(out,'rest-light.png'),'.iso-stage',4],
  assert('document.documentElement.scrollWidth===innerWidth','phone no horizontal overflow'),
],['--reduced','--width','390','--light']);
console.log('Browser checks passed.');
