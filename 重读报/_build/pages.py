#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""重读报前台页：总版、定理索引、温故、错题、速记、套卷台。由 build.py 调用。"""
import os

HEAD = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<link rel="stylesheet" href="assets/katex/katex.min.css">
<link rel="stylesheet" href="assets/paper.css">
</head><body class="front">
<div class="front-wrap">
'''
FOOT = '''<script src="assets/katex/katex.min.js"></script><script src="assets/data.js"></script><script src="assets/paper.js"></script>
{script}
</div></body></html>
'''
NAV = ('<a href="index.html">总版</a><a href="一条线.html">一条线</a><a href="真题套卷.html">在线套卷</a><a href="套卷.html">套卷台</a><a href="错题.html">错题版</a><a href="速记.html">速记版</a>'
       '<a href="定理索引.html">定理索引</a><a href="温故.html">温故版</a><a href="#" onclick="CDNight();return false">夜读</a>')


def top(name):
    return f'<div class="front-top"><span>{name}</span><span>{NAV}</span></div>'


def write_all(root, idx, issues, THM, inline, esc, EX, TRAPS):
    w = lambda name, s: open(os.path.join(root, name), 'w', encoding='utf-8').write(s)
    w('index.html', front(idx, esc, EX))
    w('定理索引.html', theorems(idx, THM, esc))
    w('温故.html', recall_page())
    w('错题.html', wrong_page())
    w('速记.html', quick(idx, issues, inline, esc, TRAPS))
    w('套卷.html', exams(idx, EX))


def score_table(EX):
    """按 2016–2026 实际归类算：各部分平均每卷多少分、选填和解答各多少"""
    parts = {'甲': '一元微积分', '乙': '线性代数', '丙': '多元与级数', '丁': '概率统计'}
    rows, tot = {p: [0, 0] for p in parts}, 0
    for y in EX.PAPER_YEARS:
        n = len(EX.OLD if y <= 2020 else EX.NEW)
        for i, (no, s) in enumerate(zip(EX.MAP[y], EX.scores(y))):
            rows[EX.part_of(no)][0 if i < n else 1] += s
    k = len(EX.PAPER_YEARS)
    body = ''.join(f'<tr><td>{parts[p]}</td><td>{v[0]/k:.0f}</td><td>{v[1]/k:.0f}</td><td><b>{(v[0]+v[1])/k:.0f}</b></td></tr>' for p, v in rows.items())
    return f'<div class="tab"><table><thead><tr><th>部分</th><th>选填</th><th>解答</th><th>合计</th></tr></thead><tbody>{body}</tbody></table></div>'


def front(idx, esc, EX):
    tot = sum(i['mins'] for i in idx)
    maxw = max(i['w'] for i in idx) or 1
    names = {'甲': '一元微积分', '乙': '线性代数', '丙': '多元与级数', '丁': '概率统计'}
    parts = ''
    for p, name in names.items():
        items = [i for i in idx if i['part'] == p]
        parts += f'<section class="part"><h2>{name}<small>{sum(i["mins"] for i in items)} 分钟 · 平均每卷 {sum(i["w"] for i in items):.0f} 分</small></h2>'
        for i in items:
            parts += (f'<a class="it" data-no="{i["no"]}" href="q{i["no"]:02d}.html"><span class="t">{esc(i["title"])}</span>'
                      f'<span class="s"><span>第 {i["no"]} 期 · {esc(i["kicker"])}</span><span>{i["mins"]} 分</span></span>'
                      f'<span class="wbar" title="2016–2026 平均每卷约 {i["w"]:g} 分"><i style="width:{100*i["w"]/maxw:.0f}%"></i><em>{i["w"]:g}</em></span></a>' if i['w'] >= 1 else
                      f'<span class="wbar"><em>{"不足 1 分，后面都要用" if i["w"] else "打底，后面都要用"}</em></span></a>')
        parts += '</section>'
    return HEAD.format(title='重读报 · 数学一') + f'''
