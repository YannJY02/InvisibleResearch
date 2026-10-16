import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {join,dirname} from 'node:path';
import {ISO_CSS,plateHtml,axisVector} from './vendor/iso-kit.mjs';
import {instrument,projection,travel} from './geometry.mjs';
const here=dirname(fileURLToPath(import.meta.url));
const out=join(here,'../artifacts/anatomy');
mkdirSync(out,{recursive:true});
const light=process.argv.includes('--light');
const model=readFileSync(join(here,'model.mjs'),'utf8').replaceAll('export ','');
const live=readFileSync(join(here,'live.js'),'utf8');
const style=readFileSync(join(here,'style.css'),'utf8');
const license=readFileSync(join(here,'vendor/LICENSE'),'utf8');
const plate=plateHtml({fig:'FIG 01 / 06 TRACKS',title:'六轨比较尺',hint:'后排 1—6 轨 · 前排高亮为汇总',readout:'',body:`<div class="iso-stage" tabindex="0" role="group" aria-label="机械比较尺。左右方向键切换轮次或待解释特征，空格暂停演示。">${instrument()}</div>`});
const html=`<!doctype html>\n<!-- Anatomy drawing kit license:\n${license}\n-->
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Boruta / SHAP · 变量筛选与预测归因</title><style>${ISO_CSS}\n${style}</style></head>
<body class="iso" data-theme="${light?'light':'dark'}"><main>
<nav class="topbar" aria-label="页面工具"><span>METHOD LAB / 方法解剖室</span><button id="theme" type="button">切换明暗</button></nav>
<header><div class="eyebrow">SELECTION & ATTRIBUTION</div><h1>哪些变量值得留下？<br>这次预测，又由谁推动？</h1><p>Boruta 寻找超过随机参照的特征；SHAP 分配模型预测相对基线的差额。操作同一台比较尺，理解两个不同的问题。</p></header>
<div class="switches" role="group" aria-label="选择方法"><button id="mode-boruta" aria-pressed="true">01 / Boruta · 筛选变量</button><button id="mode-shap" aria-pressed="false">02 / SHAP · 分解预测</button></div>
<section class="workbench" aria-label="交互仪器">
<div class="figure-wrap">${plate}<div class="scale" id="scale" aria-hidden="true"></div><p class="caption" id="caption"></p><div class="tours"><span id="tour-note">闲置时自动演示；操作后暂停。</span><button id="tour" type="button">暂停演示</button></div></div>
<aside class="aside">
<div id="boruta-controls"><div class="eyebrow">SHADOW BENCHMARK</div><h2>先和“打乱版的自己”比一比</h2><p>每轮将各列单独打乱，破坏它与结果的对应关系，再一起建模。本页回放预设的重要性分数，让判断过程可见。</p><label for="round">当前轮次 <output id="round-value">1 / 20</output></label><input id="round" type="range" min="1" max="20" value="1"><div class="controls"><button id="next">下一轮</button><button id="finish">看 20 轮结果</button><button id="reset">重置</button></div><p class="note">单轮超过影子最大值，只记一次“命中”；本教学示例到第 20 轮才作检验。</p></div>
<div id="shap-controls" hidden><div class="eyebrow">ALL POSSIBLE ORDERS</div><h2>换一种加入顺序，贡献会变吗？</h2><p>六条轨道对应 A、B、C 的全部加入顺序。每条轨道显示所选特征在该顺序下的边际贡献，高亮游标显示平均值。</p><div class="controls"><label for="feature">观察特征</label><select id="feature"><option value="0">A</option><option value="1">B</option><option value="2">C</option></select></div><div class="chip-controls" aria-label="当前样本"><button data-input="0">A = +1</button><button data-input="1">B = +1</button><button data-input="2">C = +1</button></div><div class="controls"><label for="interaction">交互强度 λ = <output id="interaction-value">6</output></label><input id="interaction" type="range" min="0" max="12" step="1" value="6"></div><p class="note">试试选 B，再把 λ 从 6 拉到 0：模型中的 B 主项为 −2，但它分到交互贡献后，SHAP 可以为正。</p></div>
<div class="big-readout mono" id="metric"></div><p id="metric-label"></p><ol class="lane-list" id="lanes"></ol><div id="detail" class="track-detail"></div><div id="statuses" class="status-list"></div>
</aside></section>
<div class="sr-only" id="announcement" aria-live="polite"></div>
<section class="below">
<article class="lesson" id="boruta-lesson"><div class="eyebrow">01 / WHAT SURVIVES RANDOMNESS</div><h2>Boruta：相关，不等于“最精简”</h2><ol><li><strong>造一个随机参照。</strong>保留一列取值，却打乱它与样本的对应关系，得到影子特征。</li><li><strong>同场测重要性。</strong>原始特征和影子一起进入模型；每轮以最强影子为门槛。原始 Boruta 使用随机森林的重要性度量。</li><li><strong>跨多轮收集证据。</strong>确认、拒绝或继续待定；一次赢过门槛不足以确认。其目标是保留所有相关特征，不是找出最小变量集。</li></ol><p>这里的 A/B/C 仅是三条教学测量通道，和 SHAP 模式的小模型没有拟合关系。分数大小随模型及度量变化，没有跨项目通用的“3 分门槛”。</p><details><summary>示例的检验规则与简化</summary><p>20 轮固定测量；命中数 H 按 Binomial(20, 0.5) 的上下尾计算，分别比较 0.05 / (2 × 3)。0.5 是此类检验的设定，不能解释为随机变量击败多个影子最大值的天然概率。图中三条影子是简化展示；实际算法可能生成更多影子，并逐轮检验、剔除拒绝变量，校正方式依实现而异。本页不运行随机森林，也不复刻完整 Boruta。</p></details></article>
<article class="lesson"><div class="eyebrow">02 / HOW CREDIT IS SHARED</div><h2>SHAP：先看顺序，再取平均</h2><p>模型固定为 <strong>f = 10 + 4A − 2B + C + λAB</strong>。背景是 A/B/C 各以相同概率取 −1 或 +1 的八种组合。暂未揭示的变量按这八行取平均，而不是填 0 或重新训练模型。</p><div class="equation mono" id="equation"></div><p>在默认样本中，B 先加入时贡献 −2；A 已加入后，B 贡献 +4。六种顺序平均后，B 的 SHAP 为 +1。交互项的贡献由 A、B 分摊。</p><details><summary>展开当前样本的全部联盟值 v(S)</summary><div id="coalitions" class="scroll-table"></div></details><p>显示单位为<strong>教学模型分数</strong>。实际任务必须注明解释的是回归值、概率还是 log-odds；基线与贡献必须使用同一尺度。</p></article>
<article class="lesson wide"><div class="eyebrow">03 / SAME WORD, DIFFERENT QUESTIONS</div><h2>“重要”需要先说明：对什么重要？</h2><div class="scroll-table"><table class="comparison"><thead><tr><th>方法</th><th>回答的问题</th><th>结果怎样读</th></tr></thead><tbody><tr><th>Boruta</th><td>特征能否持续超过随机参照？</td><td>确认 / 拒绝 / 待定；结果依赖数据、学习器与重要性度量。</td></tr><tr><th>局部 SHAP</th><td>这一个样本的预测差额怎样分配？</td><td>正值推高、负值拉低相对基线的预测；不表示现实世界的因果效应。</td></tr><tr><th>全局 SHAP 汇总</th><td>在指定样本群体中，归因幅度一般有多大？</td><td>常用 mean(|SHAP|)；绝对值丢失方向，不是显著性检验。</td></tr><tr><th>BorutaSHAP</th><td>若以汇总 SHAP 作重要性，哪些特征能超过影子？</td><td>结合筛选框架与归因度量；检验、阈值和抽样须看具体实现。</td></tr></tbody></table></div></article>
<article class="lesson"><h3>相关变量，是理解两者的关键边界</h3><p>两列携带相近信息时，重要性可能分摊或竞争；不能把一个较小的数直接读成“这列没价值”。SHAP 的背景选择、条件式或干预式缺失处理也会改变归因。本例特意使用独立变量，让计算能完全看清。</p></article>
<article class="lesson"><h3>放回研究流程中</h3><p>若研究期刊被某索引收录的预测：Boruta 可用于训练数据内的候选变量筛选；SHAP 可解释已训练模型对某本期刊的预测。筛选应放在交叉验证的训练折内，性能用未参与筛选的数据评价。解释模型学到了什么，仍需与收录机制的因果解释区分。</p></article>
</section>
<footer><strong>依据与复算</strong><p>本页是方法教学，未使用项目期刊数据。Boruta 是预设测量回放；SHAP 是对明确小模型的精确枚举。查看源代码可复算每个读数。</p><ol><li>Kursa & Rudnicki (2010). <a href="https://www.jstatsoft.org/article/view/v036i11">Feature Selection with the Boruta Package</a>, §2.</li><li>Lundberg & Lee (2017). <a href="https://arxiv.org/abs/1705.07874">A Unified Approach to Interpreting Model Predictions</a>, §2–4.</li><li>SHAP 官方：<a href="https://shap.readthedocs.io/en/latest/example_notebooks/overviews/An%20introduction%20to%20explainable%20AI%20with%20Shapley%20values.html">背景、可加性与相关特征</a>；<a href="https://shap.readthedocs.io/en/latest/example_notebooks/overviews/Be%20careful%20when%20interpreting%20predictive%20models%20in%20search%20of%20causal%20insights.html">预测归因与因果解释</a>。</li><li><a href="https://github.com/Ekeany/Boruta-Shap">BorutaShap 项目</a>（结合方法的实现示例）。</li></ol><p>2026-10-16 · Anatomy SVG kit © 2026 Ryan, MIT · 图形由 66 个实体零件构成 · 可离线使用</p></footer>
</main><script type="module">${model}\nconst motionAxis=${JSON.stringify(axisVector(projection,[1,0,0]))}, travel=${travel};\n${live}</script></body></html>`;
const path=join(out,light?'index-light.html':'index.html');
writeFileSync(path,html);
console.log(path);
