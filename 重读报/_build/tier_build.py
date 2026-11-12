#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真题套卷「分档 · 限时 · 三条分数线」：把 _build/tier/YYYY.txt 编成 assets/exam/tier.js。
数学一重读报与术式408共用同一份脚本（两边各一份，改了要同步）。

用法：python3 _build/tier_build.py

━━━━ 源文件语法（一年一个 _build/tier/YYYY.txt）━━━━
  // 注释
  @note 一句话        这张卷的拿分结构（显示在成绩单的三条线下面，可省）
  题号 档 分钟 | 说明
      档＝必 / 常 / 冲 / 弃（整题归一档，选择、填空一般这样写）
      或 a/b/c/x 四个数（解答题按问拆：保底拿 a 分、正常再拿 b 分、冲刺再拿 c 分、战略放弃 x 分，和＝本题满分）
      分钟＝考场上这题最多给多久，可写小数
      说明可省；「弃」档或 x＞0 的题必须写说明：为什么不值、时间该挪到哪
  例：
      7 必 1.5
      23 冲 3 | 要建 B 树，先跳过，做完综合题回来
      41 8/4/3/0 20 | 暴力解写满拿 8；最优解的思想再拿 4
━━━━ 四档的判据 ━━━━
  必＝定义、背过的结论、一步套公式、标准手算，读完讲义就该对；丢了要当天补
  常＝两三步推理或中等计算，按正常节奏能做出来
  冲＝要绕弯、计算量大或考得偏；做对是加分，做错不伤筋骨
  弃＝按分值算时间不划算；先跳过，全卷做完有剩余时间再回来
三条线按预期得分率算，不按全对算：保底＝必×90%；正常＝必×95%＋常×70%；冲刺＝必×100%＋常×90%＋冲×50%。
校验（不过退出码 1）：题号齐全、拆分之和＝满分、总限时不超过整卷时长、弃档必须有说明。
"""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(HERE, 'tier')
PAPERS = os.path.join(ROOT, 'assets', 'exam')
LIMIT = 180
IDX = {'必': 0, '常': 1, '冲': 2, '弃': 3}
# 三条线不按「全对」算（没人能全对）：每条线是各档的预期得分率
RATE = [(0.9, 0, 0), (0.95, 0.7, 0), (1.0, 0.9, 0.5)]


def paper(y):
    s = open(os.path.join(PAPERS, 'y%s.js' % y), encoding='utf-8').read()
    return json.loads(s[s.index(']=') + 2:].rstrip().rstrip(';'))


def main():
    errs, out = [], {}
    for f in sorted(glob.glob(os.path.join(SRC, '*.txt'))):
        y = os.path.basename(f)[:4]
        qs = {q['no']: q for q in paper(y)['q']}
        rec = {'q': {}}
        for i, ln in enumerate(open(f, encoding='utf-8'), 1):
            ln = ln.strip()
            if not ln or ln.startswith('//'): continue
            w = '%s.txt 第 %d 行' % (y, i)
            if ln.startswith('@note'):
                rec['note'] = ln[5:].strip(); continue
            m = re.match(r'(\d+)\s+(\S+)\s+([\d.]+)\s*(?:\|\s*(.*))?$', ln)
            if not m:
                errs.append(w + '：看不懂 ' + ln[:40]); continue
            no, tier, mins, note = int(m.group(1)), m.group(2), float(m.group(3)), (m.group(4) or '').strip()
            if no not in qs:
                errs.append(w + '：卷子里没有第 %d 题' % no); continue
            sc = qs[no]['score']
            if tier in IDX:
                p = [0, 0, 0, 0]; p[IDX[tier]] = sc
            else:
                try: p = [int(x) for x in tier.split('/')]
                except ValueError: p = []
                if len(p) != 4:
                    errs.append(w + '：档要写 必/常/冲/弃 或 a/b/c/x'); continue
                if sum(p) != sc:
                    errs.append(w + '：第 %d 题拆分之和 %d ≠ 满分 %d' % (no, sum(p), sc)); continue
            if p[3] and not note:
                errs.append(w + '：第 %d 题有放弃的分，必须写说明' % no)
            if no in rec['q']: errs.append(w + '：第 %d 题写了两次' % no)
            d = {'m': mins, 'p': p}
            if note: d['n'] = note
            rec['q'][no] = d
        miss = [n for n in qs if n not in rec['q']]
        if miss: errs.append('%s.txt：缺第 %s 题' % (y, '、'.join(map(str, miss))))
        tot = sum(d['m'] for d in rec['q'].values())
        if tot > LIMIT: errs.append('%s.txt：总限时 %.1f 分钟，超过 %d' % (y, tot, LIMIT))
        s = [sum(d['p'][k] for d in rec['q'].values()) for k in range(4)]
        rec['sum'] = s
        rec['line'] = [round(s[0] * RATE[0][0]), round(s[0] * RATE[1][0] + s[1] * RATE[1][1]), round(s[0] * RATE[2][0] + s[1] * RATE[2][1] + s[2] * RATE[2][2])]
        rec['mins'] = round(tot, 1)
        out[int(y)] = rec
        print('%s  必 %d 常 %d 冲 %d 弃 %d ⟹ 保底 %3d · 正常 %3d · 冲刺 %3d   限时合计 %5.1f 分（余 %4.1f 检查）' % (y, s[0], s[1], s[2], s[3], rec['line'][0], rec['line'][1], rec['line'][2], tot, LIMIT - tot))
    if errs:
        print('\n'.join('✗ ' + e for e in errs)); sys.exit(1)
    open(os.path.join(PAPERS, 'tier.js'), 'w', encoding='utf-8').write('window.EXAM_TIER=%s;\n' % json.dumps(out, ensure_ascii=False, separators=(',', ':')))
    print('✓ tier.js：%d 年' % len(out))


if __name__ == '__main__':
    main()
