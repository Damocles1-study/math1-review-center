#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把某年精解文件顶部的本年卡（@kp/@tpl）提到全局 _build/rich/kp.txt，再把其他年份里与全局重名的本年卡删掉（改用全局）。
用法：python3 _build/rich_promote.py 2022 [2023 …]      （重读报与术式408各一份，内容相同）
只在没有别的会话正写这些年份时跑。跑完再 python3 _build/rich_build.py。"""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
RICH = os.path.join(HERE, 'rich')
KP = os.path.join(RICH, 'kp.txt')
ID = re.compile(r'@(?:kp|tpl)\s+([^|]+?)\s*\|')

def split(path):
    s = open(path, encoding='utf-8').read()
    m = re.search(r'^#\d+\s*$', s, re.M)
    i = m.start() if m else len(s)
    return re.split(r'(?m)^(?=@(?:kp|tpl)\s)', s[:i]), s[i:]

def gids():
    return set(ID.findall(open(KP, encoding='utf-8').read()))

for y in sys.argv[1:]:
    p = os.path.join(RICH, '%s.txt' % y)
    defs, body = split(p)
    have = gids()
    up = [d for d in defs if d.startswith('@') and ID.match(d).group(1) not in have]
    rest = [d for d in defs if not (d.startswith('@') and ID.match(d).group(1) not in have)]
    if up:
        g = open(KP, encoding='utf-8').read().rstrip()
        open(KP, 'w', encoding='utf-8').write(g + '\n\n// ── 由 %s 年精解提上来 ──\n\n' % y + '\n'.join(d.rstrip() + '\n' for d in up))
    open(p, 'w', encoding='utf-8').write(''.join(rest).rstrip() + '\n\n' + body)
    print('%s：提上去 %d 张' % (y, len(up)))

have = gids()
for p in sorted(glob.glob(os.path.join(RICH, '[12][09][0-9][0-9].txt'))):
    defs, body = split(p)
    drop = [ID.match(d).group(1) for d in defs if d.startswith('@') and ID.match(d).group(1) in have]
    if drop:
        keep = [d for d in defs if not (d.startswith('@') and ID.match(d).group(1) in have)]
        open(p, 'w', encoding='utf-8').write(''.join(keep).rstrip() + '\n\n' + body)
        print('%s：删掉与全局重名的本年卡 %s' % (os.path.basename(p), drop))
