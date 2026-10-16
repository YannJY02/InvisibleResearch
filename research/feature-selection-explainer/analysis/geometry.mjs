import * as k from './vendor/iso-kit.mjs';

export const bed={x:-182,y:-126,w:364,d:264,r:6};
export const projection=k.fitProjection(k.boxCorners(bed,-12,24),760,440,{pad:45,azimuth:38,elevation:42});
export const lanes=Array.from({length:7},(_,i)=>-102+i*32);
export const travel=126;
const P=projection;
const S=(plan,z,h,tone='mid',lit=false)=>k.solidSvg(k.slabOf(plan,z,h,P,4,.65),{tone,lit});
const line=(d,tone='lo')=>k.lineSvg(d,{tone});
const dot=(x,y,z)=>k.dotsSvg([k.iso([x,y,z],P)],{size:.65});
const screws=(plan,z)=>k.corners(plan,2.5).map(([x,y])=>dot(x,y,z)).join('');

export function instrument() {
  let solids=0;
  const slab=(...args)=>{solids++;return S(...args);};
  const out=[`<path class="iso-halo" d="${k.haloOf(bed,-12,12,P)}"/>`];
  for(const [x,y] of k.corners(bed,18).sort((a,b)=>k.depthOf([...a,0],P)-k.depthOf([...b,0],P)))
    out.push(slab({x:x-7,y:y-7,w:14,d:14,r:2},-12,5,'lo'));
  out.push(slab(bed,-7,7,'lo'));
  out.push(slab(k.insetPlan(bed,6),0,2,'lo'));
  out.push(line(k.planOutline(k.insetPlan(bed,3),0,P),'faint'));
  out.push(screws(k.insetPlan(bed,7),2));
  // Each track is separate in depth. Its support stack is drawn bottom to top.
  for(const [i,y] of lanes.entries()) {
    const parts=[];
    for(const ry of [y-6,y+3]) parts.push(slab({x:-151,y:ry,w:302,d:3,r:.4},2,3));
    for(const x of [-160,151]) {
      const stop={x,y:y-9,w:9,d:22,r:1};
      parts.push(slab(stop,2,9),screws(stop,11));
    }
    const ruler={x:-126,y:y+7,w:252,d:6,r:.5};
    parts.push(slab(ruler,2,.8,'lo'));
    const ticks=k.topTicks(-126,126,6,5,ruler.y,2.8,[2.4,5],P);
    parts.push(line(ticks.minor),line(ticks.major,'mid'));
    parts.push(line(k.lineOnTop([0,y+7],[0,y+13],2.8,P),'hi'));
    // Six small dots on the left stops number the lanes without floating text.
    for(let n=0;n<(i===6 ? 1:i+1);n++) parts.push(dot(-155.5,y-5+n*2.5,11));
    const cursor=[];
    cursor.push(slab({x:-9,y:y-6,w:18,d:12,r:1},5,2,'hi',i===6));
    cursor.push(slab({x:-3,y:y-5,w:6,d:17,r:.6},7,3,'hi',i===6));
    cursor.push(slab({x:-7,y:y-3,w:14,d:6,r:1},10,5,'mid',i===6));
    for(const x of [-4,0,4]) cursor.push(line(k.lineOnTop([x,y-3],[x,y+3],15,P),'lo'));
    cursor.push(screws({x:-9,y:y-6,w:18,d:12,r:1},7));
    cursor.push(line(k.lineOnTop([0,y+3],[0,y+12],10,P),i===6?'lit':'hi'));
    parts.push(`<g data-cursor="${i}" transform="${k.translateAlong(P,[0,0,0])}">${cursor.join('')}</g>`);
    out.push(`<g data-track="${i}">${parts.join('')}</g>`);
  }
  const label={x:-165,y:122,w:54,d:8,r:1};
  out.push(slab(label,2,.7,'lo'),screws(label,2.7));
  out.push(k.faceTextSvg(k.topMatrix([-138,126],2.7,P),'ANATOMY / 06',{size:3,anchor:'middle',tone:'mid'}));
  for(const x of [112,130,148]) {
    const key={x,y:122,w:11,d:8,r:1};
    out.push(slab(key,2,3,'mid'),line(k.planOutline(k.insetPlan(key,2),5,P),'lo'));
  }
  if(solids!==66) throw new Error(`Expected 66 parts, found ${solids}`);
  return k.figureSvg({width:760,height:440,label:'六轨机械比较尺：由后向前为第 1 至第 6 轨，最前方高亮游标显示影子最大值或六次边际贡献的平均值。每个游标的位置与旁边的数字同步。',body:out});
}
