/* 重读报：公式渲染、分栏翻页、右栏定理全文、自测与进度。纯前端，进度只在本机 localStorage */
(function(){
const store={
  get(k,d){try{const v=localStorage.getItem('cd_'+k);return v==null?d:JSON.parse(v)}catch(e){return d}},
  set(k,v){try{localStorage.setItem('cd_'+k,JSON.stringify(v))}catch(e){}}
};
window.CDStore=store;
function renderMath(root){
  (root||document).querySelectorAll('.m,.M').forEach(el=>{
    if(el.dataset.ok)return;
    try{katex.render(el.textContent,el,{displayMode:el.classList.contains('M'),throwOnError:true,strict:false,output:'html',trust:false})}
    catch(e){el.classList.add('texerr');el.style.color='red';console.error('TEX',el.textContent,e.message)}
    el.dataset.ok=1;
  });
}
/* 长公式：先按栏宽缩小，缩到 .8 还放不下就在关系符处折行；超宽行内公式同样缩小 */
function fitMath(root,colW){
  (root||document).querySelectorAll('.M').forEach(el=>{
    const k=el.querySelector('.katex');if(!k)return;
    k.style.fontSize='';el.classList.remove('wrap');
    const cw=el.clientWidth;if(!cw)return;
    const sw=el.scrollWidth;
    if(sw>cw+1){
      const base=parseFloat(getComputedStyle(k).fontSize),ratio=cw/sw*.985;
      if(ratio>=.8)k.style.fontSize=base*ratio+'px';
      else{k.style.fontSize=base*.8+'px';if(el.scrollWidth>cw+1)el.classList.add('wrap')}
    }
  });
  if(colW)(root||document).querySelectorAll('.m').forEach(el=>{
    const k=el.querySelector('.katex');if(!k)return;
    k.style.fontSize='';
    const w=el.getBoundingClientRect().width;
    if(w>colW-30){const base=parseFloat(getComputedStyle(k).fontSize);k.style.fontSize=Math.max(base*.72,base*(colW-34)/w)+'px'}
  });
}
window.CDRender=renderMath;window.CDFit=fitMath;
const theme=store.get('theme','');
if(theme)document.documentElement.dataset.theme=theme;
function toggleNight(){
  const r=document.documentElement;
  if(r.dataset.theme==='night'){delete r.dataset.theme;store.set('theme','')}
  else{r.dataset.theme='night';store.set('theme','night')}
}
window.CDNight=toggleNight;

/* 自测：记录形如 {id:{ok:0|1,t:时间,n:做过次数}} */
function bindRecall(root){
  root.addEventListener('click',e=>{
    const a=e.target.closest('.rq-a');
    if(a){a.closest('.rq').classList.add('open');return}
    const b=e.target.closest('.rq-b button');
    if(b){
      const rq=b.closest('.rq');
      rq.querySelectorAll('button').forEach(x=>x.classList.remove('sel'));
      b.classList.add('sel');
      const rec=store.get('recall',{}),id=rq.dataset.q,o=rec[id]||{n:0};
      o.ok=+b.dataset.v;o.t=Date.now();o.n=(o.n||0)+1;rec[id]=o;store.set('recall',rec);
    }
  });
}
window.CDBindRecall=bindRecall;

if(!document.body.classList.contains('issue'))return;

const no=+document.body.dataset.no,D=window.CD;
const $=id=>document.getElementById(id);
const sheet=$('sheet'),cover=$('cover'),stage=$('stage'),vp=$('vp'),flow=$('flow'),sent=$('sent'),rail=$('railc');
let page=0,pages=1,step=0,busy=false;
const POS='pos'+no;

/* 头版：从上期和更早挑三道，答错过的优先 */
function prevQs(){
  const rec=store.get('recall',{});
  const pool=D.recall.filter(r=>r.no<no);
  const box=$('prevq');
  if(!pool.length){box.innerHTML='<p class="hint">这是第一期，没有旧账。从这里开始，每期开头都要先答三道前面的题：记不住的毛病，靠这三道治。</p>';return}
  const score=r=>{const o=rec[r.id];let s=0;if(o&&o.ok===0)s+=100;if(!o)s+=20;s+=(r.no===no-1)?30:Math.max(0,10-(no-r.no));if(o&&o.ok===1)s-=30;return s+((r.no*7+no*13+r.id.length)%5)};
  const pick=pool.slice().sort((a,b)=>score(b)-score(a)).slice(0,3);
  box.innerHTML=pick.map(r=>`<div class="rq" data-q="${r.id}"><p class="rq-q">${r.q}</p><p class="rq-a">${r.a}</p><div class="rq-b"><button data-v="1">答对了</button><button data-v="0">没答上</button></div></div>`).join('');
  renderMath(box);
}

function layout(){
  const W=vp.clientWidth,H=vp.clientHeight;
  if(!W)return;
  const cols=W>=1120?3:W>=640?2:1,gap=cols>1?30:0;
  flow.style.width=W+'px';
  flow.style.columnCount=cols;
  flow.style.columnGap=gap+'px';
  flow.style.columnRuleStyle=cols>1?'solid':'none';
  step=W+gap;
  fitMath(flow,(W-gap*(cols-1))/cols);
  const left=flow.getBoundingClientRect().left;
  const tr=flow.style.transform;flow.style.transform='none';
  const fl=flow.getBoundingClientRect().left;
  const r=sent.getBoundingClientRect();
  const fp=Math.floor((r.left-fl+1)/step)+1;
  flow.style.transform=tr;
  pages=fp+1; // 0 = 头版
}

function firstVisible(){
  const kids=flow.querySelectorAll('p,h2,h3,.M,.thm,.ex,figure,.tab,li');
  const b=vp.getBoundingClientRect();
  for(const k of kids){const r=k.getBoundingClientRect();if(r.left>=b.left-2&&r.left<b.right)return k}
  return null;
}
function pageOf(el){
  const tr=flow.style.transform;flow.style.transform='none';
  const fl=flow.getBoundingClientRect().left,x=el.getBoundingClientRect().left;
  flow.style.transform=tr;
  return Math.floor((x-fl+1)/step)+1;
}
function citedHere(){
  const b=vp.getBoundingClientRect(),ids=[];
  flow.querySelectorAll('a.c').forEach(a=>{
    const r=a.getBoundingClientRect();
    if(r.left>=b.left-2&&r.right<=b.right+2&&!ids.includes(a.dataset.t))ids.push(a.dataset.t);
  });
  return ids;
}
function thmCard(id){
  const t=D.thm[id];if(!t)return'';
  const where=t.no===no?'本期':`<a href="q${String(t.no).padStart(2,'0')}.html">第${t.no}期</a>`;
  return `<div class="rcard" data-id="${id}"><h5>${t.name}<span>${t.lab} · ${where}</span></h5>${t.html}</div>`;
}
function updateRail(){
  const ids=page>0?citedHere():[];
  rail.innerHTML=ids.length?ids.map(thmCard).join(''):`<p class="rail-empty">${page>0?'本版没有引用前面的定理。文中蓝色虚线的名称，点一下这里就显示全文。':''}</p>`;
  renderMath(rail);fitMath(rail);
  const n=$('railn');if(n)n.textContent=ids.length||'';
}
function apply(p){
  page=Math.max(0,Math.min(p,pages-1));
  cover.hidden=page!==0;
  stage.hidden=page===0;
  if(page>0){
    flow.style.transform=`translate3d(${-(page-1)*step}px,0,0)`;
    updateRail();
  }
  $('pgt').textContent=page===0?`头版 · 共 ${pages} 版`:`第 ${page+1} 版 / 共 ${pages} 版`;
  $('pgb').style.width=(100*(page+1)/pages)+'%';
  store.set(POS,page);
  if(page===pages-1){const rd=store.get('read',{});if(!rd[no]){rd[no]=Date.now();store.set('read',rd)}}
  store.set('last',no);
  try{history.replaceState(null,'','#p'+(page+1))}catch(e){}
}
function flip(to){
  if(busy)return;
  if(to<0){location.href=document.body.dataset.prev;return}
  if(to>=pages){location.href=document.body.dataset.next;return}
  if(to===page)return;
  const reduce=matchMedia('(prefers-reduced-motion:reduce)').matches;
  if(reduce){apply(to);return}
  busy=true;
  const old=document.createElement('div');old.className='leaf';
  [cover,stage].forEach(n=>{if(!n.hidden)old.appendChild(n.cloneNode(true))});
  old.querySelectorAll('[id]').forEach(n=>n.removeAttribute('id'));
  const f=to>page;
  apply(to);
  if(f){
    sheet.appendChild(old);
    old.style.animation='turnOut .42s cubic-bezier(.45,.05,.55,.95) forwards';
    old.addEventListener('animationend',()=>{old.remove();busy=false},{once:true});
  }else{
    const nw=old.cloneNode(false);
    [cover,stage].forEach(n=>{if(!n.hidden){const c=n.cloneNode(true);c.querySelectorAll('[id]').forEach(x=>x.removeAttribute('id'));c.removeAttribute('id');nw.appendChild(c)}});
    old.style.cssText='z-index:2;box-shadow:none';
    sheet.appendChild(old);sheet.appendChild(nw);
    nw.style.animation='turnIn .42s cubic-bezier(.45,.05,.55,.95) forwards';
    nw.addEventListener('animationend',()=>{old.remove();nw.remove();busy=false},{once:true});
  }
}
const next=()=>flip(page+1),prev=()=>flip(page-1);
$('nx').onclick=next;$('pv').onclick=prev;
function jumpTo(el){const p=pageOf(el);apply(p)}

/* 键盘 / 点边缘 / 滑动 */
addEventListener('keydown',e=>{
  if(e.metaKey||e.ctrlKey||e.altKey)return;
  if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();next()}
  else if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();prev()}
  else if(e.key==='t'||e.key==='T')toc();
  else if(e.key==='h'||e.key==='H')hideToggle();
  else if(e.key==='Escape'){$('drawer').hidden=true;$('sheetup').hidden=true}
});
let sx=null,sy=null;
sheet.addEventListener('touchstart',e=>{sx=e.touches[0].clientX;sy=e.touches[0].clientY},{passive:true});
sheet.addEventListener('touchend',e=>{
  if(sx==null)return;
  const t=e.changedTouches[0],dx=t.clientX-sx,dy=t.clientY-sy;sx=null;
  if(Math.abs(dx)>50&&Math.abs(dx)>Math.abs(dy)*1.4&&!e.target.closest('.M,.tab'))(dx<0?next:prev)();
},{passive:true});
sheet.addEventListener('click',e=>{
  if(e.target.closest('a,button,.rq,.paper,.rail,.M,.tab'))return;
  if(String(getSelection()))return;
  if(e.target.closest('.cover'))return;
  const b=vp.getBoundingClientRect();
  if(e.clientX>b.right-Math.min(60,b.width*.08))next();
  else if(e.clientX<b.left+Math.min(44,b.width*.05))prev();
});

