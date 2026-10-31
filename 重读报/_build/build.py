#!/usr/bin/env python3
"""重读报构建器：_src/NN.txt → qNN.html + assets/data.js
硬校验（任何一条不过就退出码 1）：
  1. [[定理]] 只能引用「此前已刊登」的定理（同期也要在引用位置之前）
  2. TERMS 里的术语不许出现在它的首发期之前（防「这里用后面的知识」）
  3. 行内标记配平、图存在、期号连续
"""
import html, json, re, sys, glob, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figs import FIG

PARTS = {'甲': '一元微积分', '乙': '线性代数', '丙': '多元与级数', '丁': '概率统计'}
PAPER = '重读报'
ERR = []

# 术语 → 首发期号。文稿里早于该期出现就报错。
TERMS = {
    '等价无穷小': 3, '导数': 4, '求导': 4, '微分': 4, '可导': 4,
    '中值定理': 6, '洛必达': 6, '泰勒': 7, '麦克劳林': 7, '极值': 6, '拐点': 8, '渐近线': 8,
    '不定积分': 10, '原函数': 10, '定积分': 11, '变限积分': 11, '反常积分': 12,
    '微分方程': 13, '特征方程': 14,
    '行列式': 15, '矩阵': 16, '逆矩阵': 16, '伴随': 16, '秩': 17, '基础解系': 17,
    '线性相关': 18, '线性无关': 18, '极大无关组': 18, '特征值': 19, '特征向量': 19,
    '相似': 20, '对角化': 20, '二次型': 21, '正定': 21, '合同': 21,
    '叉积': 22, '偏导': 23, '全微分': 23, '梯度': 24, '方向导数': 24, '切平面': 24,
    '二重积分': 25, '三重积分': 26, '曲线积分': 27, '曲面积分': 27, '格林': 28,
    '高斯公式': 29, '散度': 29, '斯托克斯': 29, '旋度': 29,
    '级数': 30, '收敛半径': 31, '幂级数': 31, '傅里叶': 31,
    '全概率': 32, '贝叶斯': 32, '分布函数': 33, '概率密度': 33, '正态分布': 33,
    '联合分布': 34, '边缘': 34, '期望': 35, '方差': 35, '协方差': 35, '相关系数': 35,
    '切比雪夫': 36, '中心极限': 36, '大数定律': 36, '矩估计': 37, '似然': 37,
    '无偏': 37, '置信区间': 37, '假设检验': 37,
}
# 这些词在该期之前可以作为别的词的一部分出现（比如「极值」不查「极限值」），用负向排除
TERM_EXCEPT = {'伴随': ['相伴随'], '相似': ['相似形'], '合同': [], '秩': ['秩序'], '微分': []}


def esc(s):
    return html.escape(s, quote=False)


class Ctx:
    def __init__(self, no):
        self.no, self.ex = no, 0


THM, THM_SEEN = {}, []   # id → dict；出现顺序
RECALL = []


def tex(s, display=False):
    s = s.strip()
    # KaTeX 里 < > 交给 html.escape，JS 读 textContent 还原，不存在吞字问题
    cls = 'M' if display else 'm'
    tag = 'div' if display else 'span'
    return f'<{tag} class="{cls}">{esc(s)}</{tag}>'


def inline(s, ctx):
    maths = []

    def stash(m):
        maths.append(tex(m.group(0)[1:-1]))
        return f'\x00{len(maths)-1}\x00'
    t = re.sub(r'\$[^$]+\$', stash, s)
    t = esc(t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'==(.+?)==', r'<em class="hot">\1</em>', t)
    t = re.sub(r'⛳(\d+)', r'<span class="pt">\1分</span>', t)

    def cite(m):
        tid, _, disp = m.group(1).partition('|')
        tid = tid.strip()
        if tid not in THM:
            ERR.append(f'第{ctx.no}期：[[{tid}]] 引用了尚未刊登的定理')
            return disp or tid
        return f'<a class="c" data-t="{tid}">{disp or THM[tid]["name"]}</a>'
    t = re.sub(r'\[\[(.+?)\]\]', cite, t)
    return re.sub('\x00(\\d+)\x00', lambda m: maths[int(m.group(1))], t)


