#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真题精研：_build/deep/YYYY.txt → assets/exam/deep/dYYYY.js（交卷后才显示）。
只给写了 YYYY.txt 的年份生成（回第几期的链接卷子数据里已经有了）。公式写 $…$，页面上用本地 KaTeX 渲染。

源文件语法（纯文本，自动转义 < > &）：
  @time 120                 复盘限时（分钟）
  @look 一段话               这张卷长什么样、复盘重心
  @route 一步                复盘路线，可多行，按顺序
  @core 41,42,45            必吃透的题号（不写则取所有 ★★★）
  #12 ★★★                  一张卡：题号 + 等级（★ / ★★ / ★★★）
  考 …   本 …   出 …   变 …   联 …     五栏：考什么 / 本质 / 怎么出的 / 举一反三 / 联想搭配
  以「- 」开头的行是该栏里的列表项；其他不以栏名开头的行接在上一栏后面。
  行内：**粗体**  ==红字==  $公式$
"""
import json, os, re, sys, html

H = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(H)

SRC = os.path.join(H, 'deep')
OUT = os.path.join(ROOT, 'assets', 'exam', 'deep')
YEARS = range(2010, 2027)
KEYS = {'考': 'k', '本': 'core', '出': 'how', '变': 'vary', '联': 'link'}


def inline(t):
    maths = []
    def keep(m):
        maths.append(m.group(1)); return '\x00%d\x00' % (len(maths) - 1)
    t = re.sub(r'\$([^$]+)\$', keep, t)
    t = html.escape(t, quote=False)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'==(.+?)==', r'<span class="r">\1</span>', t)
    t = re.sub(r'\x00(\d+)\x00', lambda m: '<span class="m">%s</span>' % html.escape(maths[int(m.group(1))], quote=False), t)
    return t


def field_html(lines):
    out, ul = [], []
    for ln in lines:
        if ln.startswith('- '):
            ul.append('<li>' + inline(ln[2:].strip()) + '</li>')
        else:
            if ul:
                out.append('<ul>' + ''.join(ul) + '</ul>'); ul = []
            out.append(inline(ln))
    if ul:
        out.append('<ul>' + ''.join(ul) + '</ul>')
    s = ''
    for i, x in enumerate(out):
        if i and not x.startswith('<ul>') and not out[i - 1].startswith('<ul>'):
            s += '<br>'
        s += x
    return s


def parse(path):
    D = {'route': [], 'q': {}}
    cur = None; key = None; buf = {}

    def flush():
        if cur is not None:
            for k, v in buf.items():
                D['q'][cur][k] = field_html(v)
    for raw in open(path, encoding='utf-8'):
        ln = raw.rstrip('\n').rstrip()
        if not ln.strip() or ln.lstrip().startswith('//'):
            continue
        if ln.startswith('@time '):
            D['time'] = int(ln[6:].strip()); continue
        if ln.startswith('@look '):
            D['look'] = inline(ln[6:].strip()); continue
        if ln.startswith('@route '):
            D['route'].append(inline(ln[7:].strip())); continue
        if ln.startswith('@core '):
            D['core'] = [int(x) for x in re.split(r'[,，\s]+', ln[6:].strip()) if x]; continue
        m = re.match(r'^#(\d+)\s*(★*)', ln)
        if m:
            flush(); cur = int(m.group(1)); key = None; buf = {}
            assert cur not in D['q'], ('重复题号', path, cur)
            D['q'][cur] = {'lv': max(1, len(m.group(2)) or 2)}
            continue
        m = re.match(r'^(考|本|出|变|联)\s+(.*)$', ln)
        if m and cur is not None:
            key = KEYS[m.group(1)]; buf.setdefault(key, []).append(m.group(2).strip()); continue
        assert cur is not None and key is not None, ('无法归属的行', path, ln)
        buf[key].append(ln.strip())
    flush()
    if 'core' not in D:
        D['core'] = sorted(n for n, q in D['q'].items() if q['lv'] >= 3)
    return D


def load_paper(y):
    s = open(os.path.join(ROOT, 'assets', 'exam', 'y%d.js' % y), encoding='utf-8').read()
    return json.loads(s[s.index('=', s.index('[%d]' % y)) + 1:].rstrip().rstrip(';'))


def main():
    os.makedirs(OUT, exist_ok=True)
    full = []
    for y in YEARS:
        P = load_paper(y)
        path = os.path.join(SRC, '%d.txt' % y)
        if not os.path.exists(path):
            continue
        D = parse(path)
        nos = {q['no'] for q in P['q']}
        for n in D['q']:
            assert n in nos, ('题号不在卷中', y, n)
        if os.path.exists(path):
            full.append(y)
            lacks = sorted(nos - {n for n, v in D['q'].items() if 'core' in v})
            if lacks:
                print('  %d 未写精研卡的题：%s' % (y, lacks))
        D['q'] = {str(k): v for k, v in sorted(D['q'].items())}
        open(os.path.join(OUT, 'd%d.js' % y), 'w', encoding='utf-8').write(
            '(window.EXAM_DEEP=window.EXAM_DEEP||{})[%d]=%s;\n' % (y, json.dumps(D, ensure_ascii=False, separators=(',', ':'))))
    open(os.path.join(OUT, 'index.js'), 'w', encoding='utf-8').write('window.EXAM_DEEP_YEARS=%s;\n' % json.dumps(full))
    print('精研已写：', full)


if __name__ == '__main__':
    main()
