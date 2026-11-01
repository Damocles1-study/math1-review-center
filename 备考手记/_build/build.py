# -*- coding: utf-8 -*-
"""备考手记构建：_src/dNN_科目.txt → dNN.html、index.html、汇总.html。
文稿语法：
  @read 读了什么            @spent 实际用时            @mood 一句状态（可省）
  # 小节    ## 小标题        - 列表      | 表格 |      ```代码```
  正文：**粗** ==红笔== ~~荧光笔~~ `代码`，数学 sheet 里 $公式$ $$公式$$
  :::def 名称 … :::   框起来的定义/定理（一字不改抄下来的那种）
  :::eg 标题 … :::    例题过程
  :::note … :::       红笔旁注（宽屏进页边）
  :::sk 宽 高 | 图注   Python，变量 s 是 Sk 画板 :::
  :::q 题源 | ✓/✗/△ | 题干（做题记录），内部写过程或错因 :::
  :::stuck … :::      卡点 / 没想通
  @recall 问 || 答     合上本子自测
校验：数学不用未学术语、不碰 2016+ 真题；408 不碰 2020+ 真题；标签配平。
"""
import ast,datetime,glob,html,json,os,re,sys
HERE=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,HERE)
import plan
from sk import Sk
OUT=os.path.dirname(HERE);SRC=os.path.join(OUT,'_src')
ERR=[]
WD='一二三四五六日'
def inline(t,math=False):
    keep=[]
    def k(m): keep.append(m.group(0));return '\0%d\0'%(len(keep)-1)
    if math: t=re.sub(r'\$\$.+?\$\$|\$[^$]+?\$',k,t)
    t=re.sub(r'`([^`]+)`',lambda m:'<code>%s</code>'%html.escape(m.group(1),quote=False),t)
    t=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',t)
    t=re.sub(r'==(.+?)==',r'<span class="red">\1</span>',t)
    t=re.sub(r'~~(.+?)~~',r'<span class="hl">\1</span>',t)
    return re.sub(r'\0(\d+)\0',lambda m:keep[int(m.group(1))],t)
def body(lines,math,sid):
    """把一段文稿行转 HTML"""
    o=[];i=0;n=len(lines);fign=0
    def para(buf):
        if buf: o.append('<p>%s</p>'%inline(' '.join(buf),math));buf.clear()
    buf=[]
    while i<n:
        l=lines[i].rstrip();st=l.strip()
        if not st: para(buf);i+=1;continue
        if st.startswith('```'):
            para(buf);j=i+1;c=[]
            while not lines[j].strip().startswith('```'): c.append(lines[j].rstrip('\n'));j+=1
            o.append('<pre>%s</pre>'%html.escape('\n'.join(c),quote=False));i=j+1;continue
        if st.startswith(':::') and st!=':::':
            para(buf);head=st[3:];kind,_,arg=head.partition(' ');j=i+1;c=[];depth=0
            while True:
                x=lines[j].strip()
                if x==':::' and depth==0: break
                c.append(lines[j]);j+=1
            i=j+1
            if kind=='sk':
                a,_,cap=arg.partition('|');w,h=[int(v) for v in a.split()[:2]];fign+=1
                s=Sk(w,h,seed=hash_seed(sid,fign))
                try: exec('\n'.join(x.strip() if 0 else x for x in dedent(c)),{'s':s,'math':__import__('math'),'INK':None})
                except Exception as e: ERR.append('%s 图%d: %s'%(sid,fign,e))
                o.append('<figure class="fig">%s%s</figure>'%(s.svg(alt=cap.strip()),'<figcaption>%s</figcaption>'%inline(cap.strip(),math) if cap.strip() else ''))
            elif kind=='q':
                p=[x.strip() for x in arg.split('|',2)]
                if len(p)<3: ERR.append('%s q 头缺字段: %s'%(sid,arg));continue
                mark={'✓':'ok','✗':'no','△':'half'}.get(p[1],'half')
                o.append('<div class="qr %s"><div class="qh"><span class="qm">%s</span><span class="qs">%s</span></div><div class="qt">%s</div><div class="qb">%s</div></div>'%(mark,p[1],inline(p[0],math),inline(p[2],math),body(c,math,sid)))
            elif kind in('def','eg'):
                o.append('<div class="%s">%s%s</div>'%(kind,'<div class="ttl">%s</div>'%inline(arg,math) if arg else '',body(c,math,sid)))
            elif kind in('note','stuck'):
                o.append('<aside class="%s">%s</aside>'%(kind,body(c,math,sid)))
            else: ERR.append('%s 未知块 %s'%(sid,kind))
            continue
        if st.startswith('## '): para(buf);o.append('<h4>%s</h4>'%inline(st[3:],math));i+=1;continue
        if st.startswith('# '): para(buf);o.append('<h3>%s</h3>'%inline(st[2:],math));i+=1;continue
        if st.startswith('- '):
            para(buf);it=[]
            while i<n and lines[i].strip().startswith('- '): it.append(lines[i].strip()[2:]);i+=1
            o.append('<ul>%s</ul>'%''.join('<li>%s</li>'%inline(x,math) for x in it));continue
        if st.startswith('|'):
            para(buf);rows=[]
            while i<n and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')]);i+=1
            rows=[r for r in rows if not all(re.fullmatch(r'[-: ]*',c) for c in r)]
            h=''.join('<th>%s</th>'%inline(c,math) for c in rows[0])
            b=''.join('<tr>%s</tr>'%''.join('<td>%s</td>'%inline(c,math) for c in r) for r in rows[1:])
            o.append('<div class="tw"><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table></div>'%(h,b));continue
        if st.startswith('$$') and st.endswith('$$') and len(st)>4 and math:
            para(buf);o.append('<div class="dm">%s</div>'%st);i+=1;continue
        buf.append(st);i+=1
    para(buf);return ''.join(o)
