/* 在线真题套卷引擎：408 与数学一共用，各自的 EXAM_CONF 写在页面里，卷子数据按年放在 assets/exam/yYYYY.js。
 * 题目字段：no 题号 / type choice|blank|essay / score / subj / stem(html) 或 img(题面图) / opts / ans
 *           sol(html，解答) / more(html，详解，可省) / solImg(解答图数组) / tag(考点) / back({href,text})
 * 精研（可选）：C.deepPath 指向 deep/dYYYY.js，设 EXAM_DEEP[年] = {time,look,route[],core[],q:{题号:{lv,k,core,how,vary,link,back}}}，交卷后才显示。
 * 做卷顺序（可选）：C.plan = {order:[[年,档]],tiers:{档:{name,min,desc}},rhythm,cut,pace} */
(function(){
  'use strict';
  var C = window.EXAM_CONF, KEY = C.key + '_exam_v1';
  var $ = function(i){ return document.getElementById(i); };
  var root = $('app');
  var DEF = { showSol:false, mustAll:false, instant:false, timer:'down', autoEnd:false, showCount:true };

  function load(){
    var o = {};
    try { o = JSON.parse(localStorage.getItem(KEY)) || {}; } catch(e){}
    o.set = Object.assign({}, DEF, o.set||{}); o.sess = o.sess||{}; o.hist = o.hist||[];
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
    ['showSol','每题下面显示「解答」按钮','关着时做题中看不到解答，交卷后才能看。'],
    ['mustAll','必须全部答完才能交卷','有题没答时交卷按钮只列出缺的题，不让交。解答题写在纸上的，点「已写完」就算答过。'],
    ['instant','当场结算','选完立刻判对错、累计得分，答案锁定。填空和解答题写完就能对答案、当场登分。关着时等交卷统一结算。'],
    ['showCount','显示距考试倒计时','顶栏一直显示还剩多少天。'],
    ['autoEnd','时间到自动交卷','倒计时走完直接交卷，不看有没有答完。关着时只提醒，可继续写。']
  ];
  function togglesHtml(){
    var h = TOGGLES.map(function(t){
      return '<label class="tg"><input type="checkbox" data-set="'+t[0]+'"'+(S.set[t[0]]?' checked':'')+'><span class="sw"></span><span class="tx"><b>'+t[1]+'</b><small>'+t[2]+'</small></span></label>';
    }).join('');
    h += '<div class="tg tg-sel"><span class="tx"><b>计时</b><small>考试时长 '+C.minutes+' 分钟，可以中途暂停。</small></span><span class="seg" role="group">'
      + [['down','倒计时'],['up','正计时'],['off','不计时']].map(function(o){ return '<button data-timer="'+o[0]+'" class="'+(S.set.timer===o[0]?'on':'')+'">'+o[1]+'</button>'; }).join('')
      + '</span></div>';
    return h;
  }
  document.addEventListener('change', function(e){
    var k = e.target.getAttribute && e.target.getAttribute('data-set');
    if (!k) return;
    S.set[k] = e.target.checked; save();
    document.querySelectorAll('[data-set="'+k+'"]').forEach(function(x){ x.checked = e.target.checked; });
    if (cur) redrawPaper();
  });
  document.addEventListener('click', function(e){
    var b = e.target.closest && e.target.closest('[data-timer]');
    if (!b) return;
    S.set.timer = b.getAttribute('data-timer'); save();
    document.querySelectorAll('[data-timer]').forEach(function(x){ x.classList.toggle('on', x===b||x.getAttribute('data-timer')===S.set.timer); });
    tick();
  });

  /* —— 首页 —— */
  function home(){
    stopTimer(); cur=null; document.title = C.title;
    var left = daysLeft();
    var rows = C.years.slice().reverse().map(function(y){
      var hs = S.hist.filter(function(h){ return h.y===y; });
      var best = hs.length ? Math.max.apply(null, hs.map(function(h){ return h.score; })) : null;
      var ss = S.sess[y], going = ss && !ss.done && Object.keys(ss.a||{}).length;
      var info = (C.yearNote && C.yearNote[y]) || '';
      return '<a class="yr'+(best!=null?' dn':'')+(going?' go':'')+'" href="#y='+y+'"><b>'+y+'</b>'
        + '<span>'+(going?'做到 '+Object.keys(ss.a).length+' 题，继续':best!=null?'最高 '+best+' 分':'未做')+'</span>'
        + (info?'<em>'+esc(info)+'</em>':'')
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
      + '<h2>开关</h2><div class="tgs">'+togglesHtml()+'</div>'
      + '<h2>选一年</h2><div class="yrs">'+rows+'</div>'
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
        + '<td><span class="tier t-'+it[1]+'">'+esc(t.name||it[1])+'</span></td><td>'+(t.min?'复盘 '+t.min+' 分':'')+'</td>'
        + '<td>'+(st==='dn'?'✓ 做过':st==='nx'?'← 下一张':'')+(dp?'':' <small class="nod">精研待写</small>')+'</td></tr>';
    }).join('');
    var tiers=Object.keys(L.tiers).map(function(k){ var t=L.tiers[k]; return '<li><span class="tier t-'+k+'">'+esc(t.name)+'</span> '+t.desc+'</li>'; }).join('');
    return '<div class="pl-set"><label>开始做卷的日子 <input type="date" id="pl-start" value="'+start+'"></label>'
      + '<span class="seg">'+[[1.5,'一天半一张（推荐）'],[1,'一天一张']].map(function(p){ return '<button data-pace="'+p[0]+'" class="'+(pace===p[0]?'on':'')+'">'+p[1]+'</button>'; }).join('')+'</span>'
      + '<small>到 '+L.cut.slice(5).replace('-','/')+' 能做 '+keep.length+' 张'+(cutList.length?'，砍掉 '+cutList.length+' 张':'')+'；之后两天只回看错题，不开新卷。</small></div>'
      + (L.rhythm?'<div class="pl-rh">'+L.rhythm+'</div>':'')
      + '<div class="tabw"><table class="pl"><thead><tr><th>#</th><th>日期</th><th>卷</th><th>档</th><th>复盘</th><th></th></tr></thead><tbody>'+rows+'</tbody></table></div>'
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
    s.onload=cb; s.onerror=function(){ root.innerHTML='<p style="padding:2em">这一年的卷子加载失败。</p>'; };
    document.head.appendChild(s);
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

  function solHtml(q){
    var h='';
    if (q.type==='choice' && q.ans) h+='<div class="ansline">答案 <b>'+q.ans+'</b></div>';
    if (q.solImg) h+=q.solImg.map(function(s){ return '<img class="pimg" loading="lazy" src="'+s+'" alt="解答">'; }).join('');
    if (q.sol) h+='<div class="sol-b">'+q.sol+'</div>';
    if (q.more) h+='<details class="more"><summary>详解与辨析</summary><div class="sol-b">'+q.more+'</div></details>';
    if (q.tag) h+='<div class="kp">考点：'+esc(q.tag)+'</div>';
    var D=ss.done&&deepOf(q.no);
    if (D) h+=deepHtml(D);
    var bk=q.back||(D&&D.back);
    if (bk && ss.done) h+='<a class="bk" href="'+bk.href+'">'+esc(bk.text)+'</a>';
    return h;
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
    var ans = ss.a[q.no], jd = judged(q), rev = ss.show && ss.show[q.no];
    var h = '<article class="q'+(ss.flag[q.no]?' fl':'')+'" id="q'+q.no+'" data-no="'+q.no+'"><div class="qh"><span class="no">'+q.no+'</span>'
      + '<span class="sc">'+q.score+' 分</span>'+(ss.done&&q.subj&&C.subjects?'<span class="sb">'+esc(C.subjects[q.subj]||q.subj)+'</span>':'')
      + (P.flagNote&&P.flagNote[q.no]?'<span class="wn">'+esc(P.flagNote[q.no])+'</span>':'')
      + '<button class="flag" data-flag="'+q.no+'" title="标记">'+(ss.flag[q.no]?'★ 已标记':'☆ 标记')+'</button></div>';
    if (q.img) h += '<img class="pimg qi" src="'+q.img+'" alt="第 '+q.no+' 题题面">';
    if (q.stem) h += '<div class="stem">'+q.stem+'</div>';
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
    var canShowBtn = !ss.done && S.set.showSol;
    var showNow = ss.done ? rev!==false : (jd && q.type==='choice') ? !!rev : (jd || rev);
    if (!ss.done && S.set.instant && q.type!=='choice' && !ss.open[q.no] && isDone(q)) {
      h += '<button class="solb pri" data-reveal="'+q.no+'">写完了，对答案</button>';
    } else if (canShowBtn || (jd && q.type==='choice' && !ss.done) || ss.done) {
      h += '<button class="solb" data-sol="'+q.no+'">'+(showNow?'收起解答':'解答')+'</button>';
    }
    if (showNow) h += '<div class="sol">'+solHtml(q)+(jd||ss.done?selfHtml(q):'')+'</div>';
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
        return '<a href="javascript:;" data-go="'+q.no+'" class="'+c+(ss.flag[q.no]?' fl':'')+'">'+q.no+'</a>';
      }).join('')+'</div></div>';
    }).join('');
  }
  function drawPaper(){
    var answered = P.q.filter(isDone).length;
    root.innerHTML = '<div class="bar"><a class="bk0" href="#">← 选卷</a><b class="ttl">'+cur+'</b>'
      + '<span class="timer" id="timer"></span><button class="ghost" id="pause"></button>'
      + '<span class="prog" id="prog"></span><span class="live" id="live"></span>'
      + '<span class="cdb" id="cdb"></span>'
      + '<span class="rt"><button class="ghost" id="night">夜</button><button class="ghost" id="gear">开关</button><button class="ghost sh-b" id="shb">答题卡</button><button class="sub" id="submit">'+(ss.done?'成绩':'交卷')+'</button></span></div>'
      + '<div class="gearp" id="gearp" hidden>'+togglesHtml()+'</div>'
      + '<div class="pp"><main id="pm"></main><aside id="sheet"></aside></div>'
      + '<div class="pause-m" id="pm-o" hidden><div><b>已暂停</b><p>卷面先遮住，回来继续。</p><button class="sub" id="resume">继续</button></div></div>'
      + '<div class="modal" id="modal" hidden></div>';
    redrawPaper();
    startTimer();
    if (location.hash.indexOf('q=')>0) go(+location.hash.split('q=')[1]);
    else window.scrollTo(0,0);
  }
  function redrawPaper(){
    if (!$('pm')) return;
    var y=window.scrollY, h='', last=null, nm=P.secName||{};
    if (ss.done) h += reportHtml();
    if (P.note) h += '<div class="pnote">'+P.note+'</div>';
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
    typeset();
    updateSide();
    window.scrollTo(0,y);
  }
  function typeset(){ if (window.renderMathInElement && $('pm')) try{ window.renderMathInElement($('pm'),{throwOnError:false}); }catch(e){} }
  function redrawQ(no){
    var el=$('q'+no), q=P.q.filter(function(x){ return x.no===no; })[0];
    if (el&&q) { var t=document.createElement('div'); t.innerHTML=qHtml(q); el.parentNode.replaceChild(t.firstChild,el); }
    updateSide();
  }
  function updateSide(){
    if ($('sheet')) $('sheet').innerHTML='<div class="sh-t">答题卡</div>'+sheet()+'<div class="shl"><i class="k dn"></i>已答 <i class="k fl"></i>标记'+(S.set.instant||ss.done?' <i class="k ok"></i>对 <i class="k no"></i>错':'')+'</div>';
    var n=P.q.filter(isDone).length;
    if ($('prog')) $('prog').textContent='已答 '+n+' / '+P.q.length;
    if ($('live')) $('live').textContent=(S.set.instant||ss.done)?'得分 '+liveScore():'';
    if ($('cdb')) { $('cdb').textContent=S.set.showCount?countText():''; }
    if ($('submit')) $('submit').textContent=ss.done?'成绩':'交卷';
  }
  function go(no){ var el=$('q'+no); if(el){ var y=el.getBoundingClientRect().top+window.scrollY-64; window.scrollTo({top:y,behavior:'smooth'}); } document.body.classList.remove('sh-open'); }

  /* —— 计时 —— */
  function startTimer(){ stopTimer(); lastTick=Date.now(); tm=setInterval(tick,1000); tick(); }
  function stopTimer(){ if(tm) clearInterval(tm); tm=null; }
  var lastSave=0;
  function tick(){
    if (!cur||!ss) { var cx=$('cdx'); if(cx) cx.textContent=countText()+'　·　'+C.examWhen; return; }
    var now=Date.now();
    if (!paused && !ss.done && S.set.timer!=='off') ss.secs+=(now-lastTick)/1000;
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
      + studyHtml()
      + '<div class="rep-a"><span class="seg">'+[['all','全部'],['wrong','只看失分'],['flag','只看标记']].concat(curDeep()&&curDeep().core?[['core','只看必吃透']]:[]).map(function(o){ return '<button data-filter="'+o[0]+'" class="'+((ss.filter||'all')===o[0]?'on':'')+'">'+o[1]+'</button>'; }).join('')+'</span><button class="ghost" id="redo">重做这一年</button></div></section>';
  }
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

  /* —— 事件 —— */
  document.addEventListener('click', function(e){
    var t=e.target, b;
    if (t.id==='night'||t.closest&&t.closest('#night')) { var n=document.documentElement.getAttribute('data-theme')==='night'?'':'night'; document.documentElement.setAttribute('data-theme',n); try{localStorage.setItem(C.key+'_night',n);}catch(x){} return; }
    if (!cur) return;
    if ((b=t.closest('[data-ans]'))) {
      var no=+b.getAttribute('data-ans'), q=P.q.filter(function(x){ return x.no===no; })[0];
      if (judged(q)&&q.type==='choice') return;
      ss.a[no]=ss.a[no]===b.getAttribute('data-k')?undefined:b.getAttribute('data-k');
      if(ss.a[no]===undefined) delete ss.a[no];
      save(); redrawQ(no); return;
    }
    if ((b=t.closest('[data-flag]'))) { var fn=+b.getAttribute('data-flag'); ss.flag[fn]=!ss.flag[fn]; save(); redrawQ(fn); return; }
    if ((b=t.closest('[data-go]'))) { go(+b.getAttribute('data-go')); if(b.hasAttribute('data-close')) $('modal').hidden=true; return; }
    if ((b=t.closest('[data-close]'))) { $('modal').hidden=true; return; }
    if ((b=t.closest('[data-sol]'))) {
      var sn=+b.getAttribute('data-sol'); ss.show=ss.show||{};
      var q2=P.q.filter(function(x){ return x.no===sn; })[0], now=ss.done?ss.show[sn]!==false:(judged(q2)&&q2.type==='choice')?!!ss.show[sn]:(judged(q2)||ss.show[sn]);
      ss.show[sn]=!now; if(judged(q2)&&q2.type!=='choice'&&!ss.done) ss.open[sn]=ss.show[sn];
      redrawQ(sn); return;
    }
    if ((b=t.closest('[data-reveal]'))) { var rn=+b.getAttribute('data-reveal'); ss.open[rn]=1; ss.show=ss.show||{}; ss.show[rn]=true; save(); redrawQ(rn); return; }
    if ((b=t.closest('[data-wrote]'))) { var wn=+b.getAttribute('data-wrote'); if(ss.a[wn]==='✓') delete ss.a[wn]; else ss.a[wn]='✓'; save(); redrawQ(wn); return; }
    if ((b=t.closest('[data-self]'))) { var fn2=+b.getAttribute('data-self'); ss.self[fn2]=+b.getAttribute('data-v'); if(ss.done) recordHist(); save(); ss.done?redrawPaper():redrawQ(fn2); return; }
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
    if ((k=t.getAttribute('data-txt'))) { if(t.value.trim()) ss.a[k]=t.value; else delete ss.a[k]; lazySave(); updateSide(); return; }
    if ((k=t.getAttribute('data-selfn'))) {
      var q=P.q.filter(function(x){ return x.no===+k; })[0];
      if (t.value==='') delete ss.self[k]; else ss.self[k]=Math.max(0,Math.min(q.score,+t.value));
      if (ss.done) recordHist();
      lazySave(); updateSide();
      var big=document.querySelector('.rep .big strong'); if(big) big.textContent=liveScore();
    }
  });
  var lz; function lazySave(){ clearTimeout(lz); lz=setTimeout(save,400); }
  window.addEventListener('pagehide', save);

  function route(){
    var m=location.hash.match(/y=(\d{4})/);
    warned=false; paused=false;
    if (m) open(+m[1]); else home();
  }
  window.addEventListener('hashchange', route);
  try { var nt=localStorage.getItem(C.key+'_night'); if(nt) document.documentElement.setAttribute('data-theme',nt); } catch(e){}
  setInterval(function(){ if(!cur){ tick(); } else if($('cdb')&&S.set.showCount){ $('cdb').textContent=countText(); } },30000);
  route();
})();
