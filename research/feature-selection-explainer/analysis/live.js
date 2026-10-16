const $=id=>document.getElementById(id);
const state={mode:'boruta',round:1,feature:0,x:[1,1,1],interaction:6};
const reduced=matchMedia('(prefers-reduced-motion: reduce)');
let touring=!reduced.matches, visible=false, frame=0, last=0, tourClock=0;
let targets=Array(7).fill(0), positions=[...targets], range=[0,7], current=null;
const cursors=[...document.querySelectorAll('[data-cursor]')];
const fmt=n=>(n>0?'+':'')+Number(n.toFixed(2));
const transform=x=>`translate(${motionAxis[0]*x} ${motionAxis[1]*x})`;
// Match the kit's projection directly; the vector is provided by build-time code.
const setTour=on=>{touring=on&&!reduced.matches;tourClock=0;$('tour').textContent=touring?'暂停演示':'播放演示';$('tour').disabled=reduced.matches;$('tour-note').textContent=reduced.matches?'已遵循减少动态效果设置。':'闲置演示仅在画面可见时运行；操作后暂停。';wake();};
const takeOver=()=>setTour(false);
function update(announce=false) {
  const b=state.mode==='boruta';
  $('mode-boruta').setAttribute('aria-pressed',String(b));$('mode-shap').setAttribute('aria-pressed',String(!b));
  $('boruta-controls').hidden=!b;$('shap-controls').hidden=b;
  $('round').value=state.round;$('round-value').textContent=`${state.round} / 20`;
  $('interaction-value').textContent=state.interaction;
  $('feature').value=state.feature;
  document.querySelectorAll('[data-input]').forEach(el=>{const i=+el.dataset.input;el.textContent=`${names[i]} = ${fmt(state.x[i])}`;el.setAttribute('aria-label',`${names[i]} 当前为 ${state.x[i]}，点击切换正负一`);});
  const shap=explain(state.x,state.interaction);
  $('equation').innerHTML=`${shap.base} ${shap.phi.map(v=>v<0?'− '+Math.abs(v):'+ '+v).join(' ')} = ${shap.prediction}<small>基线 + φA + φB + φC = 当前样本预测（分数）<br>当前 A=${fmt(state.x[0])}，B=${fmt(state.x[1])}，C=${fmt(state.x[2])}，λ=${state.interaction}</small>`;
  $('coalitions').innerHTML='<table class="comparison"><thead><tr><th>已揭示的变量 S</th><th>v(S)</th></tr></thead><tbody>'+shap.values.map((v,mask)=>`<tr><td>${names.filter((_,i)=>mask&(1<<i)).join('、')||'无（背景基线）'}</td><td>${v}</td></tr>`).join('')+'</tbody></table>';
  if(b) {
    current=boruta(state.round);range=[0,7];targets=[...current.real,...current.shadow,current.max];
    $('metric-label').textContent='高亮游标 / 本轮最强影子';
    $('caption').innerHTML='<strong>看相对位置：</strong>后排第 1–3 轨是原始 A/B/C，第 4–6 轨是影子。前排高亮游标在同一刻度上标记影子最大值；原始游标越过它，本轮才记一次命中。刻度沿各轨由左上向右下增大。';
    $('scale').innerHTML='<span>每轨左端：0</span><span>非负重要性</span><span>每轨右端：7</span>';
    $('lanes').innerHTML=[...names.map(n=>'原始 '+n),...names.map(n=>'影子 '+n)].map((n,i)=>`<li><span>${i+1} / ${n}</span><b data-value="${i}"></b></li>`).join('');
    $('detail').textContent='影子保留每列的取值分布，但打乱了样本对应关系。它们提供随机参照，不能当作新收集的变量。';
    $('statuses').innerHTML=names.map((n,i)=>`<div><span>${n} · ${current.hits[i]}/${state.round} 次命中</span><span class="tag">${current.status[i]}</span></div>`).join('');
  } else {
    current=shap;range=[-16,16];targets=[...shap.marginal.map(row=>row[state.feature]),shap.phi[state.feature]];
    $('metric-label').textContent=`高亮游标 / ${names[state.feature]} 的 SHAP（六种顺序平均）`;
    $('caption').innerHTML='<strong>看顺序差异：</strong>后排六轨分别显示所选特征在六种加入顺序中的边际贡献。前排高亮游标是它们的平均值。游标在零刻度两侧，分别表示拉低或推高预测。';
    $('scale').innerHTML='<span>每轨左端：−16</span><span>中点：0</span><span>每轨右端：+16</span>';
    $('lanes').innerHTML=orders.map((order,i)=>`<li><span>${i+1} / ${order.map(j=>j===state.feature?'<strong>'+names[j]+'</strong>':names[j]).join(' → ')}</span><b data-value="${i}"></b></li>`).join('');
    const order=orders[0], before=order.slice(0,order.indexOf(state.feature)).reduce((m,i)=>m|(1<<i),0),after=before|(1<<state.feature);
    $('detail').textContent=`以第 1 轨为例：加入 ${names[state.feature]} 前为 ${shap.values[before]}，加入后为 ${shap.values[after]}，边际贡献 ${fmt(shap.values[after]-shap.values[before])}。六条轨道都基于同一个固定模型。`;
    $('statuses').innerHTML=names.map((n,i)=>`<div><span>φ${n}</span><span class="mono">${fmt(shap.phi[i])}</span></div>`).join('');
  }
  // On a mode change, measurements have different units: initialize the new scale.
  if(reduced.matches) positions=[...targets];
  render();wake();
  if(announce)$('announcement').textContent=b?`Boruta 第 ${state.round} 轮。${current.status.join('，')}`:`观察 ${names[state.feature]}，SHAP 为 ${shap.phi[state.feature]}，预测 ${shap.prediction}`;
}
function render() {
  const b=state.mode==='boruta';
  positions.forEach((v,i)=>{
    const x=-travel+(v-range[0])/(range[1]-range[0])*travel*2;
    cursors[i].setAttribute('transform',transform(x));
    const value=document.querySelector(`[data-value="${i}"]`);
    if(value)value.textContent=b?targets[i].toFixed(2):fmt(targets[i]);
  });
  const moving=positions.some((v,i)=>Math.abs(v-targets[i])>.005);
  // Statistical outputs are exact targets, never animation-interpolated values.
  $('metric').textContent=b?targets[6].toFixed(2):fmt(targets[6]);
  const readout=document.querySelector('[data-readout]');
  readout.textContent=moving?`定位中 · 尺上 ${fmt(positions[6])}`:(b?`影子最大值 ${targets[6].toFixed(2)}`:`φ${names[state.feature]} = ${fmt(targets[6])}`);
  document.querySelector('.iso-stage').setAttribute('aria-label',b?`第 ${state.round} 轮。影子最大值 ${targets[6].toFixed(2)}。方向键切换轮次。`:`特征 ${names[state.feature]}，六种顺序平均贡献 ${fmt(targets[6])}。方向键切换特征。`);
}
function tick(now) {
  frame=0;
  if(!visible||document.hidden||reduced.matches){last=0;return;}
  const dt=last?Math.min((now-last)/1000,.05):0;last=now;
  const alpha=1-Math.exp(-dt/0.24);
  positions=positions.map((v,i)=>Math.abs(v-targets[i])<.0001?targets[i]:v+(targets[i]-v)*alpha);
  tourClock+=dt;
  if(touring&&tourClock>4){tourClock=0;if(state.mode==='boruta')state.round=state.round%20+1;else state.feature=(state.feature+1)%3;update();}
  render();
  if(touring||positions.some((v,i)=>Math.abs(v-targets[i])>.0001))wake();else last=0;
}
function wake(){if(!frame&&visible&&!document.hidden&&!reduced.matches)frame=requestAnimationFrame(tick);}
for(const mode of ['boruta','shap']) $('mode-'+mode).addEventListener('click',()=>{takeOver();state.mode=mode;update(true);positions=[...targets];render();});
$('round').addEventListener('input',e=>{takeOver();state.round=+e.target.value;update();});
$('round').addEventListener('change',()=>update(true));
$('next').addEventListener('click',()=>{takeOver();state.round=Math.min(20,state.round+1);update(true);});
$('finish').addEventListener('click',()=>{takeOver();state.round=20;update(true);});
$('reset').addEventListener('click',()=>{takeOver();state.round=1;update(true);});
$('feature').addEventListener('change',e=>{takeOver();state.feature=+e.target.value;update(true);});
$('interaction').addEventListener('input',e=>{takeOver();state.interaction=+e.target.value;update();});
$('interaction').addEventListener('change',()=>update(true));
document.querySelectorAll('[data-input]').forEach(el=>el.addEventListener('click',()=>{takeOver();state.x[+el.dataset.input]*=-1;update(true);}));
$('tour').addEventListener('click',()=>setTour(!touring));
$('theme').addEventListener('click',()=>{document.body.dataset.theme=document.body.dataset.theme==='light'?'dark':'light';});
document.querySelector('.iso-stage').addEventListener('keydown',e=>{
  if(e.key===' '){e.preventDefault();setTour(!touring);return;}
  if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;
  e.preventDefault();takeOver();const step=e.key==='ArrowLeft'?-1:1;
  if(state.mode==='boruta')state.round=e.key==='Home'?1:e.key==='End'?20:Math.max(1,Math.min(20,state.round+step));
  else state.feature=e.key==='Home'?0:e.key==='End'?2:(state.feature+step+3)%3;
  update(true);
});
document.querySelector('.iso-stage').addEventListener('pointerdown',takeOver);
document.querySelector('.iso-stage').addEventListener('focus',()=>{$('announcement').textContent=document.querySelector('.iso-stage').getAttribute('aria-label');});
new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;if(!visible){if(frame)cancelAnimationFrame(frame);frame=0;last=0;}else wake();},{threshold:.1}).observe(document.querySelector('.iso-plate'));
document.addEventListener('visibilitychange',()=>{last=0;if(document.hidden){cancelAnimationFrame(frame);frame=0;}else wake();});
reduced.addEventListener('change',()=>{setTour(false);if(reduced.matches){positions=[...targets];render();}else wake();});
update();positions=[...targets];render();setTour(touring);