def dedent(c):
    ind=[len(x)-len(x.lstrip()) for x in c if x.strip()]
    m=min(ind) if ind else 0
    return [x[m:] for x in c]
def hash_seed(sid,n): return sum(ord(ch)*(i+7) for i,ch in enumerate(sid))+n*131
def read_sheet(day,sub):
    p=os.path.join(SRC,'d%02d_%s.txt'%(day,sub))
    if not os.path.exists(p): return None
    meta={'read':'','spent':'','mood':''};rec=[];L=[]
    for l in open(p,encoding='utf8'):
        m=re.match(r'@(read|spent|mood) (.*)',l)
        if m: meta[m.group(1)]=m.group(2).strip();continue
        if l.startswith('@recall '): rec.append(l[8:].strip().split('||'));continue
        L.append(l)
    return meta,rec,L
MA=sorted(ast.literal_eval(''))if 0 else None
def load_terms():
    s=open(os.path.join(OUT,'..','重读报','_build','build.py'),encoding='utf8').read()
    m=re.search(r'TERMS = (\{.*?\n\})',s,re.S)
    return ast.literal_eval(m.group(1)) if m else {}
TERMS=load_terms()
MAP=plan.day_map()
def cum(sub,d):
    n=0
    for k,v in MAP.items():
        if k<=d: n+=len(v[sub])
    return n
def lint(day,sub,raw):
    sid='d%02d_%s'%(day,sub)
    for m in re.finditer(r':::q ([^|\n]*)\|',raw):
        t=m.group(1)
        for y in re.findall(r'(20[0-2]\d)',t):
            y=int(y)
            if sub=='math' and y>=2016: ERR.append(sid+' 数学用了留作套卷的 %d: %s'%(y,t))
            if sub=='cs' and y>=2020: ERR.append(sid+' 408 用了留作套卷的 %d: %s'%(y,t))
    if sub=='math':
        last=max(MAP[day]['math']) if day in MAP else 99
        chk=raw.replace('不定积分','')
        for term,first in TERMS.items():
            if first>last and term in chk: ERR.append('%s 用了第 %d 期才学的「%s」'%(sid,first,term))
    t=re.sub(r'\$.*?\$','',raw)
    for tag in ('b','u','i','sub','sup','span','code'):
        if len(re.findall('<%s\\b'%tag,t))!=len(re.findall('</%s>'%tag,t)): ERR.append(sid+' 标签未配平 '+tag)
def fmt_read(day,sub):
    v=MAP.get(day)
    if not v:return ''
    if sub=='math': return '重读报 第 %s 期'%('–'.join('%02d'%x for x in (v['math'][0],v['math'][-1])) if len(v['math'])>1 else '%02d'%v['math'][0])
    if sub=='cs': return '术式408 第 %s 话'%('–'.join('%02d'%x for x in (v['cs'][0],v['cs'][-1])) if len(v['cs'])>1 else '%02d'%v['cs'][0])
    if sub=='en': return '英语 %s'%v['en'][0].replace('_',' ')
    return '政治讲义 '+'、'.join(x.replace('_',' ') for x in v['po'])