<div class="front-top"><span id="today"></span><span id="cnt"></span></div>
<div class="front-mast">重读报</div>
<div class="front-sub"><span>数学一 · 目标 120 分 · 全 {len(idx)} 期 · 约 {tot/60:.1f} 小时 · 读完上套卷</span><span>{NAV}</span></div>
<div class="lead-wrap">
  <div>
    <div class="kick" id="leadkick"></div>
    <h1><a id="leadt" href="q01.html"></a></h1>
    <p id="leadd"></p>
    <a class="lead-go" id="leadgo" href="q01.html"></a>
    <div class="plan"><h3>今天读到哪</h3><div id="planlist"></div></div>
  </div>
  <aside class="lead-side">
    <h3>行程 <span class="seg" id="seg"><button data-d="3">三天</button><button data-d="2">两天</button></span></h3>
    <ul id="days"></ul>
    <p class="hint" id="dayhint"></p>
    <h3 style="margin-top:.9em">每期四步</h3>
    <ol class="steps"><li>头版先答三道旧题。</li><li>读讲解。卷面按 H 遮住，自己写完再对。</li><li>末尾做实战，题和考法都只放在这里。</li><li>合上前答「今日考你」，答错的会回来。</li></ol>
    <h3 style="margin-top:.9em">工具</h3>
    <ul class="tools-l"><li><a href="一条线.html">一条线</a>：十四年真题倒推的一页知识回顾，带大题开头和自测，每次做卷前滑一遍</li><li><a href="真题套卷.html">在线套卷</a>：2010–2026 整卷，可开解答按钮、当场结算、计时</li><li><a href="套卷.html">套卷台</a>：120 分账本、卷子顺序、答题卡、失分回到第几期</li><li><a href="错题.html">错题版</a>：实战做错的</li><li><a href="速记.html">速记版</a>：每期要记的行和易错，考前过</li><li><a href="定理索引.html">定理索引</a>：全部定理，可遮住自测</li><li><a href="温故.html">温故版</a>：旧题循环</li></ul>
  </aside>
</div>
<p class="hint" style="margin:.3em 0 .8em">每期右下的数字是这部分内容在 2016–2026 的卷子上平均每卷多少分。按顺序读，别跳：后面的期会直接用前面的结论。</p>
<div class="parts">{parts}</div>
''' + FOOT.format(script='''<script>
(function(){
 const D=window.CD,S=window.CDStore,rd=S.get('read',{}),last=S.get('last',0),pad=n=>String(n).padStart(2,'0');
 const $=i=>document.getElementById(i);
 $('today').textContent=new Date().toLocaleDateString('zh-CN',{month:'long',day:'numeric',weekday:'long'});
 const left=Math.ceil((new Date('2026-12-19T08:30:00+08:00')-Date.now())/864e5);
 $('cnt').textContent=left>0?`距初试 ${left} 天`:'';
 const done=Object.keys(rd).length,all=done>=D.issues.length;
 const lastI=last&&!rd[last]?D.issues.find(i=>i.no===last):null;
 const cur=lastI||D.issues.find(i=>!rd[i.no])||D.issues[0];
 function split(n){const tot=D.issues.reduce((a,i)=>a+i.mins,0),m={};let c=0;D.issues.forEach(i=>{m[i.no]=Math.min(n,Math.floor(c/(tot/n))+1);c+=i.mins});return m}
 function draw(){
  const n=S.get('days',3),m=split(n),dn='一二三';
  document.querySelectorAll('#seg button').forEach(b=>b.classList.toggle('on',+b.dataset.d===n));
  let h='';
  for(let d=1;d<=n;d++){const its=D.issues.filter(i=>m[i.no]===d),t=its.reduce((a,i)=>a+i.mins,0),ok=its.filter(i=>rd[i.no]).length;
   h+=`<li class="${ok===its.length?'dn':''}"><b>第${dn[d-1]}天</b><span>第 ${its[0].no}–${its[its.length-1].no} 期 · ${(t/60).toFixed(1)} 小时${ok?` · ${ok}/${its.length}`:''}</span></li>`}
  $('days').innerHTML=h;
  $('dayhint').textContent=n===2?'两天线每天要 8 小时，含每期实战。实在排不开，就跳过每卷分值低的期的实战，讲解和今日考你不跳。':'时长按字数、公式数、例题和实战题数算，例题和实战都算了动手的时间。';
  const today=m[cur.no],its=D.issues.filter(i=>m[i.no]===today);
  $('planlist').innerHTML=its.map(i=>`<a href="q${pad(i.no)}.html" class="${rd[i.no]?'dn':''} ${i.no===cur.no?'now':''}"><i>${i.no}</i>${i.title}<small>${i.mins} 分</small></a>`).join('');
 }
 document.getElementById('seg').onclick=e=>{const b=e.target.closest('button');if(!b)return;S.set('days',+b.dataset.d);draw()};
 draw();
 if(all){
  $('leadkick').textContent=`全 ${D.issues.length} 期已读完`;
  const a=$('leadt');a.textContent='上真题套卷';a.href='套卷.html';
  $('leadd').textContent='从 2016 年开始，限时 3 小时。交卷后在答题卡上登分，失分会归到具体的期。';
  const g=$('leadgo');g.href='套卷.html';g.textContent='打开套卷台 →';
  document.querySelector('.plan').hidden=true;
 }else{
  $('leadkick').textContent=(done?`已读 ${done} / ${D.issues.length} 期 · `:'')+`今日头条 · 第 ${cur.no} 期 · ${cur.partname}`;
  const t=$('leadt');t.textContent=cur.title;t.href=`q${pad(cur.no)}.html`;
  $('leadd').textContent=cur.deck;
  const g=$('leadgo');g.href=t.href;g.textContent=(lastI?'继续阅读':'开始阅读')+` →（约 ${cur.mins} 分钟）`;
 }
 document.querySelectorAll('.it').forEach(a=>{const n=+a.dataset.no;if(rd[n])a.classList.add('done');if(n===cur.no&&!all)a.classList.add('now')});
})();
</script>''')


def theorems(idx, THM, esc):
    body_, last = '', None
    meta = {i['no']: i for i in idx}
    for tid, t in THM.items():
        if t['no'] != last:
            last = t['no']
            body_ += f'<h3><a href="q{last:02d}.html" style="text-decoration:none">第 {last} 期 · {esc(meta[last]["kicker"])}</a></h3>'
        body_ += f'<div class="rcard"><h5>{t["name"]}<span>{t["lab"]}</span></h5><div class="rbody">{t["html"]}</div></div>'
    return HEAD.format(title='定理索引 · 重读报') + top('定理索引') + f'''
