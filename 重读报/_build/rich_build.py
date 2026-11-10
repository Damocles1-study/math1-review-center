#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真题套卷「精解」：把 _build/rich/YYYY.txt 编译成 assets/exam/rich/rYYYY.js，题面换成文字、解析换成逐步精解。
数学一重读报与术式408共用同一份脚本（两边各一份，改了要同步），脚本按自己所在位置找目录。

用法：python3 _build/rich_build.py            # 全部年份
      python3 _build/rich_build.py 2021 2022  # 只编这几年（kp.js 每次都重编）

━━━━━━━━━━━━━━━━ 源文件语法 ━━━━━━━━━━━━━━━━
_build/rich/kp.txt（全局，知识点卡与套路卡）：
  @kp id | 标题        下面若干行是内容，到下一个 @kp/@tpl 为止
  @tpl id | 套路名     同上，套路卡（跨年模板）。哪些题用了它由构建自动统计
_build/rich/YYYY.txt（一年一个）：
  @kp / @tpl           同上，只在本年可用（id 不许与全局重名）
  #N                   第 N 题开始
  @stem                题面，下面若干行，到下一个 @ 或 :: 为止
  @A … @B … @C … @D …  选择题四个选项（一行一个）
  @ans 答案            选择题写字母（构建时与卷子答案核对，不一致报错）；填空写结果
  @tpl id, id          本题用到的套路（显示成可点的套路条）
  ::read               读题：一行一句，「原句 >> 看到它想到什么」；不带 >> 的行是普通段落
  ::think              思路（动手前想什么）
  ::fast               秒杀 / 考场快法
  ::steps              详解：一行一步；行首 ~ 表示这一步考场可省；以两个空格、$$、| 开头的行接在上一步
  ::paper              考场卷面（只给解答题）
  ::note               批注：扣分点、边界、提速
  ::vary               举一反三：一行一条，「变式 >> 答案或要点」
  ::sk 宽 高 | 图注    手绘草图，下面是 Python（变量 s 是 Sk 画板，见 sk.py），到下一个 :: 为止
  ::                   单独一行，结束当前块
  块按源文件顺序显示，推荐顺序：read → sk → think → fast → steps → paper → note → vary
行内：
  $…$ 行内公式   $$…$$ 独占一行的公式   `代码`   ```（单独一行）代码块```
  **粗体**  ==红笔重点==  ⛳2（采分点）
  {{省|…}} 考场可省  {{秒|…}} 秒杀  {{圈|…}} 圈出来  {{波|…}} 波浪线  {{扣|…}} 扣分点  {{注|…}} 红笔旁注
  [[id]] 或 [[id|显示文字]]  可点的知识点 / 套路弹窗
  - 列表   1. 有序列表   | 表 | 格 |
