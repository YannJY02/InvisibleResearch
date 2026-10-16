// All machine bodies are bevelled rectangular solids; no hidden wireframes.
export function machine(k) {
  const bed = { x: -139, y: -96, w: 278, d: 192, r: 1.5 };
  const P = k.fitProjection(k.boxCorners(bed, -16, 30), 760, 480,
    { pad: 63, azimuth: 56, elevation: 42 });
  const at = (v) => k.iso(v, P);
  const L = (d, tone = 'lo') => k.lineSvg(d, { tone });
  const screw = (x, y, z) => L(k.planOutline({ x:x-1.1, y:y-1.1, w:2.2, d:2.2, r:.3 },z,P)) +
    k.dotsSvg([at([x,y,z])], {size:.45,tone:'mid'});
  let count = 0;
  const slab = (x,y,w,d,z,h,tone='mid',extra='') => {
    count++;
    const plan = {x,y,w,d,r:Math.min(1.5,w/6,d/6)};
    return k.solidSvg(k.slabOf(plan,z,h,P,4,Math.min(.6,h/4)), {tone,inner:extra});
  };
  const outline = (x,y,w,d,z,tone='faint') => L(k.planOutline({x,y,w,d,r:.7},z,P),tone);
  const rule = (y, z, first=-111, last=111, step=6) => {
    let s='';
    // Closed engraved slots have actual boundaries, unlike floating line ends.
    for(let x=first,i=0;x<=last;x+=step,i++)
      s+=outline(x,y,.5,i%5===0?5:2.5,z,i%5===0?'mid':'lo');
    return s;
  };
  let body = `<path class="iso-halo" d="${k.haloOf(bed,-16,12,P)}"/>`;
  const feet=k.corners(bed,17).sort((a,b)=>k.depthOf([...a,0],P)-k.depthOf([...b,0],P));
  for(const [x,y] of feet) {
    body+=slab(x-7,y-7,14,14,-16,4,'lo');
    body+=slab(x-9,y-9,18,18,-12,4,'lo');
  }
  body+=slab(-139,-96,278,192,-8,8,'lo',L(k.sideSeam(bed,-4,P,4),'faint'));
  body+=slab(-136,-93,272,186,0,2,'lo');
  body+=outline(-132,-89,264,178,2);
  for(const [x,y] of k.corners(bed,9))body+=screw(x,y,2);
  body+=slab(-126,-89,50,9,2,.7,'lo');
  body+=k.faceTextSvg(k.topMatrix([-101,-85],2.7,P),'FEATURE / 01',{size:2.2,tone:'mid',anchor:'middle'});
  body+=slab(-135,-80,4,160,2,4,'lo')+slab(131,-80,4,160,2,4,'lo');
  const starts=[-76,-35,6,47];
  const slider = (id,x,y,w,d,stage) => {
    let s=slab(x,y,w,d,8,3,'hi');
    s+=slab(x+2,y+1,3,d-2,11,1,'mid');
    s+=slab(x+w-5,y+1,3,d-2,11,1,'mid');
    s+=slab(x+w/2-2,y+2,4,d-4,11,5,'hi');
    for(let v=y+3;v<y+d-2;v+=2)s+=outline(x+w/2-1.4,v,2.8,.35,16,'lo');
    s+=screw(x+3.5,y+d/2,12)+screw(x+w-3.5,y+d/2,12);
    return `<g data-slider="${id}" data-stage-part="${stage}">${s}</g>`;
  };
  starts.forEach((y,i)=>{
    let s=slab(-126,y,252,33,2,3,'mid');
    s+=outline(-122,y+2,244,29,5);
    s+=slab(-116,y+5,232,3,5,3,'mid');
    s+=slab(-116,y+21,232,3,5,3,'mid');
    s+=slab(-123,y+4,6,21,5,8,'mid');
    s+=slab(117,y+4,6,21,5,8,'mid');
    s+=slab(-115,y+26,230,5.5,5,.5,'lo');
    s+=rule(y+26,5.5);
    for(const x of [-120,120])s+=screw(x,y+7,13)+screw(x,y+22,13);
    if(i===2){
      // Three independent binary switches: each travels 24 units on its track.
      for(let n=0;n<3;n++){
        const x=-106+n*78;
        s+=slab(x-3,y+9,3,11,5,3,'lo')+slab(x+49,y+9,3,11,5,3,'lo');
        s+=outline(x+2,y+12,4,4,5,'mid')+outline(x+42,y+12,4,4,5,'hi');
        s+=slider(`category-${n}`,x+6,y+5,18,19,i);
      }
    }else{
      // Centre marks: imputation median, scaled zero, ratio minimum.
      const ref=i===0?-25.5:i===1?-76.5:-102;
      s+=slab(ref-.7,y+24,1.4,7.5,5.5,.5,'hi');
      s+=slider(['fill','scale','','ratio'][i],-111,y+5,18,19,i);
    }
    body+=`<g data-bank="${i}">${s}</g>`;
  });
  body+=slab(90,-89,29,8,2,1,'lo');
  body+=`<g data-missing-flag>${outline(93,-87,10,4,3,'hi')}${outline(106,-87,10,4,3,'lo')}</g>`;
  return {P,count,svg:k.figureSvg({width:760,height:480,
    label:'四联机械计算尺。四排依次显示填补后的面积、缩放后的面积、三个地区开关和每间房面积。滑块位置与下方公式使用同一计算模型。',body})};
}
