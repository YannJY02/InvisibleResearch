import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {homedir} from 'node:os';
import {dirname,join,resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {machine} from './geometry.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const skill=resolve(process.env.ANATOMY_HOME||join(homedir(),'.agents/skills/anatomy'));
const k=await import(pathToFileURL(join(skill,'kit/iso-kit.mjs')));
const {kitScript}=await import(pathToFileURL(join(skill,'scripts/inline-kit.mjs')));
const {svg,P,count}=machine(k);
const light=process.argv.includes('--light');
const out=join(here,'artifacts/interactive');
mkdirSync(out,{recursive:true});
const stages=['填补缺失','统一尺度','编码类别','构造特征'];
const body=`
<main>
<header><div class="eyebrow">THE FEATURE WORKSHOP <span>交互笔记 / 01</span></div>
<div class="headline"><h1>模型看到的，<br>是你选择的表达。</h1><button id="theme" class="quiet" aria-label="切换深浅主题">${light?'深色':'浅色'}模式 ↗</button></div>
<p class="intro">特征工程，就是把原始记录转成模型可用的表达。<br class="desktop">试着改一套房屋的信息，看同一条记录如何变成七个数。</p></header>
<section class="workshop" aria-label="特征工程工作台">
<div class="instrument"><div class="iso-plate">
<div class="corners"><span>FIG. 01</span><span>特征计算尺</span></div>
<div class="iso-stage" tabindex="0" aria-label="计算尺，可用左右方向键切换解释步骤">${svg}</div>
<div class="corners bottom"><span>后排 → 前排，与步骤 01—04 对应</span><output data-readout>训练尺已锁定</output></div>
</div><div class="machine-caption"><span class="dot"></span><span>亮起的滑块对应当前解释；位置来自真实计算。</span><button id="tour" aria-pressed="true">暂停导览</button></div></div>
<aside class="sample"><div class="small-heading">输入一条新样本 <span>合成数据</span></div>
<label class="range-label" for="area">面积 <output id="area-label">80 m²</output></label>
<input id="area" type="range" min="20" max="180" step="1" value="80" aria-describedby="area-help">
<div class="range-ends" id="area-help"><span>20 m²</span><span>180 m²</span></div>
<label class="check"><input type="checkbox" id="missing">这条记录没有填写面积</label>
<div class="field-row"><label for="rooms">房间数</label><select id="rooms">${[1,2,3,4,5].map(n=>`<option value="${n}" ${n===2?'selected':''}>${n} 间</option>`).join('')}</select></div>
<div class="field-row"><label for="district">地区</label><select id="district">${['中心','近郊','远郊'].map(n=>`<option ${n==='近郊'?'selected':''}>${n}</option>`).join('')}</select></div>
<div class="presets"><button data-preset="missing">试试缺失值</button><button data-preset="large">试试超大房屋</button><button data-preset="reset">重置</button></div>
<div class="raw"><span>原始记录</span><code id="raw"></code></div>
</aside></section>
<nav class="steps" aria-label="选择要理解的转换">${stages.map((s,i)=>`<button data-step="${i}" aria-pressed="${i===0}"><span>0${i+1}</span>${s}</button>`).join('')}</nav>
<section class="explanation" aria-labelledby="explain-title"><div><span id="explain-kicker" class="eyebrow"></span><h2 id="explain-title"></h2><p id="explain-copy"></p></div><div class="equation"><output id="formula"></output><p id="formula-note"></p></div></section>
<section class="result" aria-labelledby="result-title"><div class="result-heading"><h2 id="result-title">这一条记录，最终变成</h2><span>1 个样本 × 7 个特征</span></div><div id="vector" class="vector"></div><p class="result-note">这是一份特征拼接示例，不是房价预测。为了看清每种转换，这里只缩放面积；对尺度敏感的模型，其他数值列也可能需要缩放。</p><p id="announcement" class="sr-only" aria-live="polite"></p></section>
<details class="training"><summary>这把尺子是怎么校准的？ <span>训练数据、公式与边界</span></summary><div class="training-body">
<div><h3>先划分数据，再学习规则</h3><p>五条合成训练记录的面积为 40、60、80、100、120 m²，因此中位数为 80，最小值为 40，最大值为 120。地区词表顺序固定为：中心、近郊、远郊。</p><p>你调整的是一条新样本，不能参与重新计算这些参数。把测试集也用于填补、缩放或特征选择，会把测试信息泄漏到训练过程；交叉验证时，每一折也应只用该折的训练部分拟合。</p></div>
<div><h3>表达方式要为任务服务</h3><p>填补值是估计，不是找回事实。独热编码不强加类别之间的大小关系。比值特征把已有信息换一种表达，并不创造新的观测信息。</p><p>特征工程还包括文本与日期特征、交互项、变换和特征选择；这四步只是入口。更多特征不一定更好，是否保留应由领域含义和独立验证决定。若目标是房价，成交后才知道的信息不能作为预测时可用的输入。</p></div></div></details>
<footer><span>合成房屋 · 可复算演示 · Anatomy SVG</span><div>原理参考：<a href="https://scikit-learn.org/stable/modules/preprocessing.html">预处理</a> / <a href="https://scikit-learn.org/stable/modules/impute.html">缺失值</a> / <a href="https://scikit-learn.org/stable/common_pitfalls.html#data-leakage">数据泄漏</a></div></footer>
</main>`;
const style=readFileSync(join(here,'style.css'),'utf8');
const model=readFileSync(join(here,'model.mjs'),'utf8').replace(/^export /gm,'');
const runtime=readFileSync(join(here,'live.mjs'),'utf8');
// The kit contains its own HTML builder; escape embedded closing script tags.
const license=readFileSync(join(skill,'LICENSE'),'utf8');
const script=`/* Anatomy kit — ${license.replace(/\*\//g,'* /')} */\n${kitScript()}\n{\n${model}\nconst projection=${JSON.stringify(P)};\n${runtime}\n}`.replace(/<\/(script)/gi,'<\\/$1');
const html=`<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>特征工程 · 交互计算尺</title><style>${k.ISO_CSS}\n${style}</style></head><body class="iso" data-theme="${light?'light':'dark'}">${body}<script type="module">${script}</script></body></html>`;
const file=join(out,light?'index-light.html':'index.html');
writeFileSync(file,html);
console.log(`${file}\n${count} structural solids; self-contained HTML`);
