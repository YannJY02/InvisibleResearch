// Teaching examples only. No empirical data or fitted forest is used here.
export const names = ['A', 'B', 'C'];
export const orders = [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
export const background = Array.from({length:8}, (_,mask) => names.map((_,i) => mask & (1<<i) ? 1 : -1));
export const score = (x, interaction=6) => 10 + 4*x[0] - 2*x[1] + x[2] + interaction*x[0]*x[1];
export function coalition(x, mask, interaction=6) {
  return background.reduce((sum,row) => sum + score(row.map((v,i) => mask & (1<<i) ? x[i] : v), interaction),0)/8;
}
export function explain(x, interaction=6) {
  const values = Array.from({length:8},(_,mask) => coalition(x,mask,interaction));
  const marginal = orders.map(order => {
    let mask=0;
    const row=[0,0,0];
    for(const i of order) { const next=mask | (1<<i); row[i]=values[next]-values[mask]; mask=next; }
    return row;
  });
  return {base:values[0], prediction:values[7], values, marginal,
    phi:names.map((_,i) => marginal.reduce((sum,row) => sum+row[i],0)/6)};
}
export function importanceRound(round) {
  const i=round-1;
  const shadow=[2.2+(i%4)*.18, 2.5+((i*3)%5)*.12, 2.35+((i*7)%6)*.11];
  const max=Math.max(...shadow);
  const real=[5.2+(i%5)*.22, max + (i%2===0 ? .65 : -.45), .65+(i%4)*.17];
  return {real,shadow,max};
}
export function binomialTail(hits,n,upper) {
  let prob=2**(-n), total=0;
  for(let k=0;k<=n;k++) {if(upper ? k>=hits : k<=hits) total+=prob; prob*= (n-k)/(k+1);}
  return total;
}
export function boruta(round) {
  const hits=[0,0,0];
  for(let r=1;r<=round;r++) {
    const {real,max}=importanceRound(r);
    real.forEach((v,i) => {if(v>max) hits[i]++;});
  }
  const cutoff=.05/6;
  const status=hits.map(h => round<20 ? '积累证据' : binomialTail(h,20,true)<cutoff ? '确认相关' : binomialTail(h,20,false)<cutoff ? '拒绝' : '暂未确定');
  return {...importanceRound(round),hits,status,cutoff};
}
