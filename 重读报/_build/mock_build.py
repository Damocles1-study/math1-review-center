#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""数学一模拟卷：把 _build/mock/3NNN.txt 编成 assets/exam/y3NNN.js，接进在线套卷（真题套卷.html）。

为什么是 3001、3002……：套卷引擎的路由只认 #y=四位数字，模拟卷借用四位编号，不改引擎。
引擎、样式（assets/exam/engine.js、exam.css）与 408 共用，这里只生成数据。

用法：python3 _build/mock_build.py          # 全部模拟卷
      python3 _build/mock_build.py 3002     # 只编一套

━━━━ 源文件语法 ━━━━
与 _build/rich/YYYY.txt 完全相同（见 rich_build.py 开头），另加三种行：
  @paper 名称 | 一句话说明        文件开头，写在第一题之前
  @at N                         本题归在重读报第 N 期（与 exam_map.MOCK 核对，交卷后显示「回第 N 期」）
  @src 出处                     题源：自编 / 改编自重读报第 N 期例题 / 经典题型……（显示在解析最前面）
题型和分值按题号定：1–10 选择 5 分，11–16 填空 5 分，17 解答 10 分，18–22 解答 12 分（数一 2021 起的结构）。

知识点卡：除了 kp.txt 的全局卡，还可以写 [[R.定理id|显示文字]]——R. 后面是重读报 _src 里 :::thm 的 id。
构建时把那条定理的全文抄进弹窗，并附「重读报第 N 期整页打开」的链接（新标签打开，关掉就回到原题）。
这些卡写进 assets/exam/mock_kp.js（不带参数构建时生成），真题套卷.html 在 kp.js 之后引入它；y3NNN.js 只放卷子一条语句。
另生成 assets/exam/deep/d3NNN.js（交卷后的「这张卷怎么复盘」和每题精研卡）：由每题 ::rev 的 保底 / 带走 / 卡点 / 错了说明
和 _build/tier/3NNN.txt 的档自动拼出，不用另写（引擎打开任何一卷都会请求 deep 文件，没有就 404）。

