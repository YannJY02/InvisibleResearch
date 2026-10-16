// Inlined by build.mjs inside a scope shared with the pure teaching model.
const $ = (s)=>document.querySelector(s);
const fitted=fit(TRAINING);
const fields={area:$('#area'),missing:$('#missing'),rooms:$('#rooms'),district:$('#district')};
const sliders=[...document.querySelectorAll('[data-slider]')];
const tabs=[...document.querySelectorAll('[data-step]')];
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let stage=0, tour=!reduced.matches, visible=false, frame=0,last=0,elapsed=0;
let positions=[0,0,0,0,0,0], targets=positions.slice(), result;
const fmt=(v)=>Number.isInteger(v)?String(v):v.toFixed(3).replace(/0+$/,'').replace(/\.$/,'');
function sample(){return {area:Number(fields.area.value),missing:fields.missing.checked,rooms:Number(fields.rooms.value),district:fields.district.value};}
function explain(){
  const s=sample(),r=result;
  const content=[
    ['IMPUTATION / 缺失值','没有记录，不等于零。',
      '面积缺失时，用训练集的中位数代填，同时保留一个“曾经缺失”的标记。否则，模型可能把未知误读成真的没有面积。',
      s.missing?'缺失 → 80 m² · 标记 1':fmt(s.area)+' m² → '+fmt(r.filledArea)+' m² · 标记 0',
      '后排滑块显示代填后的面积。试着勾选“没有填写面积”；80 是估计值，不是真实面积。'],
    ['SCALING / 数值尺度','换一把尺子，保留相对位置。',
      '这里采用 Min–Max 缩放：减去训练最小值，再除以训练范围。它改变单位，不改变这列数值的大小顺序。',
      '('+fmt(r.filledArea)+' − 40) / (120 − 40) = '+fmt(r.scaledArea),
      r.scaledArea>1||r.scaledArea<0?'超出 0—1 是正常的：新样本超出了训练范围；我们没有裁剪，也没有重学尺子。':'训练面积 40 映射到 0，120 映射到 1。拖到 180，看看为什么结果会超过 1。'],
    ['ONE-HOT / 类别编码','地区是类别，不是名次。',
      '为三个地区各留一个位置，属于哪一类，就把那一位设为 1。若直接编码成 1、2、3，一些模型可能误读出大小或距离关系。',
      s.district+' → ['+r.oneHot.join(', ')+']',
      '三个开关从左到右依次代表中心、近郊、远郊；0 为左端，1 为右端。词表之外的类别需要另定处理规则。'],
    ['DERIVATION / 特征构造','把“多大”变成“每间多大”。',
      '总面积相同，房间数不同，每间房的平均面积也不同。这个比值把已有字段组合成一种可能与任务相关的表达。',
      fmt(r.filledArea)+' m² / '+s.rooms+' 间 = '+fmt(r.areaPerRoom)+' m²/间',
      (s.missing?'当前比值使用填补后的面积，因此也带有估计的不确定性。':'这是总面积除以房间数，并非实测的单间面积。')+' 是否有用，仍需在独立验证数据上检验。']
  ][stage];
  ['#explain-kicker','#explain-title','#explain-copy','#formula','#formula-note'].forEach((sel,i)=>$(sel).textContent=content[i]);
  tabs.forEach((t,i)=>t.setAttribute('aria-pressed',String(i===stage)));
  document.querySelectorAll('[data-stage-part]').forEach(el=>el.classList.toggle('selected',Number(el.dataset.stagePart)===stage));
  document.querySelectorAll('.feature').forEach((el,i)=>el.classList.toggle('active',[[3],[0],[4,5,6],[2]][stage].includes(i)));
  $('[data-readout]').textContent=['面积 '+fmt(r.filledArea)+' m²','缩放 '+fmt(r.scaledArea),'编码 '+r.oneHot.join(' / '),'每间 '+fmt(r.areaPerRoom)+' m²'][stage];
  $('#tour').textContent=reduced.matches?'下一步':tour?'暂停导览':'自动导览';
  $('#tour').setAttribute('aria-pressed',String(tour));
}
function update(announce=true){
  const s=sample();result=transform(s,fitted);
  fields.area.disabled=s.missing;
  $('#area-label').textContent=s.missing?'未填写':s.area+' m²';
  $('#raw').textContent=(s.missing?'面积: null':s.area+' m²')+' / '+s.rooms+' 间 / '+s.district;
  const values=result.vector;
  if(!$('#vector').children.length)$('#vector').innerHTML=result.names.map((name,i)=>`<div class="feature"><strong id="value-${i}"></strong><span>${name}</span></div>`).join('');
  values.forEach((v,i)=>$('#value-'+i).textContent=fmt(v));
  // Both numerical scales use the same physical span. Min-max is affine,
  // so its relative carriage position stays aligned with the area carriage.
  // Extents include all valid new samples, not just training observations.
  targets=[(result.filledArea-20)/160*204,(result.scaledArea+.25)/2*204,
    ...result.oneHot.map(v=>v*24),(result.areaPerRoom-4)/176*204];
  $('[data-missing-flag]').setAttribute('opacity',s.missing?'1':'.3');
  explain();
  if(announce)$('#announcement').textContent='输出特征：'+values.map(fmt).join('，');
  if(reduced.matches){positions=targets.slice();draw();}else run();
}
function draw(){sliders.forEach((el,i)=>el.setAttribute('transform',translateAlong(projection,[positions[i],0,0])));}
function tick(now){
  frame=0;
  const dt=last?Math.min((now-last)/1000,1/30):1/60;last=now;
  if(tour&&!reduced.matches){elapsed+=dt;if(elapsed>9){elapsed=0;stage=(stage+1)%4;explain();}}
  positions=positions.map((p,i)=>Math.abs(targets[i]-p)<.015?targets[i]:p+(targets[i]-p)*(1-Math.exp(-dt/.2)));
  draw();
  if(visible&&!document.hidden&&!reduced.matches&&(tour||positions.some((p,i)=>p!==targets[i])))frame=requestAnimationFrame(tick);
}
function run(){if(!frame&&visible&&!document.hidden&&!reduced.matches){last=0;frame=requestAnimationFrame(tick);}}
function pause(){tour=false;elapsed=0;explain();}
for(const field of Object.values(fields))field.addEventListener('input',()=>{pause();update();});
tabs.forEach((t,i)=>t.addEventListener('click',()=>{stage=i;pause();}));
$('.iso-stage').addEventListener('keydown',e=>{if(e.key==='ArrowRight'||e.key==='ArrowLeft'){e.preventDefault();stage=(stage+(e.key==='ArrowRight'?1:3))%4;pause();}});
$('#tour').addEventListener('click',()=>{if(reduced.matches){stage=(stage+1)%4;tour=false;explain();return;}tour=!tour;elapsed=0;explain();run();});
document.querySelectorAll('[data-preset]').forEach(b=>b.addEventListener('click',()=>{
  const preset=b.dataset.preset;fields.area.value=preset==='large'?'180':'80';fields.missing.checked=preset==='missing';fields.rooms.value='2';fields.district.value='近郊';stage=preset==='large'?1:0;pause();update();
}));
$('#theme').addEventListener('click',()=>{const light=document.body.dataset.theme!=='light';document.body.dataset.theme=light?'light':'dark';$('#theme').textContent=light?'深色模式 ↗':'浅色模式 ↗';});
new IntersectionObserver(entries=>{visible=entries.at(-1).isIntersecting;if(!visible){cancelAnimationFrame(frame);frame=0;}else run();},{threshold:.05}).observe($('.iso-stage'));
document.addEventListener('visibilitychange',()=>{if(document.hidden){cancelAnimationFrame(frame);frame=0;}else run();});
reduced.addEventListener('change',()=>{if(reduced.matches){tour=false;cancelAnimationFrame(frame);frame=0;}update(false);});
update(false);
if(reduced.matches){$('#tour').textContent='下一步';}
// Read-only diagnostics for reproducible browser checks.
window.featureDemo={get state(){return {sample:sample(),result,stage,tour,visible,positions:[...positions],targets:[...targets],fitted};}};