<h1 class="pg-h" style="border-top:5px solid var(--rule);padding-top:.2em">全部定理与公式，按首次刊登排列</h1>
<p class="sub-lead">共 {len(THM)} 条。做套卷卡住时来这里查，⌘F 可搜定理名。<button class="mask-btn" id="mask">遮住内容自测</button></p>
<div class="thm-grid">{body_}</div>
''' + FOOT.format(script="""<script>CDRender(document);CDFit(document);
document.getElementById('mask').onclick=e=>{const on=document.body.classList.toggle('masked');e.target.textContent=on?'全部显示':'遮住内容自测';document.querySelectorAll('.rbody.open').forEach(x=>x.classList.remove('open'))};
document.addEventListener('click',e=>{const b=e.target.closest('.rbody');if(b&&document.body.classList.contains('masked'))b.classList.toggle('open')});</script>""")


def recall_page():
    return HEAD.format(title='温故版 · 重读报') + top('温故版') + '''
<h1 class="pg-h" style="border-top:5px solid var(--rule);padding-top:.2em">记不住，就再考一次</h1>
<p class="sub-lead">只从已经读过的期号里出题。答错的和隔得久的优先。每轮 10 道，约 5 分钟。每读完一天做两轮，上套卷前再过一遍「只看答错过的」。</p>
<div class="wg"><div class="wg-tools"><button data-m="due" class="on">到期优先</button><button data-m="wrong">只看答错过的</button><button data-m="all">全部随机</button><span id="wgs" style="margin-left:auto;color:var(--ink3)"></span></div><div id="wgl"></div><div class="wg-tools" style="margin-top:12px"><button id="wgn">再来 10 道</button></div></div>
''' + FOOT.format(script='''<script>
(function(){
 const D=window.CD,S=window.CDStore;let mode='due';const box=document.getElementById('wgl');
 CDBindRecall(box);
 function draw(){
  const rec=S.get('recall',{}),rd=S.get('read',{}),now=Date.now();
  let pool=D.recall.filter(r=>rd[r.no]);
  const ever=pool.length;
  if(mode==='wrong')pool=pool.filter(r=>rec[r.id]&&rec[r.id].ok===0);
  const pr=r=>{const o=rec[r.id];if(!o)return 50+Math.random()*20;const h=(now-o.t)/36e5;return (o.ok===0?100:0)+Math.min(h,72)/(o.n||1)+Math.random()*10};
  const pick=(mode==='all'?pool.slice().sort(()=>Math.random()-.5):pool.slice().sort((a,b)=>pr(b)-pr(a))).slice(0,10);
  const wrong=D.recall.filter(r=>rec[r.id]&&rec[r.id].ok===0).length,seen=Object.keys(rec).length;
  document.getElementById('wgs').textContent=`可考 ${ever} · 答过 ${seen} · 待巩固 ${wrong}`;
  if(!pick.length){box.innerHTML='<p class="hint">'+(ever?'没有答错过的题，换个模式吧。':'还没有读完的期。读完一期后，它的题才会进入这里。')+'</p>';return}
  box.innerHTML=pick.map(r=>`<div class="rq" data-q="${r.id}"><small>第 ${r.no} 期</small><p class="rq-q">${r.q}</p><p class="rq-a">${r.a}</p><div class="rq-b"><button data-v="1">答对了</button><button data-v="0">没答上</button></div></div>`).join('');
  CDRender(box);
 }
 document.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-m]').forEach(x=>x.classList.remove('on'));b.classList.add('on');mode=b.dataset.m;draw()});
 document.getElementById('wgn').onclick=draw;draw();
})();
</script>''')


def wrong_page():
    return HEAD.format(title='错题版 · 重读报') + top('错题版') + '''