"""
import glob, html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, 'rich')
OUT = os.path.join(ROOT, 'assets', 'exam', 'rich')
PAPERS = os.path.join(ROOT, 'assets', 'exam')
sys.path.insert(0, HERE)
from sk import Sk  # noqa: E402

ERR = []
def err(where, msg): ERR.append('%s：%s' % (where, msg))

# ───────────── 行内 ─────────────
MARK = {'省': ('omit', '考场可省'), '秒': ('fast', '秒杀'), '圈': ('circ', ''), '波': ('wavy', ''), '扣': ('dock', '扣分点'), '注': ('hand', '')}

def inline(s, where, ids):
    keep = []
    def stash(h):
        keep.append(h); return '\x00%d\x00' % (len(keep) - 1)
    s = re.sub(r'`([^`]+)`', lambda m: stash('<code>%s</code>' % html.escape(m.group(1))), s)
    s = re.sub(r'\$\$(.+?)\$\$', lambda m: stash('<span class="m md">%s</span>' % html.escape(m.group(1).strip())), s)
    s = re.sub(r'\$([^$]+?)\$', lambda m: stash('<span class="m">%s</span>' % html.escape(m.group(1))), s)
    if '$' in s: err(where, '公式 $ 没配对：' + s[:60])
    def kp(m):
        k, t = m.group(1).strip(), (m.group(2) or '').strip()
        if k not in ids: err(where, '知识点 [[%s]] 没定义' % k)
        return stash('<button class="kpb%s" data-kp="%s">%s</button>' % (' tplb' if ids.get(k, {}).get('k') == 'tpl' else '', html.escape(k), t if t else (inline(ids[k]['t'], where, {}) if k in ids else html.escape(k))))
    s = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]*))?\]\]', kp, s)
    for _ in range(4):
        s2 = re.sub(r'\{\{(省|秒|圈|波|扣|注)\|((?:(?!\{\{).)*?)\}\}', lambda m: '<span class="%s"%s>%s</span>' % (MARK[m.group(1)][0], (' data-t="%s"' % MARK[m.group(1)][1]) if MARK[m.group(1)][1] else '', m.group(2)), s)
        if s2 == s: break
        s = s2
    if '{{' in s: err(where, '{{…}} 标记没闭合或类型不对：' + s[:60])
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'==(.+?)==', r'<span class="r">\1</span>', s)
    s = re.sub(r'⛳\s?(\d+(?:\.\d+)?)', r'<span class="pt">⛳ \1 分</span>', s)
    for _ in range(3):
        s = re.sub(r'\x00(\d+)\x00', lambda m: keep[int(m.group(1))], s)
    return s

def table(rows, where, ids):
    cells = [[c.strip() for c in r.strip().strip('|').split('|')] for r in rows]
    cells = [r for r in cells if not all(re.fullmatch(r':?-{2,}:?', c) for c in r)]
    h = '<div class="tabw"><table class="rt">'
    for i, r in enumerate(cells):
        tg = 'th' if i == 0 else 'td'
        h += '<tr>' + ''.join('<%s>%s</%s>' % (tg, inline(c, where, ids), tg) for c in r) + '</tr>'
    return h + '</table></div>'

def lines_html(lines, where, ids):
    """通用段落：- 列表 / 1. 列表 / 表格 / ``` 代码 / $$ 公式 / 普通行各成一段"""
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if not l.strip(): i += 1; continue
        if l.strip().startswith('```'):
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].strip().startswith('```'): buf.append(lines[j]); j += 1
            if j >= len(lines): err(where, '``` 代码块没闭合')
            out.append('<pre class="code">%s</pre>' % html.escape('\n'.join(buf))); i = j + 1; continue
        if l.lstrip().startswith('|'):
            j = i; buf = []
            while j < len(lines) and lines[j].lstrip().startswith('|'): buf.append(lines[j]); j += 1
            out.append(table(buf, where, ids)); i = j; continue
        m = re.match(r'\s*(-|\d+\.)\s+', l)
        if m:
            tagn = 'ul' if m.group(1) == '-' else 'ol'; j = i; items = []
            while j < len(lines):
                mm = re.match(r'\s*(-|\d+\.)\s+(.*)', lines[j])
                if mm and (mm.group(1) == '-') == (tagn == 'ul'): items.append(mm.group(2)); j += 1
                elif items and lines[j].startswith('  ') and lines[j].strip(): items[-1] += '<br>' + lines[j].strip(); j += 1
                else: break
            out.append('<%s>%s</%s>' % (tagn, ''.join('<li>%s</li>' % inline(t, where, ids) for t in items), tagn)); i = j; continue
        t = l.strip()
        if t.startswith('$$') and t.endswith('$$') and len(t) > 4:
            out.append('<div class="mdw">%s</div>' % inline(t, where, ids))
        else:
            out.append('<p>%s</p>' % inline(t, where, ids))
        i += 1
    return ''.join(out)