/* 定理引用 */
function showThm(id){
  const narrow=getComputedStyle($('rail')).display==='none';
  if(narrow){
    $('sheetc').innerHTML=thmCard(id);renderMath($('sheetc'));$('sheetup').hidden=false;fitMath($('sheetc'));
  }else{
    const c=rail.querySelector(`.rcard[data-id="${id}"]`);
    if(c){c.scrollIntoView({block:'nearest',behavior:'smooth'});c.classList.add('flash');setTimeout(()=>c.classList.remove('flash'),900)}
  }
}
document.addEventListener('click',e=>{
  const a=e.target.closest('a.c');
  if(a){e.preventDefault();showThm(a.dataset.t);return}
  const pp=e.target.closest('.paper');
  if(pp&&document.body.classList.contains('hidepaper')){pp.classList.toggle('open')}
});
$('sheetx').onclick=()=>{$('sheetup').hidden=true};
bindRecall(document.body);

/* 工具条 */
function hideToggle(){
  const on=document.body.classList.toggle('hidepaper');store.set('hide',on);
  document.querySelector('[data-a=hide]').classList.toggle('on',on);
}
function toc(){
  const dr=$('drawer'),rd=store.get('read',{});
  if(!dr.hidden){dr.hidden=true;return}
  let h='<div><a href="index.html"><i>⌂</i>回总版</a>';
  let last='';
  D.issues.forEach(i=>{
    if(i.partname!==last){h+=`<h4>${i.partname}</h4>`;last=i.partname}
    h+=`<a href="q${String(i.no).padStart(2,'0')}.html" class="${i.no===no?'cur':''} ${rd[i.no]?'done':''}"><i>${i.no}</i>${i.title}</a>`;
  });
  dr.innerHTML=h+'<h4>工具</h4><a href="定理索引.html"><i>§</i>定理索引</a><a href="温故.html"><i>?</i>温故版（自测复习）</a></div>';
  dr.hidden=false;
}
$('drawer').addEventListener('click',e=>{if(e.target===e.currentTarget)e.currentTarget.hidden=true});
document.querySelector('.tools').addEventListener('click',e=>{
  const b=e.target.closest('button');if(!b)return;
  const a=b.dataset.a;
  if(a==='toc')toc();
  else if(a==='hide')hideToggle();
  else if(a==='night')toggleNight();
  else if(a==='rail'){
    const ids=citedHere();
    $('sheetc').innerHTML=ids.length?ids.map(thmCard).join(''):'<p class="rail-empty">本版没有引用前面的定理。</p>';
    renderMath($('sheetc'));
    const s=$('sheetup');s.hidden=!s.hidden;fitMath($('sheetc'));
  }
});
if(store.get('hide',false))hideToggle();