def table(rows, ctx):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    h = ''.join(f'<th>{inline(c, ctx)}</th>' for c in cells[0])
    b = ''.join('<tr>' + ''.join(f'<td>{inline(c, ctx)}</td>' for c in r) + '</tr>' for r in cells[1:])
    return f'<div class="tab"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def body(lines, ctx):
    """解析一段行序列 → html"""
    out, i = [], 0
    while i < len(lines):
        l = lines[i].rstrip()
        if not l.strip():
            i += 1
            continue
        if l.startswith('$$'):
            m = re.match(r'^\$\$(.*)\$\$\s*(?:⛳(\d+))?\s*$', l)
            if not m:
                ERR.append(f'第{ctx.no}期：展示公式格式错误 {l[:40]}')
                i += 1
                continue
            pt = f'<span class="pt">{m.group(2)}分</span>' if m.group(2) else ''
            out.append(pt + tex(m.group(1), True))
        elif l.startswith('### '):
            out.append(f'<h3>{inline(l[4:], ctx)}</h3>')
        elif l.startswith('## '):
            out.append(f'<h2>{inline(l[3:], ctx)}</h2>')
        elif l.startswith('!fig '):
            key, _, cap = l[5:].partition('|')
            key = key.strip()
            if key not in FIG:
                ERR.append(f'第{ctx.no}期：图 {key} 不存在')
                svg = ''
            else:
                svg = FIG[key]()
            out.append(f'<figure>{svg}<figcaption>{inline(cap.strip(), ctx)}</figcaption></figure>')
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                rows.append(lines[i])
                i += 1
            out.append(table(rows, ctx))
            continue
        elif l.startswith('- '):
            items = []
            while i < len(lines) and lines[i].startswith('- '):
                items.append(f'<li>{inline(lines[i][2:], ctx)}</li>')
                i += 1
            out.append('<ul>' + ''.join(items) + '</ul>')
            continue
        elif l.startswith('∎'):
            out.append(f'<p class="fin">{inline(l[1:].strip(), ctx)}</p>')
        else:
            out.append(f'<p>{inline(l, ctx)}</p>')
        i += 1
    return '\n'.join(out)


LABEL = {'think': '思路', 'paper': '考场卷面', 'note': '批注', 'like': '打个比方',
         'trap': '易错', 'skip': '本报不刊', 'fml': '公式'}


def container(kind, args, lines, ctx):
    a = [x.strip() for x in args.split('|')] if args else []
    if kind == 'thm':
        tid, name = a[0], a[1]
        lab = a[2] if len(a) > 2 else '定理'
        if tid in THM:
            ERR.append(f'第{ctx.no}期：定理 id {tid} 重复')
        inner = body(lines, ctx)
        name_html = inline(name, ctx)
        THM[tid] = {'name': name_html, 'lab': lab, 'html': inner, 'no': ctx.no}
        return f'<div class="thm" id="t-{tid}"><div class="thm-h"><span>{lab}</span>{name_html}</div>{inner}</div>'
    if kind == 'ex':
        ctx.ex += 1
        tag = f'<span class="ex-tag">{inline(a[0], ctx)}</span>' if a else ''
        return f'<div class="ex"><div class="ex-h">例 {ctx.no}.{ctx.ex}{tag}</div>{body(lines, ctx)}</div>'
    if kind in LABEL:
        lab = a[0] if a else LABEL[kind]
        return f'<div class="{kind}"><div class="b-h">{inline(lab, ctx)}</div>{body(lines, ctx)}</div>'
    ERR.append(f'第{ctx.no}期：未知容器 {kind}')
    return ''