def fit_svg(svg, w, h):
    """按文字的估算外框把 viewBox 撑大，避免标注被画板边缘裁掉（中文按 1 个字号宽、其余按 0.58）"""
    x0, y0, x1, y1 = 0.0, 0.0, float(w), float(h)
    for m in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)" font-size="([\d.]+)"[^>]*text-anchor="(\w+)"[^>]*>(.*?)</text>', svg):
        x, y, fs, an = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
        t = re.sub(r'<tspan[^>]*font-size[^>]*>(.*?)</tspan>', lambda k: k.group(1)[:max(1, len(k.group(1)) * 3 // 4)], m.group(5))
        t = html.unescape(re.sub(r'<[^>]+>', '', t)).replace('\u200b', '')
        tw = sum(fs if ord(c) > 0x2e80 else fs * 0.58 for c in t)
        a = x - tw / 2 if an == 'middle' else x - tw if an == 'end' else x
        x0, x1, y0, y1 = min(x0, a - 2), max(x1, a + tw + 2), min(y0, y - fs - 2), max(y1, y + fs * 0.3 + 2)
    if (x0, y0, x1, y1) == (0, 0, w, h): return svg
    W, H = x1 - x0, y1 - y0
    return re.sub(r'viewBox="0 0 \d+ \d+" width="\d+"', 'viewBox="%.0f %.0f %.0f %.0f" width="%d"' % (x0, y0, W, H, round(W * 1.22)), svg, count=1)

# ───────────── 块 ─────────────
HEAD = {'read': ('📖', '读题 · 圈画'), 'think': ('💭', '思路'), 'fast': ('⚡', '秒杀 · 考场快法'), 'steps': ('🧮', '详解（每一步）'),
        'paper': ('✍️', '考场卷面'), 'note': ('📌', '批注'), 'vary': ('🔁', '举一反三'), 'sk': ('✏️', '草图')}

def block_html(kind, arg, lines, where, ids, seed):
    ic, nm = HEAD[kind]
    if kind == 'sk':
        m = re.match(r'(\d+)\s+(\d+)\s*(?:\|\s*(.*))?$', arg or '')
        if not m: err(where, '::sk 要写「宽 高 | 图注」'); return ''
        w, h, cap = int(m.group(1)), int(m.group(2)), m.group(3) or ''
        s = Sk(w, h, seed=seed)
        try:
            import math, random  # noqa: F401  给草图代码用
            exec('\n'.join(lines), {'s': s, 'math': math, 'random': random, 'Sk': Sk})
        except Exception as e:
            err(where, '草图代码出错：%r' % e); return ''
        return '<figure class="rb rb-sk">%s%s</figure>' % (fit_svg(s.svg(cls='sk', alt=cap), w, h), ('<figcaption>%s</figcaption>' % inline(cap, where, ids)) if cap else '')
    title = inline(arg, where, ids) if arg else nm
    if kind == 'read':
        body = ''
        for l in lines:
            if not l.strip(): continue
            if '>>' in l:
                a, b = l.split('>>', 1)
                body += '<div class="rd"><span class="rq">%s</span><span class="ra">%s</span></div>' % (inline(a.strip(), where, ids), inline(b.strip(), where, ids))
            else:
                body += lines_html([l], where, ids)
    elif kind == 'steps':
        steps = []
        for l in lines:
            if not l.strip(): continue
            if steps and (l.startswith('  ') or l.lstrip().startswith('$$') or l.lstrip().startswith('|') or l.lstrip().startswith('```') or steps[-1][2]):
                st = steps[-1]
                st[1].append(l)
                if l.strip().startswith('```'): st[2] = not st[2]
                continue
            om = l.startswith('~')
            t = l[1:] if om else l
            steps.append([om, [t], t.strip().startswith('```') and not t.strip().endswith('```')])
        body = '<ol class="steps">' + ''.join('<li%s>%s</li>' % (' class="omit-s" data-t="考场可省"' if om else '', lines_html([x.strip() if not x.lstrip().startswith('```') else x.strip() for x in ls], where, ids)) for om, ls, _ in steps) + '</ol>'
    elif kind == 'vary':
        body = '<ol class="vary">'
        for l in lines:
            if not l.strip(): continue
            a, b = (l.split('>>', 1) + [''])[:2]
            body += '<li><span class="vq">%s</span>%s</li>' % (inline(a.strip(), where, ids), ('<span class="va">%s</span>' % inline(b.strip(), where, ids)) if b.strip() else '')
        body += '</ol>'
    else:
        body = lines_html(lines, where, ids)
    return '<section class="rb rb-%s"><h5><i>%s</i>%s</h5>%s</section>' % (kind, ic, title, body)

# ───────────── 解析源文件 ─────────────
def parse_defs(text, fname, store, local=False):
    """@kp / @tpl 定义，返回剩下的行"""
    rest, cur = [], None
    for ln, l in enumerate(text.split('\n'), 1):
        m = re.match(r'@(kp|tpl)\s+([^|]+?)\s*\|\s*(.+)$', l)
        if m:
            k = m.group(2)
            if k in store: err('%s:%d' % (fname, ln), '%s 重复定义' % k)
            cur = store[k] = {'k': m.group(1), 't': m.group(3).strip(), 'src': [], 'local': local}
            continue
        if cur is not None and (l.startswith('#') or (l.startswith('@') and not l.startswith('@kp') and not l.startswith('@tpl'))):
            cur = None
        if cur is not None:
            if not l.startswith('//'): cur['src'].append(l)   # 卡与卡之间的 // 注释不算进卡片内容
        else: rest.append((ln, l))
    return rest

def parse_year(rest, fname):
    Q, q, blk = {}, None, None
    for ln, l in rest:
        m = re.match(r'#(\d+)\s*$', l)
        if m:
            q = Q.setdefault(int(m.group(1)), {'stem': [], 'opts': {}, 'blocks': [], 'tpl': [], 'ln': ln})
            blk = None; continue
        if q is None:
            if l.strip() and not l.startswith('//'): err('%s:%d' % (fname, ln), '题号 #N 之前只能写 @kp/@tpl')
            continue
        m = re.match(r'::(\w*)\s*(.*)$', l)
        if m:
            kind, arg = m.group(1), m.group(2).strip()
            if not kind: blk = None; continue
            if kind not in HEAD: err('%s:%d' % (fname, ln), '不认识的块 ::%s' % kind); blk = None; continue
            blk = [kind, arg, [], ln]; q['blocks'].append(blk); continue
        m = re.match(r'@(stem|ans|tpl|A|B|C|D)\b\s*(.*)$', l)
        if m and (blk is None or blk[0] != 'sk'):
            k, v = m.group(1), m.group(2)
            blk = None
            if k == 'stem': q['stem'] = [v] if v else []; blk = ['@stem']
            elif k == 'ans': q['ans'] = v.strip()
            elif k == 'tpl': q['tpl'] += [x.strip() for x in v.split(',') if x.strip()]
            else: q['opts'][k] = v.strip(); blk = ['@opt', k]
            continue
        if blk is None:
            if l.strip() and not l.startswith('//'): err('%s:%d' % (fname, ln), '这一行不在任何块里：' + l[:40])
            continue
        if blk[0] == '@stem': q['stem'].append(l)
        elif blk[0] == '@opt': q['opts'][blk[1]] += '\n' + l if l.strip() else ''
        else: blk[2].append(l)
    return Q

def paper_of(y):
    p = os.path.join(PAPERS, 'y%d.js' % y)
    if not os.path.exists(p): return None
    s = open(p, encoding='utf-8').read()
    return json.loads(s[s.index('=', s.index(']')) + 1:].rstrip().rstrip(';'))

def tagcheck(h, where):
    st = []
    for m in re.finditer(r'<(/?)([a-z0-9]+)\b[^>]*?(/?)>', h):
        t = m.group(2)
        if t in ('br', 'img', 'hr', 'input', 'path', 'circle', 'line', 'rect', 'ellipse', 'tspan', 'polyline', 'polygon', 'text', 'svg', 'g', 'defs', 'marker') or m.group(3): continue
        if m.group(1):
            if not st or st[-1] != t: err(where, 'HTML 标签不配平：多出 </%s>' % t); return
            st.pop()
        else: st.append(t)
    if st: err(where, 'HTML 标签不配平：%s 没闭合' % st)

def main():
    os.makedirs(OUT, exist_ok=True)
    want = [int(a) for a in sys.argv[1:] if a.isdigit()]
    G = {}
    gp = os.path.join(SRC, 'kp.txt')
    if os.path.exists(gp): parse_defs(open(gp, encoding='utf-8').read(), 'kp.txt', G)
    files = sorted(glob.glob(os.path.join(SRC, '[12][09][0-9][0-9].txt')))
    uses, years, summary = {}, [], []
    for f in files:
        y = int(os.path.basename(f)[:4]); years.append(y)
        L = {}
        n0 = len(ERR)
        text = open(f, encoding='utf-8').read()
        rest = parse_defs(text, os.path.basename(f), L, local=True)
        for k in L:
            if k in G: err('%d.txt' % y, '本年 %s 与全局 kp.txt 重名' % k)
        ids = dict(G); ids.update(L)
        Q = parse_year(rest, os.path.basename(f))
        for no, q in Q.items():
            for t in q['tpl']:
                uses.setdefault(t, []).append([y, no])
        if want and y not in want:
            del ERR[n0:]   # 只编指定年份时，别的年份（可能正被别的会话改着）报的错不算
            continue
        P = paper_of(y)
        pq = {x['no']: x for x in P['q']} if P else {}
        outq = {}
        for no, q in sorted(Q.items()):
            where = '%d 第 %d 题' % (y, no)
            if pq and no not in pq: err(where, '卷子里没有这道题'); continue
            pv = pq.get(no, {})
            r = {}
            if q['stem']: r['stem'] = lines_html(q['stem'], where, ids)
            if q['opts']:
                if sorted(q['opts']) != ['A', 'B', 'C', 'D']: err(where, '选项要 A–D 四个')
                r['opts'] = [inline(q['opts'].get(k, ''), where, ids) for k in 'ABCD']
            if pv.get('type') == 'choice':
                if q.get('ans') and pv.get('ans') and q['ans'] != pv['ans']: err(where, '答案 %s 与卷子 %s 不一致' % (q['ans'], pv['ans']))
                if q['stem'] and not q['opts'] and not pv.get('opts'): err(where, '选择题写了题面却没写选项')
            elif q.get('ans'):
                r['ans'] = inline(q['ans'], where, ids)
            for t in q['tpl']:
                if t not in ids or ids[t]['k'] != 'tpl': err(where, '@tpl %s 不是已定义的套路' % t)
            if q['tpl']: r['tpl'] = q['tpl']
            if q['blocks']:
                r['sol'] = ''.join(block_html(b[0], b[1], b[2], where + '（%s 块，第 %d 行）' % (b[0], b[3]), ids, seed=y * 100 + no * 7 + i) for i, b in enumerate(q['blocks']))
            for k in ('stem', 'sol'):
                if k in r: tagcheck(r[k], where + ' ' + k)
            outq[no] = r
        lk = {k: {'k': v['k'], 't': inline(v['t'], 'kp ' + k, ids), 'h': lines_html(v['src'], 'kp ' + k, ids)} for k, v in L.items()}
        js = '(window.EXAM_RICH=window.EXAM_RICH||{})[%d]=%s;\n' % (y, json.dumps({'q': outq, 'kp': lk}, ensure_ascii=False, separators=(',', ':')))
        open(os.path.join(OUT, 'r%d.js' % y), 'w', encoding='utf-8').write(js)
        nst = sum(1 for r in outq.values() if 'stem' in r); nsol = sum(1 for r in outq.values() if 'sol' in r)
        tot = len(P['q']) if P else 0
        summary.append('%d：题面 %d/%d · 精解 %d/%d · 草图 %d' % (y, nst, tot, nsol, tot, text.count('::sk ')))
    gk = {k: {'k': v['k'], 't': inline(v['t'], 'kp ' + k, G), 'h': lines_html(v['src'], 'kp ' + k, G)} for k, v in G.items()}
    for k, v in gk.items():
        if k in uses: v['u'] = sorted(uses[k])
    # 本年局部套路的用处也记下（弹窗里显示）
    open(os.path.join(OUT, 'kp.js'), 'w', encoding='utf-8').write('window.EXAM_KP=%s;\nwindow.EXAM_RICH_YEARS=%s;\nwindow.EXAM_TPL_USES=%s;\n' % (
        json.dumps(gk, ensure_ascii=False, separators=(',', ':')), json.dumps(years), json.dumps(uses, ensure_ascii=False, separators=(',', ':'))))
    print('\n'.join(summary))
    if ERR:
        print('\n✗ %d 处问题：' % len(ERR)); print('\n'.join('  ' + e for e in ERR)); sys.exit(1)
    print('✓ 通过')

if __name__ == '__main__':
    main()
