/* 在线真题套卷引擎：408 与数学一共用，各自的 EXAM_CONF 写在页面里，卷子数据按年放在 assets/exam/yYYYY.js。
 * 题目字段：no 题号 / type choice|blank|essay / score / subj / stem(html) 或 img(题面图) / opts / ans
 *           sol(html，解答) / more(html，详解，可省) / solImg(解答图数组) / tag(考点) / back({href,text})
 * 精研（可选）：C.deepPath 指向 deep/dYYYY.js，设 EXAM_DEEP[年] = {time,look,route[],core[],q:{题号:{lv,k,core,how,vary,link,back}}}，交卷后才显示。
 * 精解（可选）：C.richPath 指向 rich/rYYYY.js，设 EXAM_RICH[年]={q:{题号:{stem,opts,ans,sol,tpl}},kp:{}}，加载卷子时合并：有 stem 就换掉题面图（原图收进「看原卷」），有 sol 就换掉解析图。
 *   知识点/套路弹窗：<button class="kpb" data-kp="id">，内容在 window.EXAM_KP（rich/kp.js）与各年 kp。
 * 分档（可选）：页面先引 assets/exam/tier.js，设 EXAM_TIER[年]={line:[保底,正常,冲刺],mins,note,q:{题号:{m:限时分钟,p:[必,常,冲,弃],n:说明}}}（_build/tier_build.py 生成）。
 * 做卷顺序（可选）：C.plan = {order:[[年,档]],tiers:{档:{name,min,desc}},rhythm,cut,pace} */