<h1 class="pg-h" style="border-top:5px solid var(--rule);padding-top:.2em">做错的实战题</h1>
<p class="sub-lead">重做一遍，做对就从这里消失。题目下面的期号可以点回去。</p>
<div class="wg"><div class="wg-tools"><button data-m="wrong" class="on">错题</button><button data-m="all">全部实战</button><span id="wgs" style="margin-left:auto;color:var(--ink3)"></span></div><div id="wgl" class="wq"></div></div>
''' + FOOT.format(script='''<script>
(function(){
 const D=window.CD,S=window.CDStore;let mode='wrong';const box=document.getElementById('wgl');
 const pad=n=>String(n).padStart(2,'0');
 CDBindPrac(box,{fresh:true});
 function draw(){
  const rec=S.get('prac',{}),wrong=D.prac.filter(q=>rec[q.id]&&rec[q.id].ok===0),done=Object.keys(rec).length;
  document.getElementById('wgs').textContent=`实战 ${D.prac.length} · 做过 ${done} · 错着的 ${wrong.length}`;
  const list=mode==='wrong'?wrong:D.prac;
  box.innerHTML=list.length?list.map(q=>`<div class="wq-it"><a class="wq-no" href="q${pad(q.no)}.html">第 ${q.no} 期</a>${q.html}</div>`).join(''):'<p class="hint">现在没有错着的题。</p>';
  CDRender(box);
 }
 document.querySelectorAll('[data-m]').forEach(b=>b.onclick=()=>{document.querySelectorAll('[data-m]').forEach(x=>x.classList.remove('on'));b.classList.add('on');mode=b.dataset.m;draw()});
 draw();
})();
</script>''')


def quick(idx, issues, inline, esc, TRAPS):
    h = ''
    for it, i in zip(issues, idx):
        keep = ''.join(f'<li>{inline(k, it["ctx"])}</li>' for k in it['meta']['keep'])
        tr = ''.join(f'<li>{t["html"]}</li>' for t in TRAPS if t['no'] == i['no'])
        h += (f'<section class="qk"><h3><a href="q{i["no"]:02d}.html">第 {i["no"]} 期 · {esc(i["kicker"])}</a></h3><ol>{keep}</ol>'
              + (f'<div class="qk-t"><b>易错</b><ul>{tr}</ul></div>' if tr else '') + '</section>')
    return HEAD.format(title='速记版 · 重读报') + top('速记版') + f'''
<h1 class="pg-h" style="border-top:5px solid var(--rule);padding-top:.2em">每期只记这几行</h1>
<p class="sub-lead">全部 {len(idx)} 期的「本期只记」和易错，一页过完。每次套卷前翻一遍。</p>
<div class="qk-wrap">{h}</div>
''' + FOOT.format(script="<script>CDRender(document);CDFit(document)</script>")


def exams(idx, EX):
    return HEAD.format(title='套卷台 · 重读报') + top('套卷台') + f'''