校验（不过退出码 1）：22 题齐全、总分 150、选择题四个选项和字母答案、填空解答有 @ans、
解答题必须有 ::paper（三层卷面）且卷面里有 ⛳ 采分点、选填必须有 ::fast、每题有 @at 与 @src、
[[id]] 都有定义、$ 配对、HTML 标签配平（rich_build 的同一套检查）。
"""
import glob, html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import rich_build as RB  # noqa: E402
import exam_map as EX  # noqa: E402

SRC = os.path.join(HERE, 'mock')
OUT = os.path.join(ROOT, 'assets', 'exam')
ERR = RB.ERR


def err(w, m): ERR.append('%s：%s' % (w, m))


def qtype(no):
    return ('choice', 5) if no <= 10 else ('blank', 5) if no <= 16 else ('essay', 10 if no == 17 else 12)


# ───── 重读报定理 → 知识点卡 ─────
def thm_cards():
    names, raw = {}, {}
    for f in sorted(glob.glob(os.path.join(ROOT, '_src', '[0-3][0-9].txt'))):
        no = int(os.path.basename(f)[:2])
        s = open(f, encoding='utf-8').read()
        title = (re.search(r'^@kicker\s+(.*)$', s, re.M) or re.search(r'^@title\s+(.*)$', s, re.M)).group(1).strip()
        for m in re.finditer(r'^:::thm ([^|\n]+?)\s*\|\s*([^|\n]+?)(?:\s*\|\s*([^\n]*))?\n(.*?)^:::\s*$', s, re.M | re.S):
            tid = m.group(1).strip()
            names[tid] = m.group(2).strip()
            raw[tid] = (no, title, m.group(2).strip(), m.group(4))
    cards = {}
    for tid, (no, title, name, body) in raw.items():
        b = re.sub(r'\[\[([^\]|]+)(?:\|([^\]]*))?\]\]', lambda k: '「' + (k.group(2) or names.get(k.group(1).strip(), k.group(1))) + '」', body)
        b = re.sub(r'⛳\s?\d+(?:\.\d+)?', '', b).replace('∎', '')
        lines = [l for l in b.split('\n') if not l.startswith('!fig')]
        lines.append('<a class="rlink" href="q%02d.html" target="_blank" rel="noopener">重读报第 %d 期《%s》整页打开 ↗</a>（新标签打开，看完关掉就回到这题）' % (no, no, html.escape(title)))
        cards['R.' + tid] = {'k': 'kp', 't': '第 %d 期 · %s' % (no, name), 'src': lines, 'local': True}
    return cards


def kickers():
    out = {}
    for f in sorted(glob.glob(os.path.join(ROOT, '_src', '[0-3][0-9].txt'))):
        m = re.search(r'^@kicker\s+(.*)$', open(f, encoding='utf-8').read(), re.M)
        out[int(os.path.basename(f)[:2])] = m.group(1).strip() if m else ''
    return out


def tiers(pid):
    """_build/tier/3NNN.txt → {题号: 档 必/常/冲 或 'essay'}"""
    out, p = {}, os.path.join(HERE, 'tier', '%s.txt' % pid)
    if not os.path.exists(p): return out
    for l in open(p, encoding='utf-8'):
        m = re.match(r'(\d+)\s+(\S+)\s', l)
        if m: out[int(m.group(1))] = m.group(2) if m.group(2) in ('必', '常', '冲', '弃') else 'essay'
    return out


def rev_lines(q):
    out = {}
    for blk in q['blocks']:
        if blk[0] != 'rev': continue
        for l in blk[2]:
            m = re.match(r'-\s*\*\*(\S+?)\*\*\s*(.*)$', l.strip())
            if m: out[m.group(1)] = m.group(2)
    return out


def main():
    want = [a for a in sys.argv[1:] if a.isdigit()]
    KI = kickers()
    G = {}
    RB.parse_defs(open(os.path.join(HERE, 'rich', 'kp.txt'), encoding='utf-8').read(), 'kp.txt', G)
    R = thm_cards()
    files = sorted(glob.glob(os.path.join(SRC, '3[0-9][0-9][0-9].txt')))
    summary = []
    ALLKP = {}
    for f in files:
        pid = os.path.basename(f)[:4]
        if want and pid not in want: continue
        y = int(pid)
        text = open(f, encoding='utf-8').read()
        meta, at, src = {}, {}, {}
        lines, qcur = [], None
        for ln, l in enumerate(text.split('\n'), 1):   # 先抽走三种附加行（换成注释，保住行号）
            m = re.match(r'#(\d+)\s*$', l)
            if m: qcur = int(m.group(1))
            m = re.match(r'@(paper|at|src)\s+(.*)$', l)
            if m:
                k, v = m.group(1), m.group(2).strip()
                if k == 'paper':
                    nm, _, ds = v.partition('|'); meta = {'name': nm.strip(), 'desc': ds.strip()}
                elif qcur is None: err('%s:%d' % (pid, ln), '@%s 要写在题号之后' % k)
                elif k == 'at': at[qcur] = int(v)
                else: src[qcur] = v
                l = '// ' + l
            lines.append(l)
        L = {}
        rest = RB.parse_defs('\n'.join(lines), pid + '.txt', L, local=True)
        ids = dict(G); ids.update(R); ids.update(L)
        Q = RB.parse_year(rest, pid + '.txt')
        if not meta: err(pid, '缺 @paper')
        if sorted(Q) != list(range(1, 23)): err(pid, '题号要 1–22 齐全，现在是 %s' % sorted(Q))
        mock = EX.MOCK.get(y)
        if not mock: err(pid, 'exam_map.MOCK 里没有 %d' % y)
        used, out, DQ, TR = set(), [], {}, tiers(pid)
        for no, q in sorted(Q.items()):
            w = '%s 第 %d 题' % (pid, no)
            tp, sc = qtype(no)
            rec = {'no': no, 'type': tp, 'score': sc}
            if not q['stem']: err(w, '没写 @stem')
            rec['stem'] = RB.lines_html(q['stem'], w, ids)
            kinds = [b[0] for b in q['blocks']]
            if tp == 'choice':
                if sorted(q['opts']) != ['A', 'B', 'C', 'D']: err(w, '选项要 A–D 四个')
                rec['opts'] = [RB.inline(q['opts'].get(k, ''), w, ids) for k in 'ABCD']
                if q.get('ans') not in list('ABCD'): err(w, '选择题 @ans 要写一个字母')
                rec['ans'] = q.get('ans')
            else:
                if q['opts']: err(w, '只有选择题写选项')
                if not q.get('ans'): err(w, '没写 @ans')
                else: rec['ansText'] = RB.inline(q['ans'], w, ids)
            if tp == 'essay':
                if 'paper' not in kinds: err(w, '解答题要写 ::paper（三层卷面）')
                elif not any('⛳' in l for b in q['blocks'] if b[0] == 'paper' for l in b[2]): err(w, '卷面里没有 ⛳ 采分点')
                if 'think' not in kinds: err(w, '解答题要写 ::think')
            elif 'fast' not in kinds: err(w, '选填要写 ::fast（秒杀 / 速判）')
            if 'steps' not in kinds: err(w, '没写 ::steps')
            for t in q['tpl']:
                if t not in ids or ids[t]['k'] != 'tpl': err(w, '@tpl %s 不是已定义的套路' % t)
            if q['tpl']: rec['tpl'] = q['tpl']
            if no not in src: err(w, '没写 @src')
            if no not in at: err(w, '没写 @at')
            elif mock and (len(mock) < no or mock[no - 1] != at[no]):
                err(w, '@at %d 与 exam_map.MOCK 记的 %s 不一致' % (at[no], mock[no - 1] if mock and len(mock) >= no else '无'))
            sol = '<p class="msrc"><small>题源：%s</small></p>' % RB.inline(src.get(no, ''), w, ids)
            sol += ''.join(RB.block_html(b[0], b[1], b[2], w + '（%s 块，第 %d 行）' % (b[0], b[3]), ids, seed=y * 100 + no * 7 + i) for i, b in enumerate(q['blocks']))
            for k2, h in (('stem', rec['stem']), ('sol', sol)): RB.tagcheck(h, w + ' ' + k2)
            rec['rich'] = sol.replace('⛳ ', '').replace('⛳', '')
            if no in at: rec['back'] = {'href': 'q%02d.html' % at[no], 'text': '这题归在第 %d 期，回去看 →' % at[no]}
            for h in (rec['stem'], rec['rich']) + tuple(rec.get('opts', [])):
                for k3 in re.findall(r'data-kp="([^"]+)"', h): used.add(html.unescape(k3))
            used.update(q['tpl'])
            out.append(rec)
            rv, tr = rev_lines(q), TR.get(no)
            card = {'lv': 3 if tp == 'essay' or tr == '必' else 2 if tr == '常' else 1}
            k = '第 %d 期 · %s' % (at.get(no, 0), KI.get(at.get(no, 0), ''))
            if q['tpl']: k += '；套路：' + '、'.join(RB.inline(ids[t]['t'], w, ids) for t in q['tpl'] if t in ids)
            if rv.get('保底'): k += '<br>保底：' + RB.inline(rv['保底'], w, ids)
            card['k'] = k
            if rv.get('带走'): card['core'] = RB.inline(rv['带走'], w, ids)
            if rv.get('卡点'): card['how'] = '坑设在：' + RB.inline(rv['卡点'], w, ids) + ('　' + RB.inline(rv['错了说明'], w, ids) if rv.get('错了说明') else '')
            DQ[no] = card
        tot = sum(r['score'] for r in out)
        if tot != 150: err(pid, '总分 %d ≠ 150' % tot)
        kp = {}
        for k in sorted(used):
            if k in R or k in L:
                v = (R.get(k) or L[k])
                kp[k] = {'k': v['k'], 't': RB.inline(v['t'], 'kp ' + k, ids), 'h': RB.lines_html(v['src'], 'kp ' + k, ids)}
        paper = {'year': y, 'mock': 1, 'name': meta.get('name', ''), 'desc': meta.get('desc', ''), 'q': out}
        js = '(window.EXAM_PAPERS=window.EXAM_PAPERS||{})[%d]=%s;\n' % (y, json.dumps(paper, ensure_ascii=False, separators=(',', ':')))
        open(os.path.join(OUT, 'y%d.js' % y), 'w', encoding='utf-8').write(js)   # 只放一条语句：tier_build 按 JSON 读它
        deep = {'time': 120, 'core': [n for n in range(17, 23)],
                'look': RB.inline(meta.get('desc', ''), pid, ids) + ' 六道解答题都列为必吃透：先对照每题的「保底」——那一步你写出来了吗、写对了吗；再看第二问卡在哪。',
                'route': ['对答案、登分（15 分钟）：选择题自动判，填空和解答按卷面的 ⛳ 采分点逐步给自己打分，成绩同步到套卷台。',
                          '解答题逐题过「保底」（30 分钟）：每题第一问没拿到的，合上解析把那一步重写一遍，直到不看也能写。',
                          '重做失分的选填（30 分钟）：先看「秒杀」那一块，再看「每一步」；还不会就点知识点卡，回到重读报那一期。',
                          '记一行（10 分钟）：每道失分题在「我的批注」里写「下次看到什么，就先写什么」。到点就停。'],
                'q': DQ}
        open(os.path.join(OUT, 'deep', 'd%d.js' % y), 'w', encoding='utf-8').write(
            '(window.EXAM_DEEP=window.EXAM_DEEP||{})[%d]=%s;\n' % (y, json.dumps(deep, ensure_ascii=False, separators=(',', ':'))))
        ALLKP.update(kp)
        summary.append('%d %s：%d 题 · %d 分 · 草图 %d · 知识点卡 %d（重读报定理 %d）' % (y, meta.get('name', ''), len(out), tot, text.count('::sk '), len(used), sum(1 for k in used if k in R)))
    if not want:   # 知识点卡单独一个文件，页面在 engine.js 之前引入（重读报定理卡 + 模拟卷本卷卡）
        open(os.path.join(OUT, 'mock_kp.js'), 'w', encoding='utf-8').write(
            '(function(K){var A=window.EXAM_KP=window.EXAM_KP||{};for(var k in K)if(!A[k])A[k]=K[k];})(%s);\n' % json.dumps(ALLKP, ensure_ascii=False, separators=(',', ':')))
    print('\n'.join(summary))
    if ERR:
        print('\n✗ %d 处问题：' % len(ERR)); print('\n'.join('  ' + e for e in ERR)); sys.exit(1)
    print('✓ 通过')


if __name__ == '__main__':
    main()