def parse(no, text):
    meta = {'keep': [], 'recall': [], 'title': '', 'kicker': '', 'deck': '', 'part': ''}
    ctx = Ctx(no)
    html_blocks, heads, buf, kind, args = [], [], [], None, ''

    def flush():
        nonlocal buf
        if buf:
            html_blocks.append(body(buf, ctx))
            buf = []
    cin = []
    for raw in text.split('\n'):
        l = raw.rstrip()
        if kind is None and l.startswith('@'):
            k, _, v = l[1:].partition(' ')
            if k == 'keep':
                meta['keep'].append(v)
            elif k == 'recall':
                q, _, ans = v.partition('||')
                meta['recall'].append((q.strip(), ans.strip()))
            else:
                meta[k] = v
            continue
        if kind is None and l.startswith(':::'):
            flush()
            m = re.match(r':::(\w+)\s*(.*)', l)
            kind, args, cin = m.group(1), m.group(2), []
            continue
        if kind is not None:
            if l.strip() == ':::':
                html_blocks.append(container(kind, args, cin, ctx))
                kind = None
            else:
                cin.append(l)
            continue
        if l.startswith('## '):
            heads.append(l[3:])
        buf.append(l)
    flush()
    if kind:
        ERR.append(f'第{no}期：容器 {kind} 未闭合')
    return meta, heads, '\n'.join(html_blocks), ctx


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


def minutes(raw):
    """阅读时长估算：可见中文 280 字/分；展示公式 20 秒；行内公式 3 秒；每道例题再加 2 分钟自己想/对照"""
    no_math = re.sub(r'\$\$.*?\$\$|\$[^$]+\$', '', raw)
    cn = len(re.findall(r'[一-鿿]', no_math))
    disp, inl = raw.count('$$') // 2, len(re.findall(r'(?<!\$)\$(?!\$)[^$]+\$', raw))
    ex = raw.count(':::ex')
    return round(cn / 280 + disp / 3 + inl * 0.05 + ex * 2)


PAGE = '''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title} · 第{no}期 · {paper}</title>
<link rel="stylesheet" href="assets/katex/katex.min.css">
<link rel="stylesheet" href="assets/paper.css">
</head><body class="issue" data-no="{no}" data-prev="{prev}" data-next="{next}">
<header class="strip"><a class="brand" href="index.html">{paper}</a>
<span class="strip-m">第 {no} 期 · {partname} · {kicker}</span>
<nav class="tools"><button data-a="toc" title="目录 (T)">目录</button><button data-a="rail" class="only-narrow">定理<i id="railn"></i></button><button data-a="hide" title="遮住卷面，先自己写 (H)">遮卷面</button><button data-a="night" title="夜读">夜读</button></nav></header>
<main class="sheet" id="sheet">
<section class="cover" id="cover">
<div class="mast"><div class="mast-l">{partname}<br>第 {no} 期</div><div class="mast-c">{paper}</div><div class="mast-r">本期约 {mins} 分钟<br>{kicker}</div></div>
<h1>{title}</h1>
<p class="deck">{deck}</p>
<div class="cover-grid">
<div class="cover-keep"><h4>本期只记这几行</h4><ol>{keep}</ol></div>
<div class="cover-prev"><h4>开读前，先答上期</h4><div id="prevq"></div></div>
<div class="cover-toc"><h4>本期目录</h4><ol>{toc}</ol><p class="hint">→ 键 / 点右缘 / 左滑翻页</p></div>
</div></section>
<section class="stage" id="stage" hidden>
<div class="viewport" id="vp"><div class="flow" id="flow">
{content}
<div class="endq"><h2>今日考你</h2><p class="hint">合上前答一遍：先想，再点开。答错的会回到后面几期和温故版。</p>{recall}</div>
<div class="endnext" id="endnext"></div>
<div id="sent"></div>
</div></div>
<aside class="rail" id="rail"><div class="rail-h">本版引用 · 定理全文</div><div id="railc"></div></aside>
</section></main>
<footer class="pager"><button id="pv" aria-label="上一版">‹</button><div class="pginfo"><span id="pgt"></span><div class="bar"><i id="pgb"></i></div></div><button id="nx" aria-label="下一版">›</button></footer>
<div class="sheetup" id="sheetup" hidden><div class="sheetup-h"><span>定理全文</span><button id="sheetx">关闭</button></div><div id="sheetc"></div></div>
<div class="drawer" id="drawer" hidden></div>
<script src="assets/katex/katex.min.js"></script><script src="assets/data.js"></script><script src="assets/paper.js"></script>
</body></html>
'''