<h1 class="pg-h" style="border-top:5px solid var(--rule);padding-top:.2em">读完报，上真题</h1>
<p class="sub-lead"><a href="真题套卷.html" style="font-weight:700">→ 打开在线套卷：不用 PDF，网页上直接做，交卷后成绩自动进下面的账本</a></p>
<p class="sub-lead" id="sum"></p>
<div class="xm-grid">
 <section>
  <h3>120 分账本</h3>
  <p>按 2021 起的卷面（选择 10×5、填空 6×5、解答 6 题 70 分）：</p>
  <div class="tab"><table><thead><tr><th></th><th>满分</th><th>120 线</th><th>130 线</th></tr></thead><tbody>
  <tr><td>选择</td><td>50</td><td>40（错 2 题）</td><td>45</td></tr>
  <tr><td>填空</td><td>30</td><td>25（错 1 题）</td><td>25</td></tr>
  <tr><td>解答</td><td>70</td><td>55</td><td>60</td></tr>
  </tbody></table></div>
  <p>解答 55 分的算法：计算大题写满（积分、极值、线代、概率），证明题第一问拿到，第二问写到哪算哪。写不出的题也要写前几步，步骤有分。</p>
 </section>
 <section>
  <h3>分值落在哪</h3>
  <p>2016–2026 共 11 卷，逐题归到本报的期，平均每卷：</p>
  {score_table(EX)}
  <p class="hint">每期的分值见总版的条形。</p>
 </section>
 <section>
  <h3>做卷规矩</h3>
  <ol class="steps"><li>限时 3 小时，手机拿开，写在纸上。</li><li>对解析登分：选填对错，大题估分。</li><li>交卷后这里才显示每题属于第几期。错题回对应的期，把例题重写一遍，再重做这道题。</li><li>每周 2 套，从 2016 做到 2023；2024–2026 留到 12 月按考试时间做。</li></ol>
  <p class="hint">卷子和解析都是本机文件，只有从本机打开这个页面时链接才通。</p>
 </section>
