import assert from 'node:assert/strict';
import {background,explain,score,boruta,binomialTail} from './model.mjs';
assert.deepEqual(explain([1,1,1]).phi,[7,1,1]);
assert.deepEqual(explain([1,1,1]).values,[10,14,8,18,11,15,9,19]);
for(const x of background) for(const interaction of [0,3,6,9,12]) {
  const result=explain(x,interaction);
  assert.equal(result.base+result.phi.reduce((a,b)=>a+b,0),score(x,interaction));
  // Independent analytic solution, valid only for this independent ±1 background.
  assert.deepEqual(result.phi,[4*x[0]+interaction*x[0]*x[1]/2,-2*x[1]+interaction*x[0]*x[1]/2,x[2]]);
  for(const row of result.marginal) assert.equal(row.reduce((a,b)=>a+b,0),result.prediction-result.base);
}
assert.ok(Math.abs(binomialTail(20,20,true)-2**-20)<1e-15);
assert.equal(binomialTail(0,20,false),2**-20);
assert.deepEqual(boruta(20).hits,[20,10,0]);
assert.deepEqual(boruta(20).status,['确认相关','暂未确定','拒绝']);
assert.deepEqual(boruta(19).status,['积累证据','积累证据','积累证据']);
console.log('PASS: 40 exact SHAP cases, all coalition paths, binomial tails and fixed-horizon decisions');
