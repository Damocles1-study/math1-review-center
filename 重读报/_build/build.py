#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import exam_map as EX
import pages as PG

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
RECALL, PRAC, TRAPS = [], [], []


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
        if kind == 'trap':
            TRAPS.append(dict(no=ctx.no, html=body(lines, ctx)))
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


SPOIL_FROM = 2016  # 2016 及以后整卷留给套卷
QS, QIDS = {}, set()
QTYPE_MIN = 2.5   # 一道选填按 2.5 分钟算


def load_q():
    """_src/shizhan.txt → {期: [题]}。格式见该文件开头。"""
    path = os.path.join(ROOT, '_src', 'shizhan.txt')
    cur, lines = None, []
    for raw in open(path, encoding='utf-8').read().split('\n'):
        if cur is None:
            m = re.match(r':::q\s+(\d+)\s*\|\s*([^|]+?)\s*\|\s*(.+?)\s*$', raw)
            if m:
                cur, lines = (int(m.group(1)), m.group(2), m.group(3)), []
            continue
        if raw.strip() == ':::':
            no, src, ans = cur
            cur = None
            if '---' not in lines:
                ERR.append(f'实战 {src} 缺 ---')
                continue
            k = lines.index('---')
            stem, note = lines[:k], lines[k + 1:]
            opts = [l for l in stem if re.match(r'^[A-D]\. ', l)]
            stem = [l for l in stem if not re.match(r'^[A-D]\. ', l)]
            ym = re.match(r'(\d{4})-(\d+)$', src)
            if ym:
                y = int(ym.group(1))
                if y >= SPOIL_FROM:
                    ERR.append(f'实战 {src}：{SPOIL_FROM} 年及以后的题留给套卷，不许进讲义')
                if EX.MAP[y][int(ym.group(2)) - 1] != no:
                    ERR.append(f'实战 {src} 放在第 {no} 期，与 exam_map 记的第 {EX.MAP[y][int(ym.group(2)) - 1]} 期不一致')
            if opts and ans not in 'ABCD':
                ERR.append(f'实战 {src}：选择题答案应为字母')
            QS.setdefault(no, []).append(dict(no=no, src=src, ans=ans, stem=stem, opts=opts, note=note))
            continue
        lines.append(raw)
    for no, qs in QS.items():
        for i, q in enumerate(qs):
            q['id'] = q['src'] if q['src'] != '自编' else f'z{no}-{i}'
            if q['id'] in QIDS:
                ERR.append(f'实战 {q["id"]} 重复')
            QIDS.add(q['id'])
            text = ' '.join(q['stem'] + q['opts'] + q['note'])
            for term, first in TERMS.items():
                probe = text.replace('不定积分', '') if term == '定积分' else text
                if no < first and term in probe:
                    ERR.append(f'实战 {q["id"]}（第{no}期）用了第{first}期才讲的「{term}」')


def q_html(q, ctx):
    src = q['src']
    m = re.match(r'(\d{4})-(\d+)$', src)
    lab = f'{m.group(1)} 年第 {m.group(2)} 题' if m else '同型练习'
    stem = body(q['stem'], ctx)
    note = body(q['note'], ctx)
    if q['opts']:
        ob = ''.join(f'<button data-o="{o[0]}">{inline(o.replace(chr(92) + "frac", chr(92) + "dfrac"), ctx)}</button>' for o in q['opts'])
        act = f'<div class="qz-o">{ob}</div>'
        ans = q['ans']
        fin = ''
    else:
        act = '<div class="qz-s"><button class="qz-show">写完了，看答案</button></div>'
        ans = inline(q['ans'], ctx)
        fin = '<div class="qz-b"><button data-v="1">做对了</button><button data-v="0">做错了</button></div>'
    return (f'<div class="qz" data-q="{q["id"]}" data-a="{q["ans"] if q["opts"] else ""}"><div class="qz-h">{lab}<i class="qz-r"></i></div>'
            f'{stem}{act}<div class="qz-n"><p class="qz-ans">答案：{ans}</p>{note}{fin}</div></div>')


LINT = re.compile(r'真题|常考|必考|考法|每年|常客|命题|每两三年|选择题(的主力|常问)|选填常')
SKIPLINT = re.compile(r'^:::skip.*?^:::$', re.S | re.M)