/* 末版：下一期 */
(function(){
  const i=D.issues.findIndex(x=>x.no===no),n=D.issues[i+1];
  $('endnext').innerHTML=n?`明日预告 · 第 ${n.no} 期<a href="q${String(n.no).padStart(2,'0')}.html">${n.title}</a>`:'全报刊完。可以上真题套卷了。<a href="温故.html">再过一遍温故版</a>';
})();

/* 初始化 */
async function boot(){
  renderMath(document);
  prevQs();
  stage.hidden=false;cover.hidden=true;
  /* KaTeX 字体是渲染后才开始加载的，必须再等一次，否则分页用的是后备字体的宽度 */
  try{await Promise.race([document.fonts.load('1em KaTeX_Main').then(()=>document.fonts.ready),new Promise(r=>setTimeout(r,2500))])}catch(e){}
  layout();
  const hp=/#p(\d+)/.exec(location.hash);
  apply(hp?+hp[1]-1:store.get(POS,0));
  document.documentElement.dataset.ready='1';
  if(document.fonts&&document.fonts.addEventListener)document.fonts.addEventListener('loadingdone',relayout);
}
function relayout(){
  const wasCover=page===0,hid=stage.hidden;
  stage.hidden=false;
  const anchor=wasCover?null:firstVisible();
  layout();
  apply(wasCover?0:anchor?pageOf(anchor):page);
}
let rt;
addEventListener('resize',()=>{clearTimeout(rt);rt=setTimeout(relayout,120)});
(document.fonts&&document.fonts.ready?document.fonts.ready:Promise.resolve()).then(()=>boot());
})();