</div>
<h2 class="xm-h">整卷 · 2016–2026</h2>
<div id="papers" class="xm-list"></div>
<h2 class="xm-h">解答题专练 · 2010–2015 <small>这六年的选填已拆进每期实战，解答题没有用过</small></h2>
<div id="drills" class="xm-list"></div>
<div id="card"></div>
<h2 class="xm-h">失分回到哪几期</h2>
<div id="loss"><p class="hint">登过分之后，这里按失分从多到少列出该回去看的期。</p></div>
<h2 class="xm-h">搬家</h2>
<p class="hint">记录只存在这个浏览器里。换设备时导出再导入。 <button class="mask-btn" id="exp">导出记录</button> <label class="mask-btn">导入记录<input type="file" id="imp" accept=".json" hidden></label></p>
''' + FOOT.format(script='''<script>
(function(){
 const D=window.CD,S=window.CDStore,$=i=>document.getElementById(i),pad=n=>String(n).padStart(2,'0');
 const TAGS=['没记住','没想到方法','算错','审题错','没时间'];
 const issue=n=>D.issues.find(i=>i.no===n);
 const pdf=y=>`../../真题复盘中心易识别版/按年份/${y}/${y}_数学一_真题_图像保真版.pdf`;
 const sol=y=>'../../真题/'+(y<=2019?`${y}数学一解析.pdf`:y<=2025?`${y}数一真题解析.pdf`:`${y}考研数学（一）答案解析.pdf`);
 const get=()=>S.get('exam',{});
 const range=y=>{const e=D.exam[y];return D.drillYears.includes(y)?e.m.map((_,i)=>i).filter(i=>i>=e.n):e.m.map((_,i)=>i)};
 const full=y=>range(y).reduce((a,i)=>a+D.exam[y].s[i],0);
 function list(el,ys){
  const r=get();
  el.innerHTML=ys.map(y=>{const o=r[y],f=full(y);return `<div class="xm-it ${o?'dn':''}"><b>${y}</b><a href="${pdf(y)}" target="_blank">卷子</a><a href="${sol(y)}" target="_blank">解析</a><button data-y="${y}">${o?'改分':'登分'}</button><span>${o?`${o.tot} / ${f}`:''}</span></div>`}).join('');
 }
 function draw(){
  list($('papers'),D.paperYears);list($('drills'),D.drillYears);
  const r=get(),done=D.paperYears.filter(y=>r[y]);
  const last=done.slice(-3).map(y=>r[y].tot),avg=last.length?Math.round(last.reduce((a,b)=>a+b,0)/last.length):null;
  const left=Math.ceil((new Date('2026-12-19T08:30:00+08:00')-Date.now())/864e5);
  $('sum').textContent=(left>0?`距初试 ${left} 天。`:'')+(done.length?`整卷做了 ${done.length} / ${D.paperYears.length} 套，最近 ${last.length} 套平均 ${avg} 分，目标 120。`:'目标 120，能更高就更高。先把报读完，再从 2016 开始。');
  const loss={},tag={};
  Object.keys(r).forEach(y=>{const e=D.exam[y],o=r[y];range(+y).forEach(i=>{const lost=e.s[i]-(o.s[i]??0);if(lost>0){loss[e.m[i]]=(loss[e.m[i]]||0)+lost;if(o.t[i])tag[o.t[i]]=(tag[o.t[i]]||0)+lost}})});
  const k=Object.entries(loss).sort((a,b)=>b[1]-a[1]).slice(0,10);
  if(k.length){const mx=k[0][1];
   $('loss').innerHTML='<div class="xm-loss">'+k.map(([n,v])=>`<a href="q${pad(+n)}.html"><span>第 ${n} 期 · ${issue(+n).kicker}</span><i style="width:${100*v/mx}%"></i><em>${v} 分</em></a>`).join('')+'</div>'
    +(Object.keys(tag).length?'<p class="hint">失分原因：'+Object.entries(tag).sort((a,b)=>b[1]-a[1]).map(([t,v])=>`${t} ${v} 分`).join('，')+'。</p>':'');
  }
 }
 function card(y){
  const e=D.exam[y],o=get()[y]||{s:{},t:{}},idx=range(y);
  const hasS=i=>o.s[i]!=null;
  const row=i=>{const sc=e.s[i],n=i+1,big=i>=e.n;
   const val=hasS(i)?o.s[i]:'';
   const inp=big?`<input type="number" min="0" max="${sc}" step="1" data-i="${i}" value="${val}" placeholder="0–${sc}">`
     :`<button class="tk ${val===sc?'ok':''}" data-i="${i}" data-v="${sc}">对</button><button class="tk ${val===0?'no':''}" data-i="${i}" data-v="0">错</button>`;
   const sel=`<select data-t="${i}"><option value="">失分原因</option>${TAGS.map(t=>`<option ${o.t[i]===t?'selected':''}>${t}</option>`).join('')}</select>`;
   const where=get()[y]?`<a class="wh" href="q${pad(e.m[i])}.html">第 ${e.m[i]} 期</a>`:'';
   return `<div class="xr" data-r="${i}"><b>${n}</b><span class="xs">${inp}</span>${sel}${where}</div>`};
  $('card').innerHTML=`<div class="xm-card"><div class="xm-card-h"><b>${y} 年答题卡</b><span>共 ${full(y)} 分</span><button id="xclose">收起</button></div><div class="xrows">${idx.map(row).join('')}</div><div class="xm-card-f"><span id="xtot"></span><button id="xsave" class="lead-go">交卷，看失分</button></div></div>`;
  const box=$('card');
  const collect=()=>{const s={},t={};box.querySelectorAll('input[data-i]').forEach(x=>{if(x.value!=='')s[x.dataset.i]=Math.max(0,Math.min(+x.max,+x.value))});box.querySelectorAll('.tk.ok,.tk.no').forEach(x=>{s[x.dataset.i]=+x.dataset.v});box.querySelectorAll('select').forEach(x=>{if(x.value)t[x.dataset.t]=x.value});return{s,t}};
  const tot=()=>{const c=collect();$('xtot').textContent=`已登 ${Object.keys(c.s).length} / ${idx.length} 题，${Object.values(c.s).reduce((a,b)=>a+b,0)} 分`};
  box.onclick=ev=>{const b=ev.target.closest('.tk');if(b){b.parentNode.querySelectorAll('.tk').forEach(x=>x.classList.remove('ok','no'));b.classList.add(+b.dataset.v?'ok':'no');tot();return}
   if(ev.target.id==='xclose'){box.innerHTML='';return}
   if(ev.target.id==='xsave'){const c=collect(),r=get();r[y]={s:c.s,t:c.t,tot:Object.values(c.s).reduce((a,b)=>a+b,0),at:Date.now()};S.set('exam',r);draw();card(y);box.scrollIntoView({block:'start'})}};
  box.oninput=tot;tot();box.scrollIntoView({block:'start',behavior:'smooth'});
 }
 document.addEventListener('click',ev=>{const b=ev.target.closest('.xm-it button');if(b)card(+b.dataset.y)});
 $('exp').onclick=()=>{const o={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.startsWith('cd_'))o[k]=localStorage.getItem(k)}const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify(o)],{type:'application/json'}));a.download='重读报记录.json';a.click()};
 $('imp').onchange=async ev=>{const f=ev.target.files[0];if(!f)return;const o=JSON.parse(await f.text());Object.keys(o).forEach(k=>{if(k.startsWith('cd_'))localStorage.setItem(k,o[k])});location.reload()};
 draw();
})();
</script>''')