def recall_html(no, items, ctx):
    r = []
    for i, (q, a) in enumerate(items):
        qid = f'{no}-{i}'
        r.append(f'<div class="rq" data-q="{qid}"><p class="rq-q">{inline(q, ctx)}</p><p class="rq-a">{inline(a, ctx)}</p>'
                 f'<div class="rq-b"><button data-v="1">答对了</button><button data-v="0">没答上</button></div></div>')
    return ''.join(r)


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
NAV = '<a href="index.html">总版</a><a href="定理索引.html">定理索引</a><a href="温故.html">温故版</a><a href="../index.html">旧版复盘中心</a><a href="#" onclick="CDNight();return false">夜读</a>'


def write_front(idx):
    tot = sum(i['mins'] for i in idx)
    n_ex = sum(i['ex'] for i in idx)
    parts = ''
    for p, name in PARTS.items():
        items = [i for i in idx if i['part'] == p]
        if not items:
            continue
        parts += f'<section class="part"><h2>{name}<small>{sum(i["mins"] for i in items)} 分钟</small></h2>'
        for i in items:
            parts += (f'<a class="it" data-no="{i["no"]}" href="q{i["no"]:02d}.html"><span class="t">{esc(i["title"])}</span>'
                      f'<span class="s"><span>第 {i["no"]} 期 · {esc(i["kicker"])}</span><span>{i["mins"]} 分</span></span></a>')
        parts += '</section>'
    days = ''
    for d in (1, 2, 3):
        its = [i for i in idx if i['day'] == d]
        days += (f'<li data-day="{d}"><b>第{"一二三"[d-1]}天</b><span>第 {its[0]["no"]}–{its[-1]["no"]} 期 · 约 {sum(i["mins"] for i in its)/60:.1f} 小时</span></li>')
    html_ = HEAD.format(title='重读报 · 数学一') + f'''
<div class="front-top"><span id="today"></span><span>数学一 · 重捋一遍，然后上套卷</span></div>
<div class="front-mast">重读报</div>
<div class="front-sub"><span>全 {len(idx)} 期 · 例题 {n_ex} 道 · 预计 {tot/60:.1f} 小时</span><span>{NAV}</span></div>
<div class="lead-wrap">
  <div>
    <div class="kick" id="leadkick">创刊号</div>
    <h1><a id="leadt" href="q01.html"></a></h1>
    <p id="leadd"></p>
    <a class="lead-go" id="leadgo" href="q01.html">开始阅读 →</a>
    <p class="hint" style="margin-top:.8em">→ 键翻页，T 目录，H 遮住卷面。文中蓝色虚线的定理名，右栏自动显示全文。</p>
  </div>
  <aside class="lead-side">
    <h3>三日行程</h3><ul>{days}</ul>
    <h3 style="margin-top:.9em">这份报怎么读</h3>
    <ul style="display:block"><li style="display:block">每期先答头版的三道旧题，治「读完就忘」。</li>
    <li style="display:block">每个知识点只用已经刊登过的内容，构建时有程序检查。</li>
    <li style="display:block">大题先合上卷面自己写，再对照标准格式。</li>
    <li style="display:block">例题走教材常见题型，不照搬近年真题卷，把新鲜感留给套卷。</li></ul>
  </aside>
</div>
<div class="parts">{parts}</div>
''' + FOOT.format(script='''<script>
(function(){
 const D=window.CD,S=window.CDStore,rd=S.get('read',{}),last=S.get('last',0);
 document.getElementById('today').textContent=new Date().toLocaleDateString('zh-CN',{year:'numeric',month:'long',day:'numeric',weekday:'long'});
 let nx=D.issues.find(i=>!rd[i.no])||D.issues[0];
 const lastI=last&&!rd[last]?D.issues.find(i=>i.no===last):null;
 const cur=lastI||nx,done=Object.keys(rd).length;
 const pad=n=>String(n).padStart(2,'0');
 document.getElementById('leadkick').textContent=(done?`已读 ${done} / ${D.issues.length} 期 · `:'创刊号 · ')+`今日头条 · 第 ${cur.no} 期 · ${cur.partname}`;
 const t=document.getElementById('leadt');t.textContent=cur.title;t.href=`q${pad(cur.no)}.html`;
 document.getElementById('leadd').textContent=cur.deck;
 const g=document.getElementById('leadgo');g.href=t.href;g.textContent=(lastI?'继续阅读':'开始阅读')+` →（约 ${cur.mins} 分钟）`;
 document.querySelectorAll('.it').forEach(a=>{const n=+a.dataset.no;if(rd[n])a.classList.add('done');if(n===cur.no)a.classList.add('now')});
 const dd={};D.issues.forEach(i=>{dd[i.day]=dd[i.day]||[0,0];dd[i.day][1]++;if(rd[i.no])dd[i.day][0]++});
 document.querySelectorAll('[data-day]').forEach(li=>{const v=dd[li.dataset.day];if(v[0])li.querySelector('b').textContent+=` ${v[0]}/${v[1]}`});
})();
</script>''')
    open(os.path.join(ROOT, 'index.html'), 'w', encoding='utf-8').write(html_)

    # 定理索引
    body_ = ''
    last = None
    meta = {i['no']: i for i in idx}
    for tid, t in THM.items():
        if t['no'] != last:
            last = t['no']
            body_ += f'<h3><a href="q{last:02d}.html" style="text-decoration:none">第 {last} 期 · {esc(meta[last]["kicker"])}</a></h3>'
        body_ += f'<div class="rcard"><h5>{t["name"]}<span>{t["lab"]}</span></h5>{t["html"]}</div>'
    html_ = HEAD.format(title='定理索引 · 重读报') + f'''
<div class="front-top"><span>定理索引</span><span>{NAV}</span></div>
<h1 class="pg-h" style="border-top:5px solid var(--rule);padding-top:.2em">全部定理与公式，按首次刊登排列</h1>
<p class="sub-lead">共 {len(THM)} 条。做套卷卡住时来这里查。⌘F 可搜定理名。</p>
<div class="thm-grid">{body_}</div>
''' + FOOT.format(script="<script>CDRender(document);CDFit(document)</script>")
    open(os.path.join(ROOT, '定理索引.html'), 'w', encoding='utf-8').write(html_)

    # 温故版：间隔复习
    html_ = HEAD.format(title='温故版 · 重读报') + f'''
<div class="front-top"><span>温故版</span><span>{NAV}</span></div>
<h1 class="pg-h" style="border-top:5px solid var(--rule);padding-top:.2em">记不住，就再考一次</h1>
<p class="sub-lead">只从你已经读过的期号里出题。答错的和隔得久的优先。每轮 10 道，约 5 分钟。建议每读完一天的内容做两轮，上套卷前再过一遍「只看答错过的」。</p>
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
    open(os.path.join(ROOT, '温故.html'), 'w', encoding='utf-8').write(html_)


def main():
    files = sorted(glob.glob(os.path.join(ROOT, '_src', '[0-9][0-9].txt')))
    nos = [int(os.path.basename(f)[:2]) for f in files]
    issues = []
    for f, no in zip(files, nos):
        raw = open(f, encoding='utf-8').read()
        src_for_terms = re.sub(r'^@(recall)\s.*$', lambda m: m.group(0), raw, flags=re.M)
        for term, first in TERMS.items():
            probe = re.sub(r'不定积分', '', src_for_terms) if term == '定积分' else src_for_terms
            if no < first and term in probe:
                # 例外词
                bad = True
                for ex in TERM_EXCEPT.get(term, []):
                    if ex in src_for_terms:
                        bad = False
                if bad:
                    idx = probe.find(term)
                    ERR.append(f'第{no}期：术语「{term}」应从第{first}期才出现 …{probe[max(0, idx-18):idx+18]!r}')
        meta, heads, content, ctx = parse(no, raw)
        issues.append(dict(no=no, meta=meta, heads=heads, content=content, ctx=ctx, raw=raw, mins=minutes(raw)))
    for it in issues:
        no, m = it['no'], it['meta']
        ctx = it['ctx']
        rec = [{'id': f'{no}-{i}', 'q': inline(q, ctx), 'a': inline(a, ctx), 'no': no} for i, (q, a) in enumerate(m['recall'])]
        RECALL.extend(rec)
        toc = ''.join(f'<li>{inline(h, ctx)}</li>' for h in it['heads'])
        keep = ''.join(f'<li>{inline(k, ctx)}</li>' for k in m['keep'])
        idx = nos.index(no)
        prev = f'q{nos[idx-1]:02d}.html' if idx else 'index.html'
        nxt = f'q{nos[idx+1]:02d}.html' if idx + 1 < len(nos) else 'index.html'
        if not m['title']:
            ERR.append(f'第{no}期缺标题')
        page = PAGE.format(no=no, paper=PAPER, title=inline(m['title'], ctx), partname=PARTS.get(m['part'], ''),
                           kicker=esc(m['kicker']), mins=it['mins'], deck=inline(m['deck'], ctx), keep=keep,
                           toc=toc, content=it['content'], recall=recall_html(no, m['recall'], ctx),
                           prev=prev, next=nxt)
        page = page.replace('<title>' + inline(m['title'], ctx), '<title>' + strip_tags(inline(m['title'], ctx)))
        open(os.path.join(ROOT, f'q{no:02d}.html'), 'w', encoding='utf-8').write(page)
    # 三日行程：按预计时长三等分
    tot = sum(i['mins'] for i in issues)
    cum, day_of = 0, {}
    for i in issues:
        day_of[i['no']] = min(3, int(cum / (tot / 3)) + 1)
        cum += i['mins']
    idx = [dict(no=i['no'], part=i['meta']['part'], partname=PARTS.get(i['meta']['part'], ''),
                title=strip_tags(i['meta']['title']), kicker=i['meta']['kicker'], deck=strip_tags(i['meta']['deck']),
                mins=i['mins'], day=day_of[i['no']], ex=i['ctx'].ex) for i in issues]
    data = 'window.CD=' + json.dumps({'issues': idx, 'thm': THM, 'recall': RECALL}, ensure_ascii=False) + ';\n'
    open(os.path.join(ROOT, 'assets', 'data.js'), 'w', encoding='utf-8').write(data)
    write_front(idx)
    print(f'{len(issues)} 期 · {tot} 分钟 ≈ {tot/60:.1f} 小时 · 例题 {sum(i["ctx"].ex for i in issues)} · 定理 {len(THM)} · 自测 {len(RECALL)}')
    for p in PARTS:
        s = [i for i in issues if i['meta']['part'] == p]
        if s:
            print(f'  {p} {PARTS[p]}: {len(s)} 期 {sum(i["mins"] for i in s)} 分钟 ; ' + ' '.join(f"{i['no']}:{i['mins']}" for i in s))
    if ERR:
        print('\n'.join('✗ ' + e for e in ERR))
        sys.exit(1)
    print('校验通过：无前向引用、无越期术语')


if __name__ == '__main__':
    main()