def progress_svg(day):
    s=Sk(620,78,seed=day*17)
    x=8;W=196
    for i,k in enumerate(plan.ORDER):
        c=plan.SUBJ[k];col=(i%2)*306+x;row=(i//2)*34+6
        n=cum(k,day);s.text(col,row+13,c['name'],13,'k',rot=0,bold=True)
        s.bar(col+40,row+2,W,13,n/c['total'],label='%d/%d %s'%(n,c['total'],c['unit']))
    return s.svg(cls='sk prog',alt='四科累计进度')
def sheet_html(day,sub,idp=''):
    r=read_sheet(day,sub)
    if not r:return ''
    meta,rec,L=r;raw=''.join(L);lint(day,sub,raw);c=plan.SUBJ[sub];math=sub in('math','cs')
    n=cum(sub,day);pct=round(100*n/c['total'])
    head=('<header class="sh"><div class="sl"><span class="tag">%s · %s</span><span class="tm">%s</span></div>'
          '<div class="rd">%s</div><div class="pg"><span>%s</span><span>进度 %d/%d %s（%d%%）</span></div></header>')%(c['slot'],c['name'],c['time'],html.escape(meta['read'] or fmt_read(day,sub),quote=False),html.escape(meta['spent'],quote=False),n,c['total'],c['unit'],pct)
    rb=''
    if rec:
        rb='<div class="rec"><div class="rt">合上本子自测（点开看答案）</div>'+''.join('<details><summary>%s</summary><div>%s</div></details>'%(inline(q[0].strip(),math),inline(q[1].strip() if len(q)>1 else '',math)) for q in rec)+'</div>'
    return '<article class="sheet s-%s%s" id="%sd%02d-%s" data-sub="%s">%s%s%s</article>'%(sub,' m' if math else '',idp,day,sub,sub,head,body(L,math,'d%02d_%s'%(day,sub)),rb)
def day_html(day,idp=''):
    d=plan.date_of(day);left=(plan.EXAM-d).days;is_study=day in MAP
    title='第 %d 天'%day
    head=('<div class="dh" id="%sday%02d"><div class="dn">%s</div><div class="dd">%d 月 %d 日 周%s · 距初试 %d 天 · 全程 %d/21</div>%s</div>')%(idp,day,title,d.month,d.day,WD[d.weekday()],left,day,progress_svg(day))
    subs=plan.ORDER if is_study else ['rev']
    if is_study: head+='<div class="tb">07:30 起床 · 08:00 单词 30 分 · <b>08:30 数学</b> · 11:30 午饭午睡 · <b>14:00 408</b> · 17:30 跑步晚饭 · <b>19:00 英语</b> · <b>20:40 政治</b> · 21:40 写复盘 · 22:30 睡</div>'
    else: head+='<div class="tb">周日只复盘：上午过一遍这周的笔记和错题，下午做一点补漏，晚上休息。不学新内容。</div>'
    parts=[]
    if is_study:
        parts=[sheet_html(day,k,idp) for k in plan.ORDER]
    else:
        r=read_sheet(day,'rev')
        if r:
            meta,rec,L=r;raw=''.join(L)
            parts=['<article class="sheet s-rev m" id="%sd%02d-rev" data-sub="rev"><header class="sh"><div class="sl"><span class="tag">周日 · 复盘</span></div><div class="rd">%s</div><div class="pg"><span>%s</span></div></header>%s</article>'%(idp,day,html.escape(meta['read'],quote=False),html.escape(meta['spent'],quote=False),body(L,True,'d%02d_rev'%day))]
    r=read_sheet(day,'day');tail=''
    if r:
        meta,rec,L=r
        tail='<article class="sheet s-day m" data-sub="day"><header class="sh"><div class="sl"><span class="tag">今日复盘</span><span class="tm">21:40–22:10</span></div></header>%s</article>'%body(L,True,'d%02d_day'%day)
    return head+''.join(parts)+tail
SHELL='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>%(t)s</title>
<link rel="stylesheet" href="../重读报/assets/katex/katex.min.css"><link rel="stylesheet" href="notes.css?v=%(v)s"></head><body class="%(c)s">%(b)s
<script src="../重读报/assets/katex/katex.min.js"></script><script src="notes.js?v=%(v)s"></script></body></html>'''
VER='4'
def page(t,b,c=''): return SHELL%dict(t=t,b=b,c=c,v=VER)
def done_days(): return sorted({int(os.path.basename(f)[1:3]) for f in glob.glob(os.path.join(SRC,'d??_*.txt'))})
def build():
    days=done_days();tot_cn=0;figs=0
    for f in glob.glob(os.path.join(SRC,'d??_*.txt')):
        s=open(f,encoding='utf8').read();tot_cn+=len(re.findall(r'[一-鿿]',s));figs+=s.count(':::sk ')
    # 单日页
    for i,d in enumerate(days):
        nav='<nav class="nv"><a href="index.html">目录</a>'+('<a href="d%02d.html">← 第 %d 天</a>'%(days[i-1],days[i-1]) if i else '')+('<a href="d%02d.html">第 %d 天 →</a>'%(days[i+1],days[i+1]) if i+1<len(days) else '')+'<a href="汇总.html#day%02d">在汇总里看</a></nav>'%d
        open(os.path.join(OUT,'d%02d.html'%d),'w',encoding='utf8').write(page('第 %d 天 · 备考手记'%d,nav+'<main>'+day_html(d)+'</main>'+nav))
    # 汇总
    filt='<div class="ft" id="ft"><b>只看：</b><button data-f="all" class="on">全部</button><button data-f="math">数学</button><button data-f="cs">408</button><button data-f="en">英语</button><button data-f="po">政治</button><button data-f="rev">周日复盘</button></div>'
    toc=''.join('<a href="#day%02d">%d</a>'%(d,d) for d in days)
    all_='<nav class="nv"><a href="index.html">封面与目录</a></nav><header class="ct"><h1>备考手记 · 全本</h1><p>一个模拟学生的全部笔记：%d 天，约 %.1f 万字，%d 幅手绘图。可以直接打印成 PDF。</p></header>%s<div class="toc">跳到第 %s 天</div><main>%s</main>'%(len(days),round(tot_cn/10000,1),figs,filt,toc,''.join(day_html(d,'a') for d in days))
    open(os.path.join(OUT,'汇总.html'),'w',encoding='utf8').write(page('备考手记 · 全本',all_,'all'))
    # 封面
    rows=[]
    for d in range(1,22):
        dt=plan.date_of(d)
        if d in MAP:
            v=MAP[d];cells='<td>%s</td><td>%s</td><td>%s</td><td>%s</td>'%(', '.join('%02d'%x for x in v['math']),'%02d–%02d'%(v['cs'][0],v['cs'][-1]) if len(v['cs'])>1 else '%02d'%v['cs'][0],v['en'][0].replace('_',' '),'、'.join(x.replace('_',' ').replace('导论与第1章','导论+1').replace('第','') for x in v['po']))
        else: cells='<td colspan="4" class="rv">周日复盘：这一周的笔记、错题和跨科串联</td>'
        link=d in days
        rows.append('<tr%s><td class="dc">%s</td><td class="dc">%d/%d 周%s</td>%s</tr>'%('' if link else ' class="todo"','<a href="d%02d.html">第 %d 天</a>'%(d,d) if link else '第 %d 天'%d,dt.month,dt.day,WD[dt.weekday()],cells))
    intro=open(os.path.join(SRC,'cover.html'),encoding='utf8').read()%dict(days=len(days),cn=round(tot_cn/10000,1),figs=figs)
    cov='<header class="ct"><h1>备考手记</h1><p class="sub">一个从零开始的考研学生，三周读完四个复习中心的全部笔记</p></header><main><article class="sheet">%s<h3>全程目录</h3><div class="tw"><table class="cal"><thead><tr><th>天</th><th>日期</th><th>数学（期）</th><th>408（话）</th><th>英语</th><th>政治（章）</th></tr></thead><tbody>%s</tbody></table></div></article></main>'%(intro,''.join(rows))
    open(os.path.join(OUT,'index.html'),'w',encoding='utf8').write(page('备考手记',cov,'cover'))
    # 收尾校验
    st={'math':0,'cs':0,'en':0,'po':0}
    for k in st:st[k]=len(glob.glob(os.path.join(SRC,'d??_%s.txt'%k)))
    print('天',len(days),'汉字',tot_cn,'图',figs,st)
    if ERR:
        print('\n'.join(ERR));sys.exit(1)
if __name__=='__main__': build()