def lint(no, raw):
    """问法考法不进知识部分：只许出现在实战点评里（:::skip 是取舍声明，不算）"""
    t = SKIPLINT.sub('', raw)
    t = '\n'.join(l for l in t.split('\n') if not l.startswith('本报到此'))
    for m in LINT.finditer(t):
        ERR.append(f'第{no}期：知识部分不写考法，把「{t[max(0, m.start()-12):m.end()+12]}」挪到实战点评')


def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s)


def minutes(raw, nq=0):
    """阅读时长估算：可见中文 280 字/分；展示公式 20 秒；行内公式 3 秒；每道例题再加 2 分钟自己想/对照；实战每题 2.5 分钟"""
    no_math = re.sub(r'\$\$.*?\$\$|\$[^$]+\$', '', raw)
    cn = len(re.findall(r'[一-鿿]', no_math))
    disp, inl = raw.count('$$') // 2, len(re.findall(r'(?<!\$)\$(?!\$)[^$]+\$', raw))
    ex = raw.count(':::ex')
    return round(cn / 280 + disp / 3 + inl * 0.05 + ex * 2 + nq * QTYPE_MIN)


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
<div class="cover-toc"><h4>本期目录</h4><ol>{toc}</ol><p class="hint">读完做{nqs}。→ 键 / 点右缘 / 左滑翻页</p></div>
</div></section>
<section class="stage" id="stage" hidden>
<div class="viewport" id="vp"><div class="flow" id="flow">
{content}
{shizhan}
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


def main():
    load_q()
    W = EX.weights()
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
        lint(no, raw)
        meta, heads, content, ctx = parse(no, raw)
        qs = QS.get(no, [])
        issues.append(dict(no=no, meta=meta, heads=heads, content=content, ctx=ctx, raw=raw, mins=minutes(raw, len(qs)), qs=qs))
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
        sz = ''
        if it['qs']:
            sz = ('<div class="shizhan"><h2>实战</h2><p class="hint">先自己做，再看点评。选择题点选项就判，填空写完再看答案，做错的进错题版。'
                  + (f'本期内容在 2016–2026 的卷子上平均每卷约 {W[no]:g} 分。' if W.get(no) else '') + '</p>'
                  + ''.join(q_html(q, ctx) for q in it['qs']) + '</div>')
            for q in it['qs']:
                PRAC.append(dict(id=q['id'], no=no, html=q_html(q, ctx), ans=q['ans']))
        page = PAGE.format(no=no, shizhan=sz, nqs=f' {len(it["qs"])} 道实战' if it['qs'] else '今日考你', paper=PAPER, title=inline(m['title'], ctx), partname=PARTS.get(m['part'], ''),
                           kicker=esc(m['kicker']), mins=it['mins'], deck=inline(m['deck'], ctx), keep=keep,
                           toc=toc, content=it['content'], recall=recall_html(no, m['recall'], ctx),
                           prev=prev, next=nxt)
        page = page.replace('<title>' + inline(m['title'], ctx), '<title>' + strip_tags(inline(m['title'], ctx)))
        open(os.path.join(ROOT, f'q{no:02d}.html'), 'w', encoding='utf-8').write(page)
    tot = sum(i['mins'] for i in issues)
    idx = [dict(no=i['no'], part=i['meta']['part'], partname=PARTS.get(i['meta']['part'], ''),
                title=strip_tags(i['meta']['title']), kicker=i['meta']['kicker'], deck=strip_tags(i['meta']['deck']),
                mins=i['mins'], ex=i['ctx'].ex, nq=len(i['qs']), w=W.get(i['no'], 0)) for i in issues]
    exam = {y: dict(m=EX.MAP[y], s=EX.scores(y), n=len(EX.OLD if y <= 2020 else EX.NEW)) for y in EX.MAP}
    data = 'window.CD=' + json.dumps({'issues': idx, 'thm': THM, 'recall': RECALL, 'prac': PRAC, 'exam': exam,
                                      'paperYears': EX.PAPER_YEARS, 'drillYears': EX.DRILL_YEARS}, ensure_ascii=False) + ';\n'
    open(os.path.join(ROOT, 'assets', 'data.js'), 'w', encoding='utf-8').write(data)
    PG.write_all(ROOT, idx, issues, THM, inline, esc, EX, TRAPS)
    print(f'{len(issues)} 期 · {tot} 分钟 ≈ {tot/60:.1f} 小时 · 例题 {sum(i["ctx"].ex for i in issues)} · 定理 {len(THM)} · 自测 {len(RECALL)} · 实战 {len(PRAC)}')
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
