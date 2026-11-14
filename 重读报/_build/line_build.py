#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""「一条线」：由 2010–2023 真题倒推的一页式知识回顾。源 _build/line/src.txt ⟹ 一条线.html

用法：python3 _build/line_build.py

语法（一行一个元素）：
  # 卷名 | 一句话主线            分卷
  ## 标题 | 频次                 一站（自动编号）
  > 文字                         形象比方
  ↓ 文字                         通往下一站的桥
  :::mem 标题                    必背。每行「提示 :: 答案」，自测模式下答案被遮住，点一下才显示；没有 :: 的行整行显示
  :::cue 标题                    题眼。每行「看到什么 >> 第一步做什么」
  :::open 标题                   大题开头照写（有序）
  :::trap 标题                   易错
  :::                            块结束
  < 开头的行                     原样 HTML
  其余                           段落
行内：$公式$（小于号写 \\lt）、**粗体**、==划重点==
"""
import html, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from pages import NAV


def inline(s):
    out = []
    for i, part in enumerate(re.split(r'\$([^$]+)\$', s)):
        if i % 2:
            out.append('<span class="m">%s</span>' % html.escape(part, quote=False))
        else:
            part = html.escape(part, quote=False)
            part = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', part)
            part = re.sub(r'==(.+?)==', r'<mark>\1</mark>', part)
            out.append(part)
    return ''.join(out)


def main():
    src = open(os.path.join(HERE, 'line', 'src.txt'), encoding='utf-8').read().split('\n')
    body, toc, n, blk, items, sect_open, part_open = [], [], 0, None, [], False, False

    def flush():
        nonlocal blk, items
        if blk is None: return
        kind, title = blk
        h = '<div class="ln-%s"><h4>%s</h4>' % (kind, inline(title))
        if kind == 'mem':
            h += '<ul>'
            for it in items:
                if ' :: ' in it:
                    a, b = it.split(' :: ', 1)
                    h += '<li><span class="q">%s</span><span class="a">%s</span></li>' % (inline(a), inline(b))
                else:
                    h += '<li>%s</li>' % inline(it)
            h += '</ul>'
        elif kind == 'cue':
            h += '<ul>'
            for it in items:
                a, b = (it.split(' >> ', 1) + [''])[:2]
                h += '<li><span class="sig">%s</span><span class="do">%s</span></li>' % (inline(a), inline(b))
            h += '</ul>'
        elif kind == 'open':
            h += '<ol>' + ''.join('<li>%s</li>' % inline(it) for it in items) + '</ol>'
        else:
            h += '<ul>' + ''.join('<li>%s</li>' % inline(it) for it in items) + '</ul>'
        body.append(h + '</div>')
        blk, items = None, []

    for ln in src:
        s = ln.strip()
        if blk is not None:
            if s == ':::': flush()
            elif s: items.append(s)
            continue
        if not s or s.startswith('//'): continue
        m = re.match(r':::(mem|cue|open|trap)\s*(.*)$', s)
        if m:
            blk = (m.group(1), m.group(2) or {'mem': '必背', 'cue': '题眼', 'open': '大题开头照写', 'trap': '易错'}[m.group(1)]); continue
        if s.startswith('## '):
            if sect_open: body.append('</section>')
            n += 1
            t, _, f = s[3:].partition(' | ')
            body.append('<section class="ln-st" id="s%d"><h3><span class="no">%d</span>%s%s</h3>' % (n, n, inline(t), '<span class="fq">%s</span>' % inline(f) if f else ''))
            toc.append('<a href="#s%d">%d %s</a>' % (n, n, html.escape(re.sub(r'\$|\\', '', t))))
            sect_open = True
        elif s.startswith('# '):
            if sect_open: body.append('</section>'); sect_open = False
            t, _, f = s[2:].partition(' | ')
            pid = 'p%d' % (len([x for x in toc if x.startswith('<b')]) + 1)
            body.append('<div class="ln-part" id="%s"><h2>%s</h2>%s</div>' % (pid, inline(t), '<p>%s</p>' % inline(f) if f else ''))
            toc.append('<b><a href="#%s">%s</a></b>' % (pid, html.escape(t)))
        elif s.startswith('> '):
            body.append('<p class="ln-pic">%s</p>' % inline(s[2:]))
        elif s.startswith('↓ '):
            body.append('<p class="ln-next">%s</p>' % inline(s[2:]))
        elif s.startswith('<'):
            body.append(s)
        else:
            body.append('<p>%s</p>' % inline(s))
    flush()
    if sect_open: body.append('</section>')
    page = open(os.path.join(HERE, 'line', 'page.html'), encoding='utf-8').read()
    page = page.replace('{{nav}}', NAV).replace('{{toc}}', ''.join(toc)).replace('{{body}}', '\n'.join(body))
    open(os.path.join(ROOT, '一条线.html'), 'w', encoding='utf-8').write(page)
    print('✓ 一条线.html：%d 站，%d 字节' % (n, len(page.encode('utf-8'))))


if __name__ == '__main__':
    main()