(function(){
  'use strict';
  var C = window.EXAM_CONF, KEY = C.key + '_exam_v1';
  var $ = function(i){ return document.getElementById(i); };
  var root = $('app');
  var DEF = { showSol:false, mustAll:false, instant:false, timer:'down', autoEnd:false, showCount:true,
    read:false, autoSol:true, hint:false, kpOpen:false, layer:false, tier:true, view:'scroll', fs:'m', hide:{} };

  function load(){
    var o = {};
    try { o = JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e){}
    o.set = Object.assign({}, DEF, o.set||{}); o.set.hide = o.set.hide||{}; o.sess = o.sess||{}; o.hist = o.hist||[];
    return o;
  }
  var S = load();
  function save(){ try { localStorage.setItem(KEY, JSON.stringify(S)); } catch(e){} }
  function esc(s){ return String(s==null?'':s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }
  function fmt(sec){ sec=Math.max(0,Math.floor(sec)); var h=Math.floor(sec/3600),m=Math.floor(sec%3600/60),s=sec%60; return (h?h+':':'')+(h&&m<10?'0':'')+m+':'+(s<10?'0':'')+s; }
  function daysLeft(){ return Math.ceil((new Date(C.examAt)-Date.now())/864e5); }
  function countText(){
    var ms = new Date(C.examAt)-Date.now();
    if (ms<=0) return C.examName+' 已开考';
    var d=Math.floor(ms/864e5), h=Math.floor(ms%864e5/36e5), m=Math.floor(ms%36e5/6e4);
    return '距 '+C.examName+' '+d+' 天 '+h+' 小时 '+m+' 分';
  }

  /* —— 开关 —— */
  var TOGGLES = [
    ['showSol','做题时每题下面有「看解析」按钮','关着时做题中看不到解析，交卷后才能看。'],
    ['autoSol','判完自动摊开解析','「练习」模式下选完或点「对答案」后，解析直接出现，不用再点一次。'],
    ['hint','做题时可以先看「要用的知识点」','卡住时点题目下面的「提示」，只给这题要用的知识点和套路，不给答案。看过的题会记一笔。'],
    ['kpOpen','知识点卡默认全部展开','解析顶上「这题要用到的」那一栏：开着时每张卡的公式、结论直接摊开；关着时只列标题，点哪张开哪张。'],
    ['tier','做题时显示分档和每题限时','题号旁标「必拿 / 应得 / 冲刺 / 后放」和这题最多给几分钟，顶栏显示本题已用时间，超了变红。最后三张模考卷建议关掉，自己判断。'],
    ['layer','解析分两层揭开','先只给读题和思路，合上自己写；写完再点一下看每一步和考场卷面。'],
    ['mustAll','必须全部答完才能交卷','有题没答时交卷按钮只列出缺的题，不让交。解答题写在纸上的，点「已写完」就算答过。'],
    ['showCount','显示距考试倒计时','顶栏一直显示还剩多少天。'],
    ['autoEnd','时间到自动交卷','倒计时走完直接交卷，不看有没有答完。关着时只提醒，可继续写。']
  ];
  var MODES = [['exam','考试','整卷做完再交，交卷后统一判分、看解析。'],['practice','练习','做一题对一题：选完立刻判对错，填空和解答写完点「对答案」。'],['read','读解析','不用作答，每题的解析直接摊开，适合二刷和考前翻看。']];
  var HIDES = [['rev','复盘'],['read','读题圈画'],['sk','草稿图（考场上画的、列的）'],['see','示意图（看懂就行、考场不画的）'],['think','思路'],['steps','每一步'],['omit','考场可省的步骤'],['fast','秒杀'],['paper','考场卷面'],['note','批注'],['vary','举一反三']];
  function modeOf(){ return S.set.read?'read':S.set.instant?'practice':'exam'; }
  function segHtml(attr, list, on){ return '<span class="seg" role="group">'+list.map(function(o){ return '<button data-'+attr+'="'+o[0]+'" class="'+(on===o[0]?'on':'')+'">'+o[1]+'</button>'; }).join('')+'</span>'; }
  function togglesHtml(){
    var md=modeOf(), mdDesc=MODES.filter(function(m){ return m[0]===md; })[0][2];
    var h = '<div class="tg tg-sel tg-mode"><span class="tx"><b>模式</b><small>'+mdDesc+'</small></span>'+segHtml('mode',MODES,md)+'</div>'
      + '<div class="tg tg-sel"><span class="tx"><b>计时</b><small>考试时长 '+C.minutes+' 分钟，可以中途暂停。</small></span>'+segHtml('timer',[['down','倒计时'],['up','正计时'],['off','不计时']],S.set.timer)+'</div>'
      + '<div class="tg tg-sel"><span class="tx"><b>看题方式</b><small>一题一屏时只显示当前这题，用底部按钮或 ← → 键翻题。</small></span>'+segHtml('view',[['scroll','整卷往下翻'],['one','一题一屏']],S.set.view)+'</div>'
      + '<div class="tg tg-sel"><span class="tx"><b>字号</b><small>题面和解析一起放大缩小。</small></span>'+segHtml('fs',[['s','小'],['m','中'],['l','大'],['xl','特大']],S.set.fs)+'</div>';
    h += TOGGLES.map(function(t){
      return '<label class="tg"><input type="checkbox" data-set="'+t[0]+'"'+(S.set[t[0]]?' checked':'')+'><span class="sw"></span><span class="tx"><b>'+t[1]+'</b><small>'+t[2]+'</small></span></label>';
    }).join('');
    h += '<div class="tg tg-sel tg-wide"><span class="tx"><b>解析里显示哪几块</b><small>点一下划掉就不显示。时间紧就点「精简」：去掉考场可省的步骤、举一反三和考场不画的示意图。</small></span><span class="chips"><button data-preset="full" class="pre">完整</button><button data-preset="lite" class="pre">精简</button>'
      + HIDES.map(function(o){ return '<button data-hide="'+o[0]+'" class="'+(S.set.hide[o[0]]?'':'on')+'">'+o[1]+'</button>'; }).join('')+'</span></div>';
    return h;
  }
  function refreshToggles(){ document.querySelectorAll('.tgbox').forEach(function(el){ el.innerHTML=togglesHtml(); }); }
  function applySet(){
    var de=document.documentElement;
    de.setAttribute('data-fs', S.set.fs||'m');
    HIDES.forEach(function(o){ de.classList.toggle('hide-'+o[0], !!S.set.hide[o[0]]); });
    document.body.classList.toggle('one', !!cur && S.set.view==='one');
  }
  document.addEventListener('change', function(e){
    var k = e.target.getAttribute && e.target.getAttribute('data-set');
    if (!k) return;
    S.set[k] = e.target.checked; save();
    document.querySelectorAll('[data-set="'+k+'"]').forEach(function(x){ x.checked = e.target.checked; });
    if (cur) redrawPaper();
  });
  document.addEventListener('click', function(e){
    var t=e.target, b;
    if (!t.closest) return;
    if ((b=t.closest('button[data-timer]'))) { S.set.timer=b.getAttribute('data-timer'); save(); refreshToggles(); tick(); return; }
    if ((b=t.closest('button[data-mode]'))) {
      var m=b.getAttribute('data-mode');
      S.set.read=m==='read'; S.set.instant=m==='practice';
      if (m==='exam') S.set.showSol=false; else S.set.showSol=true;
      save(); refreshToggles(); if (cur) redrawPaper(); return;
    }
    if ((b=t.closest('button[data-view]'))) {
      S.set.view=b.getAttribute('data-view'); save(); refreshToggles(); applySet();
      if (cur) { setCur(curNo()); if (S.set.view==='one') window.scrollTo(0,0); else go(ss.at); }
      return;
    }
    if ((b=t.closest('button[data-fs]'))) { S.set.fs=b.getAttribute('data-fs'); save(); refreshToggles(); applySet(); return; }
    if ((b=t.closest('button[data-preset]'))) { S.set.hide = b.getAttribute('data-preset')==='lite' ? {omit:true,vary:true,see:true} : {}; save(); refreshToggles(); applySet(); return; }
    if ((b=t.closest('button[data-hide]'))) { var hk=b.getAttribute('data-hide'); S.set.hide[hk]=!S.set.hide[hk]; save(); refreshToggles(); applySet(); return; }
  });

  /* —— 首页 —— */
  function home(){
    stopTimer(); cur=null; document.title = C.title; applySet();
    var left = daysLeft();
    var rows = C.years.slice().reverse().map(function(y){
      var hs = S.hist.filter(function(h){ return h.y===y; });
      var best = hs.length ? Math.max.apply(null, hs.map(function(h){ return h.score; })) : null;
      var ss = S.sess[y], going = ss && !ss.done && Object.keys(ss.a||{}).length;
      var info = (C.yearNote && C.yearNote[y]) || '';
      return '<a class="yr'+(best!=null?' dn':'')+(going?' go':'')+'" href="#y='+y+'"><b>'+y+'</b>'
        + '<span>'+(going?'做到 '+Object.keys(ss.a).length+' 题，继续':best!=null?'最高 '+best+' 分':'未做')+'</span>'
        + (info?'<em>'+esc(info)+'</em>':'')
        + (tierY(y)?'<em class="ln">'+lineText(y)+'</em>':'')
        + (C.deepYears&&C.deepYears.indexOf(y)>=0?'<em class="dpb">已精研</em>':'')+'</a>';
    }).join('');
    var hist = S.hist.slice().reverse().slice(0,12).map(function(h){
      return '<tr><td>'+h.y+'</td><td><b>'+h.score+'</b> / '+h.full+'</td><td>'+fmt(h.secs)+'</td><td>'+new Date(h.at).toLocaleDateString('zh-CN')+'</td></tr>';
    }).join('');
    root.innerHTML = '<div class="hm">'
      + '<div class="hm-top"><a href="'+C.backHref+'">← '+esc(C.backText)+'</a><span>'+esc(C.title)+'</span><button class="ghost" id="night">夜</button></div>'
      + '<div class="hero"><div class="cd"><i>距 '+esc(C.examName)+'</i><strong>'+(left>0?left:0)+'</strong><i>天</i></div>'
      + '<div class="hero-t"><h1>'+esc(C.heading)+'</h1><p>'+C.lead+'</p><p class="cdx" id="cdx">'+esc(countText())+'　·　'+esc(C.examWhen)+'</p></div></div>'
      + (C.plan?'<h2>按这个顺序做</h2><div id="plan">'+planHtml()+'</div>':'')
      + '<h2>模式与开关</h2><div class="tgs tgbox">'+togglesHtml()+'</div>'
      + '<h2>选一年</h2>'+(window.EXAM_TIER?'<p class="lnlead">每年下面一行是这张卷的<b>三条线</b>，按预期得分率算，不按全对算：<b>保</b>＝必拿题拿到九成（低于它说明基础题在丢，先补这些，别碰难题）；<b>常</b>＝必拿题基本全拿、应得题拿七成（正常发挥该到的分）；<b>冲</b>＝再加上应得题九成、冲刺题一半（尽力能到的分）。做题时每题标着档和限时：<b>冲刺题超过限时就蒙一个、点标记，做完综合题再回来</b>；标「后放」或写着「取舍」的部分先跳过。交卷后成绩单告诉你分丢在哪一档、哪几题超时。</p>':'')+'<div class="yrs">'+rows+'</div>'
      + (window.EXAM_KP?'<h2>知识点与套路速查</h2><p class="kpent"><a href="#kp">翻开速查本 →</a><span>精解里出现过的 '+Object.keys(window.EXAM_KP).length+' 张卡：公式、常用结论、跨年套路，每张标着真题里在哪出现过。可以搜。</span></p>':'')
      + (hist?'<h2>做过的卷子</h2><div class="tabw"><table class="hst"><thead><tr><th>年份</th><th>得分</th><th>用时</th><th>日期</th></tr></thead><tbody>'+hist+'</tbody></table></div>':'')
      + (C.footHtml?'<div class="foot">'+C.footHtml+'</div>':'')
      + '</div>';
    window.scrollTo(0,0);
  }

  /* —— 做卷顺序 —— */
  function pget(){ var o={}; try{ o=JSON.parse(localStorage.getItem(C.key+'_plan'))||{}; }catch(e){} return o; }
  function pset(o){ try{ localStorage.setItem(C.key+'_plan',JSON.stringify(o)); }catch(e){} }
  function ymd(d){ return d.getFullYear()+'-'+('0'+(d.getMonth()+1)).slice(-2)+'-'+('0'+d.getDate()).slice(-2); }
  function planHtml(){
    var L=C.plan, o=pget(), pace=+(o.pace||L.pace||1.5);
    var start=o.start||L.start||ymd(new Date());
    if (!o.start) { o.start=start; pset(o); }   /* 第一次打开时钉住，免得日期每天往后漂 */
    var d0=new Date(start+'T00:00:00'), cut=new Date(L.cut+'T00:00:00');
    var slots=Math.max(0,Math.floor((cut-d0)/864e5/pace)+1);
    var order=L.order.slice(), keep=order.slice(), cutList=[];
    while (keep.length>slots) {   /* 时间不够：保住末尾的模考卷，从模考前一张往前砍 */
      var k=keep.length-1; while(k>=0&&keep[k][1]==='mock') k--;
      if (k<0) break; cutList.unshift(keep[k]); keep.splice(k,1);
    }
    var doneY={}; S.hist.forEach(function(h){ doneY[h.y]=1; });
    var nextShown=false;
    var rows=keep.map(function(it,i){
      var y=it[0], t=L.tiers[it[1]]||{}, dt=new Date(d0.getTime()+Math.floor(i*pace)*864e5);
      var st=doneY[y]?'dn':(!nextShown?(nextShown=true,'nx'):'');
      var dp=C.deepYears&&C.deepYears.indexOf(y)>=0;
      return '<tr class="'+st+'"><td>'+(i+1)+'</td><td>'+(dt.getMonth()+1)+'/'+dt.getDate()+'</td><td><a href="#y='+y+'"><b>'+y+'</b></a>'+(it[2]?'<small>'+it[2]+'</small>':'')+'</td>'
        + '<td><span class="tier t-'+it[1]+'">'+esc(t.name||it[1])+'</span></td><td>'+(t.min?'复盘 '+t.min+' 分':'')+'</td><td class="pln">'+(lineText(y)||'<small class="nod">—</small>')+'</td>'
        + '<td>'+(st==='dn'?'✓ 做过':st==='nx'?'← 下一张':'')+(dp?'':' <small class="nod">精研待写</small>')+'</td></tr>';
    }).join('');
    var tiers=Object.keys(L.tiers).map(function(k){ var t=L.tiers[k]; return '<li><span class="tier t-'+k+'">'+esc(t.name)+'</span> '+t.desc+'</li>'; }).join('');
    return '<div class="pl-set"><label>开始做卷的日子 <input type="date" id="pl-start" value="'+start+'"></label>'
      + '<span class="seg">'+[[1.5,'一天半一张（推荐）'],[1,'一天一张']].map(function(p){ return '<button data-pace="'+p[0]+'" class="'+(pace===p[0]?'on':'')+'">'+p[1]+'</button>'; }).join('')+'</span>'
      + '<small>到 '+L.cut.slice(5).replace('-','/')+' 能做 '+keep.length+' 张'+(cutList.length?'，砍掉 '+cutList.length+' 张':'')+'；之后两天只回看错题，不开新卷。</small></div>'
      + (L.rhythm?'<div class="pl-rh">'+L.rhythm+'</div>':'')
      + '<div class="tabw"><table class="pl"><thead><tr><th>#</th><th>日期</th><th>卷</th><th>档</th><th>复盘</th><th>保 · 常 · 冲</th><th></th></tr></thead><tbody>'+rows+'</tbody></table></div>'
      + (cutList.length?'<p class="pl-cut">时间不够、先砍的：'+cutList.map(function(it){ return '<a href="#y='+it[0]+'">'+it[0]+'</a>'; }).join(' ')+'（价值最低，有空再补）</p>':'')
      + '<ul class="pl-t">'+tiers+'</ul>'
      + (L.why?'<details class="pl-why"><summary>为什么是这个顺序</summary>'+L.why+'</details>':'');
  }
  document.addEventListener('change', function(e){
    if (e.target.id!=='pl-start') return;
    var o=pget(); o.start=e.target.value; pset(o); var p=$('plan'); if(p) p.innerHTML=planHtml();
  });
  document.addEventListener('click', function(e){
    var b=e.target.closest&&e.target.closest('[data-pace]'); if(!b) return;
    var o=pget(); o.pace=+b.getAttribute('data-pace'); pset(o); var p=$('plan'); if(p) p.innerHTML=planHtml();
  });

  /* —— 卷子 —— */
  var cur=null, P=null, ss=null, tm=null, lastTick=0, paused=false, warned=false;
  function loadPaper(y, cb){
    window.EXAM_PAPERS = window.EXAM_PAPERS||{};
    if (window.EXAM_PAPERS[y]) return cb();
    var s=document.createElement('script');
    s.src=C.dataPath.replace('{Y}',y)+'?v='+(C.ver||1);
    s.onload=function(){ loadRich(y, cb); }; s.onerror=function(){ root.innerHTML='<p style="padding:2em">这一年的卷子加载失败。</p>'; };
    document.head.appendChild(s);
  }
  function loadRich(y, cb){
    var ys=window.EXAM_RICH_YEARS||[];
    if (!C.richPath || ys.indexOf(y)<0) return cb();
    window.EXAM_RICH=window.EXAM_RICH||{};
    if (window.EXAM_RICH[y]) { mergeRich(y); return cb(); }
    var s=document.createElement('script');
    s.src=C.richPath.replace('{Y}',y)+'?v='+(C.richVer||C.ver||1);
    s.onload=function(){ mergeRich(y); cb(); }; s.onerror=function(){ cb(); };
    document.head.appendChild(s);
  }
  function mergeRich(y){
    var R=window.EXAM_RICH[y], P0=window.EXAM_PAPERS[y];
    if (!R||!P0||P0._rich) return;
    P0._rich=1;
    window.EXAM_KP=window.EXAM_KP||{};
    for (var k in (R.kp||{})) window.EXAM_KP[k]=R.kp[k];
    P0.q.forEach(function(q){
      var r=R.q&&R.q[q.no]; if(!r) return;
      if (r.stem) { if(q.img){ q.origImg=q.img; delete q.img; } q.stem=r.stem; }
      if (r.opts) q.opts=r.opts;
      if (r.ans) q.ansText=r.ans;
      if (r.tpl) q.tpl=r.tpl;
      if (r.sol) { q.rich=r.sol.replace(/⛳\s*/g,''); if(q.solImg){ q.solOrig=q.solImg; delete q.solImg; } if(q.sol){ q.solBook=q.sol; delete q.sol; } if(q.more){ q.moreBook=q.more; delete q.more; } }
    });
  }
  function deepOf(no){ var D=cur&&window.EXAM_DEEP&&window.EXAM_DEEP[cur]; return D&&D.q&&D.q[no]; }
  function loadDeep(y){
    window.EXAM_DEEP = window.EXAM_DEEP||{};
    if (!C.deepPath || window.EXAM_DEEP[y] || loadDeep['_'+y]) return;
    loadDeep['_'+y]=1;
    var s=document.createElement('script');
    s.src=C.deepPath.replace('{Y}',y)+'?v='+(C.deepVer||C.ver||1);
    s.onload=function(){ if(cur===y&&ss&&ss.done) redrawPaper(); };
    s.onerror=function(){};
    document.head.appendChild(s);
  }
  function open(y){
    loadDeep(y);
    loadPaper(y, function(){
      P = window.EXAM_PAPERS[y]; cur = y;
      ss = S.sess[y];
      if (!ss || ss.done && !location.hash.match(/review/)) {
        if (ss && ss.done) { showReport(); return; }
        ss = S.sess[y] = { a:{}, flag:{}, self:{}, open:{}, secs:0, at:Date.now() };
      }
      document.title = y+' 真题 · '+C.title;
      drawPaper();
    });
  }
  function isDone(q){
    var v = ss.a[q.no];
    if (q.type==='choice') return !!v;
    return v!=null && v!=='';
  }
  function fullScore(){ return P.q.reduce(function(a,q){ return a+q.score; },0); }
  function qScore(q){
    if (q.type==='choice') return ss.a[q.no]===q.ans ? q.score : 0;
    var v = ss.self[q.no];
    return v==null ? null : v;
  }
  function liveScore(){
    return P.q.reduce(function(a,q){
      if (q.type==='choice') return a + (ss.a[q.no]===q.ans?q.score:0);
      return a + (ss.self[q.no]||0);
    },0);
  }
  function judged(q){ return ss.done || (S.set.instant && (q.type==='choice' ? !!ss.a[q.no] : !!ss.open[q.no])); }

  /* —— 分档 · 限时 · 三条线 —— */
  var TN=['必拿','应得','冲刺','后放'], TS=['保','常','冲','弃'], TC=['a','b','c','x'];
  function tierY(y){ return window.EXAM_TIER&&window.EXAM_TIER[y]; }
  function tierOf(no){ var T=cur&&tierY(cur); return T&&T.q&&T.q[no]; }
  function isOver(u,t){ return u>t.m*60*1.25+20; }
  function tierChip(q){
    var t=tierOf(q.no); if(!t||(!ss.done&&!S.set.tier)) return '';
    var i=t.p.indexOf(q.score), h, jd=judged(q)||ss.done, u=(ss.qt&&ss.qt[q.no])||0;
    if (i>=0) h='<span class="tr tr-'+TC[i]+'">'+TN[i]+'</span>';
    else h='<span class="tr tr-s">'+t.p.map(function(x,k){ return x?'<i class="tr-'+TC[k]+'">'+TS[k]+' '+x+'</i>':''; }).join('')+'</span>';
    h+='<span class="tm'+(jd&&isOver(u,t)?' ov':'')+'">限 '+t.m+' 分'+(jd&&u>=5?' · 用了 '+fmt(u):'')+'</span>';
    return h;
  }
  function tierNote(q){
    var t=tierOf(q.no); if(!t||!t.n||(!ss.done&&!S.set.tier)) return '';
    if (!(judged(q)||ss.done) && !t.p[3]) return '';   /* 做题时只提前给「先跳过」这类取舍建议，别的说明判完再给 */
    if (!(judged(q)||ss.done)) return '<div class="trn"><i>取舍</i>这题有 '+t.p[3]+' 分不值得硬啃：能写的先写上，卡住 3 分钟就走，先做后面的题。具体放哪一问，对完答案再看。</div>';
    return '<div class="trn"><i>'+(t.p[3]?'取舍':'分档说明')+'</i>'+t.n+'</div>';
  }
  function refreshTier(){ var el=document.querySelector('.trp'); if(!el) return; var d=document.createElement('div'); d.innerHTML=tierRep(); if(d.firstChild) el.parentNode.replaceChild(d.firstChild, el); }
  function lineText(y){ var T=tierY(y); return T?'保 '+T.line[0]+' · 常 '+T.line[1]+' · 冲 '+T.line[2]:''; }
  function tierRep(){
    var T=cur&&tierY(cur); if(!T) return '';
    var full=[0,0,0,0], got=[0,0,0,0], lost=[[],[],[],[]], over=[], xt=0, any=0, pend=0;
    P.q.forEach(function(q){
      var t=T.q[q.no]; if(!t) return;
      var u=(ss.qt&&ss.qt[q.no])||0;
      if (u) any=1;
      if (isOver(u,t)) over.push([q.no,u,t.m]);
      if (t.p[3]===q.score) xt+=u;
      if (qScore(q)==null) { pend++; return; }
      var r=qScore(q);
      t.p.forEach(function(p,i){ if(!p) return; var g=Math.min(r,p); r-=g; full[i]+=p; got[i]+=g; if(g<p) lost[i].push(q.no); });
    });
    var sc=liveScore(), L=T.line, F=fullScore(), msg;
    var lk=function(n){ return '<a href="javascript:;" data-go="'+n+'">'+n+'</a>'; };
    if (pend) msg='<b>还有 '+pend+' 道题没登分。</b>在下面每题解答底下自评，登完这里才算数；下表暂时只统计已登分的题。';
    else if (sc<L[0]) msg='<b>低于保底线 '+(L[0]-sc)+' 分。</b>必拿题丢了 '+(full[0]-got[0])+' 分，先把这些补回来；冲刺题这一轮不用管。';
    else if (sc<L[1]) msg='<b>过了保底线，离正常线差 '+(L[1]-sc)+' 分。</b>'+(full[0]-got[0]?'必拿题还丢了 '+(full[0]-got[0])+' 分，这是最便宜的分。':'必拿题全拿到了，差的分在「应得」题上。');
    else if (sc<L[2]) msg='<b>到了正常线，离冲刺线差 '+(L[2]-sc)+' 分。</b>'+(full[0]-got[0]+full[1]-got[1]?'必拿、应得题里还丢了 '+(full[0]-got[0]+full[1]-got[1])+' 分，先补它们再啃冲刺题。':'剩下的分都在冲刺题上。');
    else msg='<b>到了冲刺线。</b>保持这个节奏，别再加量。';
    var pos=function(v){ return (100*v/F).toFixed(1)+'%'; };
    var h='<div class="trp"><div class="trp-h"><b>三条线</b><span>保底 '+L[0]+'　正常 '+L[1]+'　冲刺 '+L[2]+'　你 '+sc+'</span></div>'
      + '<div class="trk"><i class="z za" style="width:'+pos(L[0])+'"></i><i class="z zb" style="left:'+pos(L[0])+';width:'+pos(L[1]-L[0])+'"></i><i class="z zc" style="left:'+pos(L[1])+';width:'+pos(L[2]-L[1])+'"></i><i class="me" style="left:'+pos(sc)+'"><u>'+sc+'</u></i></div>'
      + '<p class="trm">'+msg+'</p>'
      + '<div class="tabw"><table class="rp trt"><tbody>'+[0,1,2,3].map(function(i){
          if (!full[i]) return '';
          return '<tr><td><span class="tr tr-'+TC[i]+'">'+TN[i]+'</span></td><td><b>'+got[i]+'</b> / '+full[i]+'</td><td>'+(lost[i].length?(i<3?'丢在 ':'没拿 ')+lost[i].map(lk).join(' '):'全拿到')+'</td></tr>';
        }).join('')+'</tbody></table></div>';
    if (any) {
      over.sort(function(a,b){ return (b[1]-b[2]*60)-(a[1]-a[2]*60); });
      var ex=over.reduce(function(a,o){ return a+o[1]-o[2]*60; },0);
      h+='<p class="tro">'+(over.length?'<b>超时 '+over.length+' 题，多花 '+Math.round(ex/60)+' 分钟：</b>'+over.slice(0,8).map(function(o){ return lk(o[0])+' '+fmt(o[1])+'（限 '+o[2]+'）'; }).join('　'):'<b>没有明显超时的题。</b>')
        + (xt>=60?'　「后放」题上花了 '+Math.round(xt/60)+' 分钟。':'')+'</p>';
    }
    if (T.note) h+='<p class="trnote">'+T.note+'</p>';
    return h+'</div>';
  }

  /* 这题要用到的知识点、套路：q.tpl ＋ 精解里出现过的 data-kp，按出现顺序去重 */
  function kpIds(q){
    if (q._kp) return q._kp;
    var K=window.EXAM_KP||{}, ids=[], seen={};
    (q.tpl||[]).forEach(function(t){ if(K[t]&&!seen[t]){ seen[t]=1; ids.push(t); } });
    String(q.rich||'').replace(/data-kp="([^"]+)"/g, function(_,id){ id=id.replace(/&amp;/g,'&'); if(K[id]&&!seen[id]){ seen[id]=1; ids.push(id); } });
    return (q._kp=ids);
  }
  /* 跨年字眼：同一张套路卡下，各年真题题干里的原话 → 该想到什么 ＋ 那道题带走的一句（rich_build 自动汇总，写新年份就自动变长） */
  function cueHtml(id, skipNo){
    var c=(window.EXAM_TPL_CUES&&window.EXAM_TPL_CUES[id])||[];
    c=c.filter(function(x){ return !(x[0]===cur&&x[1]===skipNo); });
    if (!c.length) return '';
    return '<details class="cue"'+(c.length<=3?' open':'')+'><summary>真题里的字眼：看到这些话就想到这张卡（'+c.length+' 题）</summary>'+c.map(function(x){
      return '<div class="cue-r"><a href="#y='+x[0]+'&q='+x[1]+'">'+x[0]+'·'+x[1]+'</a><div>'+(x[2]?'<span class="rq">'+x[2]+'</span> <span class="ra">'+x[3]+'</span>':'')+(x[4]?'<p class="cue-t">带走：'+x[4]+'</p>':'')+'</div></div>'; }).join('')+'</details>';
  }
  function kpCard(id, open, skipNo, from){
    var K=window.EXAM_KP[id], u=K.u||(window.EXAM_TPL_USES&&window.EXAM_TPL_USES[id])||[];
    u=u.filter(function(x){ return !(x[0]===cur&&x[1]===skipNo); });
    return '<details class="kc'+(K.k==='tpl'?' tpl':'')+'"'+(open?' open':'')+'><summary><i>'+(K.k==='tpl'?'套路':'知识点')+'</i><b>'+K.t+'</b>'+(from||'')+'</summary><div class="kpc">'+K.h+'</div>'+(K.k==='tpl'?cueHtml(id,skipNo):'')
      + (u.length?'<div class="kpu"><i>'+(skipNo?'别的真题里也用到':'真题里出现在')+'</i>'+u.map(function(x){ return '<a href="#y='+x[0]+'&q='+x[1]+'">'+x[0]+' 第 '+x[1]+' 题</a>'; }).join('')+'</div>':'')+'</details>';
  }
  function kpPanel(q, hint){
    var ids=kpIds(q); if(!ids.length) return '';
    return '<div class="kpall'+(hint?' kpall-h':'')+'"><div class="kpa-h"><b>'+(hint?'提示：这题要用到的':'这题要用到的')+'</b><small>'+ids.length+' 张卡，点标题展开</small><button class="kpa-x" data-kpall>全部展开 / 收起</button></div>'
      + ids.map(function(id){ return kpCard(id, S.set.kpOpen, q.no); }).join('')+'</div>';
  }
  var WHY = C.whyTags || ['概念没记牢','没思路','计算失误','审题漏条件','时间不够','蒙的、不确定'];
  function whyHtml(q){
    var w=ss.why[q.no];
    return '<div class="why"><span>这题的问题出在</span>'+WHY.map(function(x){ return '<button data-why="'+q.no+'" data-w="'+esc(x)+'" class="'+(w===x?'on':'')+'">'+esc(x)+'</button>'; }).join('')+'</div>';
  }
  function notes(){ var o={}; try{ o=JSON.parse(localStorage.getItem(C.key+'_notes'))||{}; }catch(e){} return o; }
  function noteHtml(q){
    var v=notes()[cur+'-'+q.no]||'';
    return '<div class="mynote"><i>我的批注</i><textarea data-note="'+q.no+'" rows="2" placeholder="错在哪一步；下次看到什么，就该想到什么。写在这里，重做这张卷时还在。">'+esc(v)+'</textarea></div>';
  }
  function solHtml(q){
    var h='';
    if (q.type==='choice' && q.ans) h+='<div class="ansline">答案 <b>'+q.ans+'</b></div>';
    else if (q.ansText) h+='<div class="ansline">答案 <b>'+q.ansText+'</b></div>';
    h+=kpPanel(q);
    if (q.rich) {
      var lay = S.set.layer && !ss.done && !ss.lay[q.no] && q.rich.indexOf('rb-steps')>0;
      h+='<div class="rich'+(lay?' lay':'')+'">'+q.rich+'</div>';
      if (lay) h+='<button class="laybtn" data-lay="'+q.no+'">合上自己写一遍，写完再点这里看每一步和考场卷面 ↓</button>';
    }
    if (q.solImg) h+=q.solImg.map(function(s){ return '<img class="pimg" loading="lazy" src="'+s+'" alt="解答">'; }).join('');
    if (q.sol) h+='<div class="sol-b">'+q.sol+'</div>';
    if (q.more) h+='<details class="more"><summary>详解与辨析</summary><div class="sol-b">'+q.more+'</div></details>';
    if (q.solOrig) h+='<details class="more orig"><summary>原书解析（扫描版，备查）</summary>'+q.solOrig.map(function(s){ return '<img class="pimg" loading="lazy" src="'+s+'" alt="原书解析">'; }).join('')+'</details>';
    if (q.solBook) h+='<details class="more orig"><summary>题库原解析（备查）</summary><div class="sol-b">'+q.solBook+(q.moreBook?'<hr>'+q.moreBook:'')+'</div></details>';
    if (q.tag) h+='<div class="kp">考点：'+esc(q.tag)+'</div>';
    var D=ss.done&&deepOf(q.no);
    if (D) h+=deepHtml(D);
    var bk=q.back||(D&&D.back);
    if (bk && ss.done) h+='<a class="bk" href="'+bk.href+'">'+esc(bk.text)+'</a>';
    return h;
  }
  /* 交卷后哪些题值得花时间：失分、没登分、标记过、看过提示、选了错因、精研卡点名必吃透 */
  function needRev(q){
    var v=qScore(q), D=curDeep();
    return v==null || v<q.score || !!ss.flag[q.no] || !!ss.hint[q.no] || !!ss.why[q.no] || !!(D&&D.core&&D.core.indexOf(q.no)>=0);
  }
  function solShown(q){
    var rev=ss.show&&ss.show[q.no], jd=judged(q);
    if (ss.done) return rev!==undefined ? !!rev : needRev(q);   /* 交卷后：只有要复盘的题默认摊开 */
    if (S.set.read) return rev!==false;
    if (jd && q.type==='choice') return !!rev;
    return !!(jd||rev);
  }
  var DEEP_ROWS=[['k','考什么'],['core','本质'],['how','怎么出的'],['vary','举一反三'],['link','联想搭配']];
  var LV={3:['★★★','吃透：错了要重做，举一反三逐条口答'],2:['★★','看懂：读本质和怎么出的'],1:['★','扫过：看一眼本质']};
  function deepHtml(D){
    var rows=DEEP_ROWS.filter(function(r){ return D[r[0]]; });
    if (!rows.length) return '';
    var lv=LV[D.lv]||LV[2];
    return '<div class="deep lv'+(D.lv||2)+'"><div class="dp-h"><b>精研</b><span class="dp-lv">'+lv[0]+'</span><small>'+lv[1]+'</small></div>'
      + rows.map(function(r){ return '<div class="dp-r"><i>'+r[1]+'</i><div>'+D[r[0]]+'</div></div>'; }).join('')+'</div>';
  }
  function selfHtml(q){
    if (q.type==='choice') return '';
    var v = ss.self[q.no];
    if (q.type==='blank') {
      return '<div class="self"><span>这题</span><button data-self="'+q.no+'" data-v="'+q.score+'" class="'+(v===q.score?'ok':'')+'">对 +'+q.score+'</button><button data-self="'+q.no+'" data-v="0" class="'+(v===0?'no':'')+'">错 0</button></div>';
    }
    return '<div class="self"><span>自评得分</span><input type="number" inputmode="numeric" min="0" max="'+q.score+'" data-selfn="'+q.no+'" value="'+(v==null?'':v)+'" placeholder="0–'+q.score+'"><span>/ '+q.score+'</span></div>';
  }
  function qHtml(q){
    var ans = ss.a[q.no], jd = judged(q);
    var h = '<article class="q'+(ss.flag[q.no]?' fl':'')+(ss.at===q.no?' cur':'')+'" id="q'+q.no+'" data-no="'+q.no+'"><div class="qh"><span class="no">'+q.no+'</span>'
      + '<span class="sc">'+q.score+' 分</span>'+tierChip(q)+(ss.done&&q.subj&&C.subjects?'<span class="sb">'+esc(C.subjects[q.subj]||q.subj)+'</span>':'')
      + (P.flagNote&&P.flagNote[q.no]?'<span class="wn">'+esc(P.flagNote[q.no])+'</span>':'')
      + (ss.hint[q.no]?'<span class="hn">看过提示</span>':'')
      + '<button class="flag" data-flag="'+q.no+'" title="标记">'+(ss.flag[q.no]?'★ 已标记':'☆ 标记')+'</button></div>';
    h += tierNote(q);
    if (q.img) h += '<img class="pimg qi" src="'+q.img+'" alt="第 '+q.no+' 题题面">';
    if (q.stem) h += '<div class="stem">'+q.stem+'</div>';
    if (q.origImg) h += '<details class="orig oq"><summary>看原卷题面</summary><img class="pimg" loading="lazy" src="'+q.origImg+'" alt="原卷"></details>';
    if (q.type==='choice') {
      h += '<div class="opts'+(q.opts?'':' opts-l')+'">';
      var L=['A','B','C','D'];
      L.forEach(function(k,i){
        var cls='';
        if (jd) { if (k===q.ans) cls='ok'; else if (k===ans) cls='no'; }
        else if (k===ans) cls='sel';
        h += '<button class="op '+cls+'" data-ans="'+q.no+'" data-k="'+k+'"'+(jd?' disabled':'')+'><b>'+k+'</b>'+(q.opts?'<span>'+q.opts[i]+'</span>':'')+'</button>';
      });
      h += '</div>';
    } else if (q.type==='blank') {
      h += '<div class="inw"><input class="bl" data-txt="'+q.no+'" value="'+esc(ans&&ans!=='✓'?ans:'')+'" placeholder="写答案（也可以写在纸上）"'+(ss.done?' disabled':'')+'><button class="wrote'+(ans==='✓'?' on':'')+'" data-wrote="'+q.no+'"'+(ss.done?' disabled':'')+'>已写在纸上</button></div>';
    } else {
      h += '<div class="inw inw-e"><textarea data-txt="'+q.no+'" rows="4" placeholder="过程写在纸上就行，这里可以记要点"'+(ss.done?' disabled':'')+'>'+esc(ans&&ans!=='✓'?ans:'')+'</textarea><button class="wrote'+(ans==='✓'?' on':'')+'" data-wrote="'+q.no+'"'+(ss.done?' disabled':'')+'>已写完</button></div>';
    }
    /* 解答区 */
    var canShowBtn = !ss.done && (S.set.showSol || S.set.read);
    var showNow = solShown(q), acts='';
    if (!ss.done && S.set.instant && q.type!=='choice' && !ss.open[q.no] && isDone(q)) {
      acts += '<button class="solb pri" data-reveal="'+q.no+'">写完了，对答案</button>';
    } else if (canShowBtn || (jd && q.type==='choice' && !ss.done) || ss.done) {
      acts += '<button class="solb" data-sol="'+q.no+'">'+(showNow?'收起解析':'看解析')+'</button>';
    }
    var canHint = !ss.done && S.set.hint && !showNow && kpIds(q).length;
    if (canHint) acts += '<button class="solb hintb" data-hint="'+q.no+'">'+(ss.hint[q.no]===2?'收起提示':'提示：要用的知识点')+'</button>';
    if (acts) h += '<div class="acts">'+acts+'</div>';
    if (canHint && ss.hint[q.no]===2) h += kpPanel(q, 1);
    if (ss.done && !showNow) { var G=deepOf(q.no); h += '<div class="gist"><i>做对了，过一眼这行就走</i>'+(G&&G.core?G.core:'想再看一遍就点「看解析」。')+'</div>'; }
    if (showNow) h += '<div class="sol"><span class="soltab">解析</span>'+solHtml(q)+(jd||ss.done?selfHtml(q)+whyHtml(q):'')+noteHtml(q)
      + '<div class="solend"><button class="solb" data-sol="'+q.no+'">收起解析</button><button class="solb" data-step="1">下一题 →</button></div></div>';
    return h + '</article>';
  }
  function sheet(){
    var secs=[];
    P.q.forEach(function(q){ var t=q.type; if(!secs.length||secs[secs.length-1].t!==t) secs.push({t:t,q:[]}); secs[secs.length-1].q.push(q); });
    var nm={choice:'选择',blank:'填空',essay:C.essayName||'解答'};
    return secs.map(function(s){
      return '<div class="shs"><i>'+nm[s.t]+'</i><div>'+s.q.map(function(q){
        var c='';
        if (judged(q)&&q.type==='choice') c=ss.a[q.no]===q.ans?'ok':'no';
        else if (judged(q)&&qScore(q)!=null) c=qScore(q)>=q.score?'ok':qScore(q)>0?'mid':'no';
        else if (ss.done&&!isDone(q)) c='no';
        else if (isDone(q)) c='dn';
        return '<a href="javascript:;" data-go="'+q.no+'" class="'+c+(ss.flag[q.no]?' fl':'')+(ss.at===q.no?' cur':'')+'">'+q.no+'</a>';
      }).join('')+'</div></div>';
    }).join('');
  }
  function drawPaper(){
    ss.hint=ss.hint||{}; ss.why=ss.why||{}; ss.lay=ss.lay||{}; ss.show=ss.show||{}; ss.qt=ss.qt||{};
    var answered = P.q.filter(isDone).length;
    root.innerHTML = '<div class="bar"><a class="bk0" href="#">← 选卷</a><b class="ttl">'+cur+'</b>'
      + '<span class="timer" id="timer"></span><span class="qtm" id="qtm"></span><button class="ghost" id="pause"></button>'
      + '<span class="prog" id="prog"></span><span class="live" id="live"></span>'
      + '<span class="cdb" id="cdb"></span>'
      + '<span class="rt"><button class="ghost" id="night">夜</button><button class="ghost" id="gear">模式 · 开关</button><button class="ghost sh-b" id="shb">答题卡</button><button class="sub" id="submit">'+(ss.done?'成绩':'交卷')+'</button></span></div>'
      + '<div class="gearp tgbox" id="gearp" hidden>'+togglesHtml()+'</div>'
      + '<div class="pp"><main id="pm"></main><aside id="sheet"></aside></div>'
      + '<div class="pause-m" id="pm-o" hidden><div><b>已暂停</b><p>卷面先遮住，回来继续。</p><button class="sub" id="resume">继续</button></div></div>'
      + '<div class="onenav" id="onenav"><button class="ghost" data-step="-1">← 上一题</button><span id="onepos"></span><button class="ghost" data-step="1">下一题 →</button></div>'
      + '<div class="modal" id="modal" hidden></div>';
    applySet();
    redrawPaper();
    startTimer();
    if (location.hash.indexOf('q=')>0) go(+location.hash.split('q=')[1]);
    else window.scrollTo(0,0);
  }
  function legendHtml(){
    return '<details class="lgd"><summary>解析里的记号怎么读 · 快捷键</summary><div class="lgd-b">'
      + '<p><span class="rq">黄色划线</span> 题目里该圈出来的话　<span class="ra">蓝色楷体</span> 读到这句该想到什么　<span class="circ">红圈</span> 关键量　<span class="wavy">波浪线</span> 容易看漏　<span class="omit">灰色</span> 考场上可以不写　图注开头写着「考场上画 / 草稿上列 / 看懂就行」，前两种才需要自己动笔　<span class="fast">橙色</span> 秒杀做法　<span class="pt">2 分</span> 采分点　<button class="kpb" type="button">蓝色虚线</button> 点开是知识点　<button class="kpb tplb" type="button">紫框</button> 点开是跨年套路</p>'
      + '<p class="keys">键盘：<kbd>←</kbd><kbd>→</kbd> 或 <kbd>K</kbd><kbd>J</kbd> 上一题、下一题　<kbd>A</kbd><kbd>B</kbd><kbd>C</kbd><kbd>D</kbd> 选当前题　<kbd>S</kbd> 看 / 收起解析　<kbd>H</kbd> 提示　<kbd>F</kbd> 标记　<kbd>Esc</kbd> 关掉知识点卡</p></div></details>';
  }
  function redrawPaper(){
    if (!$('pm')) return;
    var y=window.scrollY, h='', last=null, nm=P.secName||{};
    if (ss.done) h += reportHtml();
    if (P.note) h += '<div class="pnote">'+P.note+'</div>';
    h += legendHtml();
    var filter = ss.filter||'all';
    P.q.forEach(function(q){
      if (q.type!==last) { h+='<h3 class="sech">'+esc(nm[q.type]||'')+'</h3>'; last=q.type; }
      if (ss.done && filter==='wrong' && (qScore(q)===q.score)) return;
      if (ss.done && filter==='flag' && !ss.flag[q.no]) return;
      if (ss.done && filter==='core') { var cd=curDeep(); if(cd&&cd.core&&cd.core.indexOf(q.no)<0&&!(qScore(q)!=null&&qScore(q)<q.score)) return; }
      h += qHtml(q);
    });
    if (!ss.done) h += '<button class="sub sub-end" id="submit2">交卷</button>';
    $('pm').innerHTML = h;
    typeset($('pm'));
    updateSide();
    var vis=visNos(); if (vis.indexOf(ss.at)<0) ss.at=vis[0];
    setCur(ss.at);
    window.scrollTo(0,y);
  }
  /* 公式排版：任何往页面里塞 HTML 的地方都要过一遍，否则 <span class="m"> 里的 TeX 会原样露出来 */
  function typeset(el){ if (window.renderMathInElement && el) try{ window.renderMathInElement(el,{throwOnError:false}); }catch(e){} }
  function qOf(no){ return P.q.filter(function(x){ return x.no===no; })[0]; }
  function redrawQ(no){
    var el=$('q'+no), q=qOf(no);
    if (el&&q) { var t=document.createElement('div'); t.innerHTML=qHtml(q); var nu=t.firstChild; el.parentNode.replaceChild(nu,el); typeset(nu); }
    updateSide();
  }
  function visNos(){ return [].map.call(document.querySelectorAll('#pm .q'), function(el){ return +el.getAttribute('data-no'); }); }
  function curNo(){
    var vis=visNos();
    if (S.set.view==='one') return vis.indexOf(ss.at)>=0?ss.at:vis[0];
    var els=document.querySelectorAll('#pm .q');
    for (var i=0;i<els.length;i++) if (els[i].getBoundingClientRect().bottom>110) return +els[i].getAttribute('data-no');
    return vis[vis.length-1];
  }
  function setCur(no){
    if (no==null) return;
    ss.at=no;
    document.querySelectorAll('#pm .q').forEach(function(el){ el.classList.toggle('cur', +el.getAttribute('data-no')===no); });
    document.querySelectorAll('#sheet [data-go]').forEach(function(a){ a.classList.toggle('cur', +a.getAttribute('data-go')===no); });
    var vis=visNos(), op=$('onepos'); if (op) op.textContent='第 '+no+' 题 · '+(vis.indexOf(no)+1)+' / '+vis.length;
  }
  function step(d){ var vis=visNos(), i=vis.indexOf(curNo()), n=vis[i+d]; if (n!=null) go(n); }
  var scT; window.addEventListener('scroll', function(){
    if (!cur||!ss||S.set.view==='one') return;
    clearTimeout(scT); scT=setTimeout(function(){ if(cur&&$('pm')) setCur(curNo()); },120);
  }, {passive:true});
  function updateSide(){
    if ($('sheet')) $('sheet').innerHTML='<div class="sh-t">答题卡</div>'+sheet()+'<div class="shl"><i class="k cu"></i>当前 <i class="k dn"></i>已答 <i class="k fl"></i>标记'+(S.set.instant||ss.done?' <i class="k ok"></i>对 <i class="k no"></i>错':'')+'</div>';
    var n=P.q.filter(isDone).length;
    if ($('prog')) $('prog').textContent='已答 '+n+' / '+P.q.length;
    if ($('live')) $('live').textContent=(S.set.instant||ss.done)?'得分 '+liveScore():'';
    if ($('cdb')) { $('cdb').textContent=S.set.showCount?countText():''; }
    if ($('submit')) $('submit').textContent=ss.done?'成绩':'交卷';
  }
  function go(no){
    var el=$('q'+no);
    if (!el && ss && ss.done && ss.filter && ss.filter!=='all') { ss.filter='all'; redrawPaper(); el=$('q'+no); }
    if (el) { setCur(no); var y=el.getBoundingClientRect().top+window.scrollY-64; window.scrollTo({top:y,behavior:S.set.view==='one'?'auto':'smooth'}); }
    document.body.classList.remove('sh-open');
  }

  /* —— 计时 —— */
  function startTimer(){ stopTimer(); lastTick=Date.now(); tm=setInterval(tick,1000); tick(); }
  function stopTimer(){ if(tm) clearInterval(tm); tm=null; }
  var lastSave=0;
  function tick(){
    if (!cur||!ss) { var cx=$('cdx'); if(cx) cx.textContent=countText()+'　·　'+C.examWhen; return; }
    var now=Date.now();
    if (!paused && !ss.done && S.set.timer!=='off') ss.secs+=(now-lastTick)/1000;
    var qn=ss.at, qq=qn!=null&&P&&qOf(qn), qt=$('qtm');
    if (qq && !paused && !ss.done && !S.set.read && !judged(qq) && now-lastTick<5000) { ss.qt=ss.qt||{}; ss.qt[qn]=(ss.qt[qn]||0)+(now-lastTick)/1000; }
    if (qt) { var tq=qq&&tierOf(qn), uq=(ss.qt&&ss.qt[qn])||0;
      if (tq&&S.set.tier&&!ss.done&&!S.set.read) { qt.textContent='本题 '+fmt(uq)+' / '+tq.m+' 分'; qt.classList.toggle('ov', uq>tq.m*60); } else qt.textContent=''; }
    lastTick=now;
    var t=$('timer'), lim=C.minutes*60;
    if (t) {
      if (S.set.timer==='off') t.textContent='';
      else if (S.set.timer==='up' || ss.done) t.textContent=fmt(ss.secs);
      else { var r=lim-ss.secs; t.textContent=r>=0?fmt(r):'超时 '+fmt(-r); t.classList.toggle('warn',r<600); }
    }
    var pb=$('pause'); if(pb){ pb.textContent=paused?'继续':'暂停'; pb.hidden=ss.done||S.set.timer==='off'; }
    if (S.set.timer==='down' && !ss.done && ss.secs>=lim && !warned) {
      warned=true;
      if (S.set.autoEnd) doSubmit(); else flash('时间到了。可以继续写，超时部分会算进用时。');
    }
    if (now-lastSave>5000) { lastSave=now; save(); }
  }
  function flash(msg){
    var m=$('modal'); if(!m) return;
    m.hidden=false; m.innerHTML='<div class="mbox"><p>'+esc(msg)+'</p><div class="mact"><button class="sub" data-close>知道了</button></div></div>';
  }

  /* —— 交卷 —— */
  function askSubmit(){
    if (ss.done) { window.scrollTo({top:0,behavior:'smooth'}); return; }
    var miss=P.q.filter(function(q){ return !isDone(q); });
    var m=$('modal'); m.hidden=false;
    if (miss.length && S.set.mustAll) {
      m.innerHTML='<div class="mbox"><b>还有 '+miss.length+' 题没答，现在不能交卷</b><div class="missl">'+miss.map(function(q){ return '<a href="javascript:;" data-go="'+q.no+'" data-close>'+q.no+'</a>'; }).join('')+'</div><p class="hint">「必须答完才能交卷」开着。写在纸上的题点「已写完」。</p><div class="mact"><button class="ghost" data-close>继续做题</button></div></div>';
      return;
    }
    m.innerHTML='<div class="mbox"><b>确认交卷？</b><p>'+(miss.length?'还有 '+miss.length+' 题没答，交卷后按 0 分算。':'全部答完了。')+'</p><div class="mact"><button class="ghost" data-close>再看看</button><button class="sub" id="confirm">交卷</button></div></div>';
  }
  function doSubmit(){
    ss.done=true; ss.show={}; ss.doneAt=Date.now();
    P.q.forEach(function(q){ if(q.type!=='choice'&&!isDone(q)) ss.self[q.no]=0; });
    recordHist();
    save(); paused=false;
    var m=$('modal'); if(m) m.hidden=true;
    redrawPaper(); window.scrollTo(0,0);
  }
  function recordHist(){
    var pend=P.q.filter(function(q){ return q.type!=='choice'&&ss.self[q.no]==null; }).length;
    var rec={y:cur,score:liveScore(),full:fullScore(),secs:Math.round(ss.secs),at:ss.doneAt||Date.now(),pend:pend};
    var i=-1; S.hist.forEach(function(h,k){ if(h.y===cur&&h.at===rec.at) i=k; });
    if(i>=0) S.hist[i]=rec; else S.hist.push(rec);
    if (C.onScore) try{ C.onScore(cur,P,ss,liveScore()); }catch(e){}
    save();
  }
  function reportHtml(){
    var score=liveScore(), full=fullScore();
    var groups={};
    P.q.forEach(function(q){
      var g=(C.subjects&&q.subj)?C.subjects[q.subj]:({choice:'选择',blank:'填空',essay:'解答'})[q.type];
      groups[g]=groups[g]||{s:0,f:0,w:0,p:0};
      groups[g].f+=q.score; var v=qScore(q);
      if(v==null) groups[g].p++; else { groups[g].s+=v; if(v<q.score) groups[g].w++; }
    });
    var pend=P.q.filter(function(q){ return qScore(q)==null; }).length;
    var rows=Object.keys(groups).map(function(g){ var o=groups[g]; return '<tr><td>'+g+'</td><td><b>'+o.s+'</b> / '+o.f+'</td><td><i class="gb"><i style="width:'+(100*o.s/o.f)+'%"></i></i></td><td>'+(o.w?'失分 '+o.w+' 题':'全对')+(o.p?'，待评 '+o.p:'')+'</td></tr>'; }).join('');
    var wrong=P.q.filter(function(q){ var v=qScore(q); return v!=null&&v<q.score; });
    return '<section class="rep" id="report"><div class="rep-h"><div class="big"><strong>'+score+'</strong><span>/ '+full+'</span></div><div><b>'+cur+' 年真题'+(C.target?'，目标 '+C.target:'')+'</b><br>用时 '+fmt(ss.secs)+(pend?'<br><em>还有 '+pend+' 题没登分，在下面每题解答下自评，分数会跟着变</em>':'')+'</div></div>'
      + '<div class="tabw"><table class="rp"><tbody>'+rows+'</tbody></table></div>'
      + (wrong.length?'<p class="wr">失分题：'+wrong.map(function(q){ return '<a href="javascript:;" data-go="'+q.no+'">'+q.no+'</a>'; }).join(' ')+'</p>':'')
      + tierRep() + whyStat() + studyHtml() + kpListHtml(wrong)
      + '<p class="repn">下面只把<b>失分、标记过、看过提示、必吃透</b>的题摊开；做对的题收成一行「本质」，要看再点开。解析太长就在「模式 · 开关」里点「精简」。</p>'
      + '<div class="rep-a"><span class="seg">'+[['all','全部'],['wrong','只看失分'],['flag','只看标记']].concat(curDeep()&&curDeep().core?[['core','只看必吃透']]:[]).map(function(o){ return '<button data-filter="'+o[0]+'" class="'+((ss.filter||'all')===o[0]?'on':'')+'">'+o[1]+'</button>'; }).join('')+'</span><button class="ghost" id="redo">重做这一年</button></div></section>';
  }
  function whyStat(){
    var c={}, n=0; P.q.forEach(function(q){ var w=ss.why[q.no]; if(w){ c[w]=(c[w]||[]); c[w].push(q.no); n++; } });
    if (!n) return '';
    return '<p class="whys"><b>失分原因</b>'+Object.keys(c).sort(function(a,b){ return c[b].length-c[a].length; }).map(function(w){
      return '<span>'+esc(w)+' ×'+c[w].length+'（'+c[w].map(function(x){ return '<a href="javascript:;" data-go="'+x+'">'+x+'</a>'; }).join(' ')+'）</span>'; }).join('')+'</p>';
  }
  /* 交卷后：把失分题（没有失分就整卷）牵涉的知识点、套路汇成一张清单，每张标着来自哪几题 */
  function kpListHtml(wrong){
    var src=wrong.length?wrong:P.q, map={}, order=[];
    src.forEach(function(q){ kpIds(q).forEach(function(id){ if(!map[id]){ map[id]=[]; order.push(id); } map[id].push(q.no); }); });
    if (!order.length) return '';
    order.sort(function(a,b){ return map[b].length-map[a].length; });
    return '<details class="kplist"><summary><b>'+(wrong.length?'失分题牵涉的知识点与套路':'这张卷用到的知识点与套路')+'</b>　'+order.length+' 张，复盘前先过一遍</summary><div class="kpall"><div class="kpa-h"><small>出现次数多的排前面</small><button class="kpa-x" data-kpall>全部展开 / 收起</button></div>'
      + order.map(function(id){ return kpCard(id, false, null, '<em>第 '+map[id].join('、')+' 题</em>'); }).join('')+'</div></details>';
  }
  /* 首页进来的速查本：全部卡片，可搜 */
  function kpBook(){
    stopTimer(); cur=null; applySet(); document.title='知识点与套路速查 · '+C.title;
    var K=window.EXAM_KP||{}, ids=Object.keys(K);
    var grp=function(tpl){ return ids.filter(function(id){ return (K[id].k==='tpl')===tpl; }).map(function(id){ return kpCard(id,false,null); }).join(''); };
    root.innerHTML='<div class="hm kpbook"><div class="hm-top"><a href="#">← 选卷</a><span>知识点与套路速查</span><button class="ghost" id="night">夜</button></div>'
      + '<p class="kpb-lead">精解里点得开的卡片都在这里。先看标题自己回忆，想不起来再点开。</p>'
      + '<input class="kpq" id="kpq" type="search" placeholder="搜：泰勒、特征值、缺页、滑动窗口…" autocomplete="off">'
      + '<h2>套路（跨年反复出现的做法）</h2><div class="kpall" id="kpg1">'+grp(true)+'</div>'
      + '<h2>知识点 · 公式 · 常用结论</h2><div class="kpall" id="kpg2">'+grp(false)+'</div></div>';
    root.querySelectorAll('.kc>summary').forEach(typeset);   /* 标题里的公式先排，卡片正文等展开再排 */
    window.scrollTo(0,0);
  }
  document.addEventListener('input', function(e){
    if (e.target.id!=='kpq') return;
    var v=e.target.value.trim().toLowerCase();
    document.querySelectorAll('.kpbook .kc').forEach(function(d){ d.hidden=!!v && d.textContent.toLowerCase().indexOf(v)<0; });
  });
  /* 折叠卡是懒排版的：展开时再排公式（速查本有几百张卡，一次排完太慢） */
  document.addEventListener('toggle', function(e){ var d=e.target; if (d.open && d.classList && d.classList.contains('kc')) typeset(d); }, true);
  function curDeep(){ return cur&&window.EXAM_DEEP&&window.EXAM_DEEP[cur]; }
  function studyHtml(){
    var D=curDeep();
    if (!D) return C.deepPath?'<div class="study st0">这张卷的精研还没写，先按通用路线复盘：对答案 → 错题不看解析重做 → 读解答找卡点 → 记一行到错题本。</div>':'';
    var wrong=P.q.filter(function(q){ var v=qScore(q); return v!=null&&v<q.score; }).map(function(q){ return q.no; });
    var core=(D.core||[]), must=core.slice();
    wrong.forEach(function(n){ if(must.indexOf(n)<0) must.push(n); });
    must.sort(function(a,b){ return a-b; });
    var lnk=function(n){ var w=wrong.indexOf(n)>=0, c=core.indexOf(n)>=0; return '<a href="javascript:;" data-go="'+n+'" class="'+(w?'w':'')+(c?' c':'')+'">'+n+'</a>'; };
    return '<div class="study"><div class="st-h"><b>这张卷怎么复盘</b>'+(D.time?'<span>限时 '+D.time+' 分钟，到点就停</span>':'')+'</div>'
      + (D.look?'<p class="st-look">'+D.look+'</p>':'')
      + '<div class="st-must"><i>今天必过</i><div>'+must.map(lnk).join('')+'</div><small>必吃透 '+core.length+' 题（下划线）＋ 你的失分题（红）。其余题只扫「本质」一行。</small></div>'
      + (D.route&&D.route.length?'<ol class="st-r">'+D.route.map(function(r){ return '<li>'+r+'</li>'; }).join('')+'</ol>':'')
      + '</div>';
  }
  function showReport(){ drawPaper(); }

  /* —— 知识点 / 套路弹窗 —— */
  function kpClose(){ var o=$('kpop'); if(o) o.remove(); }
  function kpOpen(btn){
    var id=btn.getAttribute('data-kp'), K=window.EXAM_KP&&window.EXAM_KP[id];
    kpClose(); if(!K) return;
    var u=K.u||(window.EXAM_TPL_USES&&window.EXAM_TPL_USES[id]);
    var o=document.createElement('div'); o.id='kpop'; o.className='kpop'+(K.k==='tpl'?' tpl':'');
    o.innerHTML='<div class="kph"><i>'+(K.k==='tpl'?'套路':'知识点')+'</i><b>'+K.t+'</b><button class="kpx" data-kpx>×</button></div><div class="kpc">'+K.h+'</div>'+(K.k==='tpl'?cueHtml(id,null):'')
      +(u&&u.length?'<div class="kpu"><i>真题里出现在</i>'+u.map(function(x){ return '<a href="#y='+x[0]+'&q='+x[1]+'">'+x[0]+' 第 '+x[1]+' 题</a>'; }).join('')+'</div>':'');
    document.body.appendChild(o);
    typeset(o);
    var r=btn.getBoundingClientRect(), W=Math.min(460, window.innerWidth-24);
    o.style.width=W+'px';
    var left=Math.max(12, Math.min(r.left+window.scrollX, window.scrollX+window.innerWidth-W-12));
    o.style.left=left+'px';
    var top=r.bottom+window.scrollY+6;
    if (r.bottom+o.offsetHeight+12>window.innerHeight && r.top>o.offsetHeight+12) top=r.top+window.scrollY-o.offsetHeight-6;
    o.style.top=top+'px';
  }
  document.addEventListener('keydown', function(e){
    if (e.key==='Escape') { kpClose(); return; }
    if (!cur||!ss||e.metaKey||e.ctrlKey||e.altKey) return;
    var tg=e.target.tagName; if (tg==='INPUT'||tg==='TEXTAREA'||tg==='SELECT') return;
    var m=$('modal'); if ((m&&!m.hidden)||paused) return;
    var k=e.key.length===1?e.key.toLowerCase():e.key, no=curNo(), q=qOf(no), el=$('q'+no), b;
    if (k==='ArrowRight'||k==='j') { e.preventDefault(); step(1); }
    else if (k==='ArrowLeft'||k==='k') { e.preventDefault(); step(-1); }
    else if (!el||!q) return;
    else if ('abcd'.indexOf(k)>=0 && k.length===1 && q.type==='choice') { b=el.querySelector('[data-k="'+k.toUpperCase()+'"]'); if(b&&!b.disabled) b.click(); }
    else if (k==='s') { b=el.querySelector('[data-sol],[data-reveal]'); if(b) b.click(); }
    else if (k==='h') { b=el.querySelector('[data-hint]'); if(b) b.click(); }
    else if (k==='f') { b=el.querySelector('[data-flag]'); if(b) b.click(); }
  });
  /* —— 事件 —— */
  document.addEventListener('click', function(e){
    var t=e.target, b;
    if ((b=t.closest&&t.closest('.kpb'))) { e.preventDefault(); kpOpen(b); return; }
    if (t.closest&&t.closest('[data-kpx]')) { kpClose(); return; }
    if ((b=t.closest&&t.closest('.va'))) { b.classList.toggle('on'); return; }
    if (!(t.closest&&t.closest('#kpop'))) kpClose();
    if (t.id==='night'||t.closest&&t.closest('#night')) { var n=document.documentElement.getAttribute('data-theme')==='night'?'':'night'; document.documentElement.setAttribute('data-theme',n); try{localStorage.setItem(C.key+'_night',n);}catch(x){} return; }
    if (!cur) return;
    if ((b=t.closest('[data-ans]'))) {
      var no=+b.getAttribute('data-ans'), q=P.q.filter(function(x){ return x.no===no; })[0];
      if (judged(q)&&q.type==='choice') return;
      ss.a[no]=ss.a[no]===b.getAttribute('data-k')?undefined:b.getAttribute('data-k');
      if(ss.a[no]===undefined) delete ss.a[no];
      setCur(no); save();
      if (judged(q)) { if (S.set.autoSol) ss.show[no]=true; redrawQ(no); }
      else {   /* 还没判分：只换选中态，不重画整题（解析、展开的卡片都留在原处） */
        b.parentNode.querySelectorAll('.op').forEach(function(x){ x.classList.toggle('sel', x.getAttribute('data-k')===ss.a[no]); });
        updateSide();
      }
      return;
    }
    if ((b=t.closest('[data-flag]'))) {
      var fn=+b.getAttribute('data-flag'); ss.flag[fn]=!ss.flag[fn]; save();
      b.textContent=ss.flag[fn]?'★ 已标记':'☆ 标记'; b.closest('.q').classList.toggle('fl', !!ss.flag[fn]); updateSide(); setCur(ss.at); return;
    }
    if ((b=t.closest('[data-step]'))) { var art=b.closest('.q'); if (art) setCur(+art.getAttribute('data-no')); step(+b.getAttribute('data-step')); return; }
    if ((b=t.closest('[data-kpall]'))) { var ds=b.closest('.kpall').querySelectorAll('details.kc'), any=[].some.call(ds,function(d){ return !d.open; }); ds.forEach(function(d){ d.open=any; }); return; }
    if ((b=t.closest('[data-hint]'))) { var hn=+b.getAttribute('data-hint'); ss.hint[hn]=ss.hint[hn]===2?1:2; save(); redrawQ(hn); return; }
    if ((b=t.closest('[data-lay]'))) { var ln=+b.getAttribute('data-lay'); ss.lay[ln]=1; var rc=b.previousElementSibling; if(rc) rc.classList.remove('lay'); b.remove(); return; }
    if ((b=t.closest('[data-why]'))) { var yn=+b.getAttribute('data-why'), w=b.getAttribute('data-w'); if(ss.why[yn]===w) delete ss.why[yn]; else ss.why[yn]=w; save(); b.parentNode.querySelectorAll('button').forEach(function(x){ x.classList.toggle('on', x.getAttribute('data-w')===ss.why[yn]); }); return; }
    if ((b=t.closest('[data-go]'))) { go(+b.getAttribute('data-go')); if(b.hasAttribute('data-close')) $('modal').hidden=true; return; }
    if ((b=t.closest('[data-close]'))) { $('modal').hidden=true; return; }
    if ((b=t.closest('[data-sol]'))) {
      var sn=+b.getAttribute('data-sol'); ss.show=ss.show||{};
      var q2=qOf(sn), now=solShown(q2);
      ss.show[sn]=!now; if(judged(q2)&&q2.type!=='choice'&&!ss.done&&!S.set.read) ss.open[sn]=ss.show[sn];
      setCur(sn); redrawQ(sn);
      if (now) { var qe=$('q'+sn); if (qe && qe.getBoundingClientRect().top<0) go(sn); }   /* 从解析底下收起时，别把人甩到下一题中间 */
      return;
    }
    if ((b=t.closest('[data-reveal]'))) { var rn=+b.getAttribute('data-reveal'); ss.open[rn]=1; ss.show=ss.show||{}; ss.show[rn]=true; save(); redrawQ(rn); return; }
    if ((b=t.closest('[data-wrote]'))) { var wn=+b.getAttribute('data-wrote'); if(ss.a[wn]==='✓') delete ss.a[wn]; else ss.a[wn]='✓'; save(); redrawQ(wn); return; }
    if ((b=t.closest('[data-self]'))) { var fn2=+b.getAttribute('data-self'); ss.self[fn2]=+b.getAttribute('data-v'); if(ss.done) recordHist(); save();
      b.parentNode.querySelectorAll('button').forEach(function(x){ var on=x===b; x.classList.toggle('ok', on&&+x.getAttribute('data-v')>0); x.classList.toggle('no', on&&+x.getAttribute('data-v')===0); });
      updateSide(); setCur(ss.at); var bg=document.querySelector('.rep .big strong'); if(bg) bg.textContent=liveScore(); refreshTier(); return; }
    if ((b=t.closest('[data-filter]'))) { ss.filter=b.getAttribute('data-filter'); redrawPaper(); return; }
    if (t.id==='submit'||t.id==='submit2') { askSubmit(); return; }
    if (t.id==='confirm') { doSubmit(); return; }
    if (t.id==='gear') { $('gearp').hidden=!$('gearp').hidden; return; }
    if (t.id==='shb') { document.body.classList.toggle('sh-open'); return; }
    if (t.id==='pause'||t.id==='resume') { paused=!paused; $('pm-o').hidden=!paused; tick(); return; }
    if (t.id==='redo') {
      var m=$('modal'); m.hidden=false;
      m.innerHTML='<div class="mbox"><b>重做 '+cur+' 年？</b><p>这张卷的作答清空，成绩记录保留。</p><div class="mact"><button class="ghost" data-close>算了</button><button class="sub" id="redo2">重做</button></div></div>';
      return;
    }
    if (t.id==='redo2') { delete S.sess[cur]; save(); warned=false; open(cur); return; }
  });
  document.addEventListener('input', function(e){
    var t=e.target, k;
    if (!cur) return;
    if ((k=t.getAttribute('data-note'))) { var o=notes(); if(t.value.trim()) o[cur+'-'+k]=t.value; else delete o[cur+'-'+k]; try{ localStorage.setItem(C.key+'_notes',JSON.stringify(o)); }catch(x){} return; }
    if ((k=t.getAttribute('data-txt'))) { if(t.value.trim()) ss.a[k]=t.value; else delete ss.a[k]; lazySave(); updateSide(); return; }
    if ((k=t.getAttribute('data-selfn'))) {
      var q=P.q.filter(function(x){ return x.no===+k; })[0];
      if (t.value==='') delete ss.self[k]; else ss.self[k]=Math.max(0,Math.min(q.score,+t.value));
      if (ss.done) recordHist();
      lazySave(); updateSide();
      var big=document.querySelector('.rep .big strong'); if(big) big.textContent=liveScore(); refreshTier();
    }
  });
  var lz; function lazySave(){ clearTimeout(lz); lz=setTimeout(save,400); }
  window.addEventListener('pagehide', save);

  function route(){
    var m=location.hash.match(/y=(\d{4})/);
    warned=false; paused=false;
    document.body.classList.remove('sh-open'); kpClose();
    if (m) open(+m[1]); else if (location.hash==='#kp') kpBook(); else home();
  }
  window.addEventListener('hashchange', route);
  try { var nt=localStorage.getItem(C.key+'_night'); if(nt) document.documentElement.setAttribute('data-theme',nt); } catch(e){}
  setInterval(function(){ if(!cur){ tick(); } else if($('cdb')&&S.set.showCount){ $('cdb').textContent=countText(); } },30000);
  route();
})();
