/* 在线真题套卷引擎：408 与数学一共用，各自的 EXAM_CONF 写在页面里，卷子数据按年放在 assets/exam/yYYYY.js。
 * 题目字段：no 题号 / type choice|blank|essay / score / subj / stem(html) 或 img(题面图) / opts / ans
 *           sol(html，解答) / more(html，详解，可省) / solImg(解答图数组) / tag(考点) / back({href,text}) */
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
        + (info?'<em>'+esc(info)+'</em>':'')+'</a>';
    }).join('');
    var hist = S.hist.slice().reverse().slice(0,12).map(function(h){
      return '<tr><td>'+h.y+'</td><td><b>'+h.score+'</b> / '+h.full+'</td><td>'+fmt(h.secs)+'</td><td>'+new Date(h.at).toLocaleDateString('zh-CN')+'</td></tr>';
    }).join('');
    root.innerHTML = '<div class="hm">'
      + '<div class="hm-top"><a href="'+C.backHref+'">← '+esc(C.backText)+'</a><span>'+esc(C.title)+'</span><button class="ghost" id="night">夜</button></div>'
      + '<div class="hero"><div class="cd"><i>距 '+esc(C.examName)+'</i><strong>'+(left>0?left:0)+'</strong><i>天</i></div>'
      + '<div class="hero-t"><h1>'+esc(C.heading)+'</h1><p>'+C.lead+'</p><p class="cdx" id="cdx">'+esc(countText())+'　·　'+esc(C.examWhen)+'</p></div></div>'
      + '<h2>开关</h2><div class="tgs">'+togglesHtml()+'</div>'
      + '<h2>选一年</h2><div class="yrs">'+rows+'</div>'
      + (hist?'<h2>做过的卷子</h2><div class="tabw"><table class="hst"><thead><tr><th>年份</th><th>得分</th><th>用时</th><th>日期</th></tr></thead><tbody>'+hist+'</tbody></table></div>':'')
      + (C.footHtml?'<div class="foot">'+C.footHtml+'</div>':'')
      + '</div>';
    window.scrollTo(0,0);
  }

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
  function open(y){
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
    if (q.back && ss.done) h+='<a class="bk" href="'+q.back.href+'">'+esc(q.back.text)+'</a>';
    return h;
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
      + '<div class="rep-a"><span class="seg">'+[['all','全部'],['wrong','只看失分'],['flag','只看标记']].map(function(o){ return '<button data-filter="'+o[0]+'" class="'+((ss.filter||'all')===o[0]?'on':'')+'">'+o[1]+'</button>'; }).join('')+'</span><button class="ghost" id="redo">重做这一年</button></div></section>';
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
