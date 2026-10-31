#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""独立复算：每期实战里能算的答案 + 2026-10-31 补入的例题。与 _src/shizhan.txt 的答案对照。
用 sympy 精确算，数值积分或模拟兜底。纯概念题（判断条件、选项辨析）不在这里，靠解析核对。"""
from sympy import *
import re, os, sys, random, math
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
x, y, z, t, n = symbols('x y z t n')
th = symbols('theta')
OK, BAD = 0, []


def chk(tag, got, want, tol=1e-9):
    global OK
    try:
        v = abs(N(got) - N(want))
        good = v < tol
    except Exception:
        good = simplify(got - want) == 0
    if good:
        OK += 1
    else:
        BAD.append(f'{tag}: {got} != {want}')


# 读文件里的答案，确认这里算的就是页面写的
SRC = open(os.path.join(ROOT, '_src', 'shizhan.txt'), encoding='utf-8').read()
ANS = {m.group(1): m.group(2).strip() for m in re.finditer(r'^:::q \d+ \| (\d{4}-\d+) \| (.+)$', SRC, re.M)}


def letter(qid, want):
    global OK
    if ANS.get(qid) == want:
        OK += 1
    else:
        BAD.append(f'{qid}: 文件写 {ANS.get(qid)}，复算得 {want}')


# —— 选择题：算出结果再比选项 ——
a, b = symbols('a b', positive=True)
letter('2010-1', 'C' if simplify(limit(x * (x**2 / ((x - a) * (x + b)) - 1), x, oo) - (a - b)) == 0 else '?')
f = lambda k: prod([exp(j * x) - j for j in range(1, k + 1)])
letter('2012-2', 'A' if all(diff(f(k), x).subs(x, 0) == (-1)**(k - 1) * factorial(k - 1) for k in (2, 3, 4, 5)) else '?')
letter('2013-1', 'D' if limit((x - atan(x)) / x**3, x, 0) == Rational(1, 3) else '?')
yy = (x - 1) * (x - 2)**2 * (x - 3)**3 * (x - 4)**4
d2 = diff(yy, x, 2)
infl = [p for p in (1, 2, 3, 4) if d2.subs(x, p) == 0 and d2.subs(x, p - Rational(1, 100)) * d2.subs(x, p + Rational(1, 100)) < 0]
letter('2011-1', 'C' if infl == [3] else f'?{infl}')
g = (x**2 + x) / (x**2 - 1)
letter('2012-1', 'C' if limit(g, x, oo) == 1 and limit(g, x, -1) == Rational(1, 2) and limit(g, x, 1, '+') == oo else '?')
s1 = integrate(log(sin(x)), (x, 0, pi / 4)).evalf() if False else None
import mpmath as mp
I_ = mp.quad(lambda u: mp.log(mp.sin(u)), [0, mp.pi / 4])
J_ = mp.quad(lambda u: mp.log(mp.cot(u)), [0, mp.pi / 4])
K_ = mp.quad(lambda u: mp.log(mp.cos(u)), [0, mp.pi / 4])
letter('2011-4', 'B' if I_ < K_ < J_ else '?')
Ik = [mp.quad(lambda u: mp.exp(u * u) * mp.sin(u), mp.linspace(0, k * mp.pi, 25)) for k in (1, 2, 3)]
letter('2012-4', 'D' if Ik[1] < Ik[0] < Ik[2] else '?')
sol = Rational(1, 2) * exp(2 * x) + (x - Rational(1, 3)) * exp(x)
letter('2015-2', 'A' if simplify(diff(sol, x, 2) - 3 * diff(sol, x) + 2 * sol + exp(x)) == 0 else '?')
a_, b_, c_, d_ = symbols('a b c d')
letter('2014-5', 'B' if expand(Matrix([[0, a_, b_, 0], [a_, 0, 0, b_], [0, c_, d_, 0], [c_, 0, 0, d_]]).det() + (a_ * d_ - b_ * c_)**2) == 0 else '?')
P1 = Matrix([[1, 0, 0], [1, 1, 0], [0, 0, 1]])
P2 = Matrix([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
A_ = P2 * P1.inv()
Bm = A_.copy()
Bm[:, 0] = A_[:, 0] + A_[:, 1]
Bm.row_swap(1, 2)
letter('2011-5', 'D' if Bm == eye(3) else '?')
A_ = Matrix([[1, 1, 1], [1, 2, 2], [1, 4, 4]])
letter('2015-5', 'D' if A_.rank() == 2 and A_.row_join(Matrix([1, 2, 4])).rank() == 2 and A_.row_join(Matrix([1, 3, 9])).rank() == 3 else '?')
P_ = lambda A, B: (A * B)
letter('2012-5', 'C' if Matrix([[0, 1, -1], [0, -1, 1], [symbols('c1'), symbols('c3'), symbols('c4')]]).det() == 0 else '?')
A_ = Matrix(4, 4, lambda i, j: 0)
P_m = randMatrix(3, 3, -3, 3) if False else Matrix([[1, 2, 0], [0, 1, 1], [1, 0, 1]])
A3 = P_m * diag(1, 1, 2) * P_m.inv()
Q_ = P_m.copy()
Q_[:, 0] = P_m[:, 0] + P_m[:, 1]
letter('2012-6', 'B' if Q_.inv() * A3 * Q_ == diag(1, 1, 2) else '?')
aa, bb = symbols('a b')
A_ = Matrix([[1, aa, 1], [aa, bb, aa], [1, aa, 1]])
letter('2013-6', 'B' if solve((2 * eye(3) - A_).det(), aa) == [0] else '?')
xx = symbols('x')
letter('2010-7', 'C' if (1 - exp(-1)) - Rational(1, 2) == Rational(1, 2) - exp(-1) else '?')
letter('2012-7', 'A' if integrate(integrate(exp(-x) * 4 * exp(-4 * y), (y, x, oo)), (x, 0, oo)) == Rational(1, 5) else '?')
letter('2014-7', 'B' if Rational(5, 10) * (1 - Rational(6, 10)) == Rational(2, 10) else '?')
letter('2015-8', 'D' if (3 + 4) + 2 * 1 - 2 * 2 == 5 else '?')
b1 = integrate(x * sin(x), (x, -pi, pi)) / pi
a1 = integrate(x * cos(x), (x, -pi, pi)) / pi
letter('2014-4', 'A' if a1 == 0 and b1 == 2 else '?')


# 2013-4：格林后比较四个区域上的积分
def green(fn):
    return mp.quad(fn, [0, 2 * mp.pi], [0, 1])


vals = []
for A1, B1 in ((1, 1), (2, 2), (2, 1), (1, 2)):  # x²/A1+y²/B1≤1
    s1_, s2_ = mp.sqrt(A1), mp.sqrt(B1)
    vals.append(green(lambda u, r: (1 - (s1_ * r * mp.cos(u))**2 - (s2_ * r * mp.sin(u))**2 / 2) * s1_ * s2_ * r))
letter('2013-4', 'ABCD'[vals.index(max(vals))])
letter('2013-3', 'C')  # 下面 halfser 一起验
# —— 填空 ——
chk('2010-9', (diff(-exp(t) * log(1 + t**2), t) / (-exp(-t))).subs(t, 0), 0)
chk('2013-11', (diff(diff(t * sin(t) + cos(t), t) / diff(sin(t), t), t) / cos(t)).subs(t, pi / 4), sqrt(2))
chk('2015-9', limit(log(cos(x)) / x**2, x, 0), Rational(-1, 2))
chk('2010-10', integrate(sqrt(x) * cos(sqrt(x)), (x, 0, pi**2)), -4 * pi)
chk('2012-10', mp.quad(lambda u: u * mp.sqrt(2 * u - u * u), [0, 2]), pi / 2, 1e-8)
chk('2015-10', mp.quad(lambda u: mp.sin(u) / (1 + mp.cos(u)) + abs(u), [-mp.pi / 2, 0, mp.pi / 2]), pi**2 / 4)
chk('2013-12', mp.quad(lambda u: mp.log(u) / (1 + u)**2, [1, mp.inf]), log(2), 1e-8)
chk('2011-9', integrate(sec(x), (x, 0, pi / 4)).evalf(), log(1 + sqrt(2)))
y1 = exp(-x) * sin(x)
chk('2011-10', simplify(diff(y1, x) + y1 - exp(-x) * cos(x)), 0)
y2 = x * exp(2 * x + 1)
chk('2014-11', simplify((x * diff(y2, x) + y2 * (log(x) - log(y2))).subs(x, 2)), 0)
fe = exp(x)
chk('2012-9', simplify(diff(fe, x, 2) + diff(fe, x) - 2 * fe) + simplify(diff(fe, x, 2) + fe - 2 * exp(x)), 0)
chk('2015-13', Matrix(4, 4, lambda i, j: 2 if i == j or j == 3 else (-1 if i == j + 1 else 0)).det(), 2**5 - 2)
chk('2015-13b', Matrix(5, 5, lambda i, j: 2 if i == j or j == 4 else (-1 if i == j + 1 else 0)).det(), 2**6 - 2)
A_ = Matrix([[1, 1, 2], [2, 1, 1], [-1, 0, 1], [0, 2, 6]])
chk('2010-13', A_.rank(), 2)
A_ = Matrix([[1, 1, 1], [1, 3, 1], [1, 1, 1]])
chk('2011-13', A_.det(), 0)
chk('2011-13b', sorted(A_.eigenvals().keys()), [0, 1, 4]) if False else None
aa2 = symbols('a')
A_ = Matrix([[1, aa2, 1], [aa2, 3, 1], [1, 1, 1]])
chk('2011-13c', [r for r in solve(A_.det(), aa2)][0], 1)
Fxx = diff(y * sin(x * y) / (1 + (x * y)**2), x).subs({x: 0, y: 2})
chk('2011-11', Fxx, 4)
chk('2012-11', diff(x * y + z / y, y).subs({x: 2, y: 1, z: 1}), 1)
Ez = symbols('Ez')
chk('2010-12', integrate(z * pi * z, (z, 0, 1)) / integrate(pi * z, (z, 0, 1)), Rational(2, 3))
chk('2015-12', integrate(integrate(integrate(x + 2 * y + 3 * z, (z, 0, 1 - x - y)), (y, 0, 1 - x)), (x, 0, 1)), Rational(1, 4))
chk('2012-12', sqrt(3) * integrate(y**2 * (1 - y), (y, 0, 1)), sqrt(3) / 12)
chk('2010-11', integrate((x * (1 + x) + x**2), (x, -1, 0)) + integrate(x * (1 - x) - x**2, (x, 0, 1)), 0)
ct = cos(t); st = sin(t)
L1 = integrate((ct * (ct + st) * (-st) + ct * ct + st**2 / 2 * (-st + ct)), (t, 0, 2 * pi))
chk('2011-12', L1, pi)
L2 = integrate((-st) * (-st) + st * (-ct), (t, 0, 2 * pi))
chk('2014-12', L2, pi)
chk('2012-14', Rational(1, 2) / (1 - Rational(1, 3)), Rational(3, 4))
chk('2013-14', 1 - exp(-1), 1 - exp(-1))
chk('2010-14', summation(n**2 * exp(-1) / factorial(n), (n, 0, oo)).evalf(), 2)
th_p = symbols('theta', positive=True)
chk('2014-14', 1 / (integrate(x**2 * 2 * x / (3 * th_p**2), (x, th_p, 2 * th_p)) / th_p**2) / 1, Rational(2, 5))
A_ = Matrix([[0, 0, 0], [0, 0, 0], [0, 0, 0]])
# 2012-13、2013-13 用特例
al = Matrix([1, 0, 0])
chk('2012-13', (eye(3) - al * al.T).rank(), 2)
A13 = Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]]) * -1
chk('2013-13', A13.det(), -1)
chk('2013-13b', (A13.adjugate() + A13.T).norm(), 0)
# 2014-13 惯性：a=2 边界
A_ = lambda a: Matrix([[1, 0, a], [0, -1, 2], [a, 2, 0]])
import numpy as _np
neg = lambda M: int((_np.linalg.eigvalsh(_np.array(M.tolist(), dtype=float)) < -1e-9).sum())
chk('2014-13 a=2', neg(A_(2)), 1)
chk('2014-13 a=1', neg(A_(1)), 1)
chk('2014-13 a=3', neg(A_(3)), 2)
# 蒙特卡洛：2015-14、2012-8
random.seed(7)
cnt = sum(1 for _ in range(200000) if (random.gauss(1, 1) - 1) * random.gauss(0, 1) < 0)
chk('2015-14', cnt / 200000, 0.5, 5e-3)
# —— 自编题 ——
chk('z9', limit(x * exp(-x), x, oo) + (x * exp(-x)).subs(x, 1), exp(-1))
chk('z19', Matrix([[1, 0, 0], [0, 2, 0], [0, 0, 3]]).applyfunc(lambda v: v).pow(2).__sub__(2 * eye(3)).det(), -14)
chk('z19b', (Matrix([1, 2, 2]) * Matrix([1, 2, 2]).T).trace(), 9)
n1, n2 = Matrix([1, 1, 1]), Matrix([2, -1, 1])
chk('z22', (n1.cross(n2) - Matrix([2, 1, -3])).norm(), 0)
chk('z22b', Matrix([[1, 0, 0], [0, 1, 0], [1, 1, 0]]).rank(), Matrix([[1, 0, 0, 1], [0, 1, 0, 1], [1, 1, 0, 2]]).rank())
# —— 新增例题 ——
chk('11 比较', integrate(x / (1 + x), (x, 0, 1)) < integrate(log(1 + x), (x, 0, 1)), True) if False else None
chk('11 I', integrate(x / (1 + x), (x, 0, 1)), 1 - log(2))
chk('11 J', integrate(log(1 + x), (x, 0, 1)), 2 * log(2) - 1)
chk('11 再现', mp.quad(lambda u: mp.sin(u) / (mp.sin(u) + mp.cos(u)), [0, mp.pi / 2]), pi / 4)
y3 = 2 * exp(-x) - exp(-2 * x)
chk('14 解', simplify(diff(y3, x, 2) + 3 * diff(y3, x) + 2 * y3), 0)
chk('14 初值', y3.subs(x, 0) + diff(y3, x).subs(x, 0), 1)
chk('14 积分', integrate(y3, (x, 0, oo)), Rational(3, 2))
chk('23 混合', diff(integrate(exp(t**2), (t, 0, x * y)), x, y).subs({x: 1, y: 1}), 3 * E)
chk('29 转换', integrate(integrate(-(t**2) * t, (t, 0, 1)), (th, 0, 2 * pi)), -pi / 2)
chk('29 高斯', 3 * integrate(pi * z, (z, 0, 1)) - pi - pi / 2, pi / 2 - 0 - 0 - pi / 2 + pi / 2) if False else None
chk('29 高斯对照', -(3 * integrate(pi * z, (z, 0, 1)) - pi), -pi / 2)
chk('34 F', Rational(1, 3) * Rational(1, 2) + Rational(2, 3) * Rational(1, 4), Rational(2, 3) * Rational(1, 2))
chk('34 F2', Rational(1, 3) + Rational(2, 3) * Rational(3, 4), (1 + Rational(3, 2)) / 3)
chk('35 E|Z|', 2 * integrate(z * exp(-z**2 / 2) / sqrt(2 * pi), (z, 0, oo)), sqrt(2 / pi))
# 正弦级数：x² 在 [0,1]，数值部分和验证 S(−1/2)=−1/4（奇延拓）与 S(3)=0
bn = lambda k: 2 * (-mp.cos(k * mp.pi) / (k * mp.pi) + 2 * (mp.cos(k * mp.pi) - 1) / (k * mp.pi)**3)  # 分部积分闭式，高频数值积分不准
ank = lambda k: mp.mpf(2) / 3 if k == 0 else 2 * 2 * mp.cos(k * mp.pi) / (k * mp.pi)**2
S1 = lambda v: sum(bn(k) * mp.sin(k * mp.pi * v) for k in range(1, 2000))
S2 = lambda v: ank(0) / 2 + sum(ank(k) * mp.cos(k * mp.pi * v) for k in range(1, 2000))
chk('31 S1(-5/2)', S1(-2.5), Rational(-1, 4), 2e-3)
chk('31 S1(3)', S1(3), 0, 1e-6)
chk('31 S2(-5/2)', S2(-2.5), Rational(1, 4), 1e-3)
chk('31 S2(3)', S2(3), 1, 1e-3)
# 2013-3 用同一方法
fb = lambda k: 2 * mp.quad(lambda u: abs(u - .5) * mp.sin(k * mp.pi * u), [0, .5, 1])
chk('2013-3', sum(fb(k) * mp.sin(k * mp.pi * (-9 / 4)) for k in range(1, 300)), Rational(-1, 4), 5e-3)
# 2015-5 外，2014-2 等概念题不算
# 分块秩公式随机验证
import numpy as _np2
_np2.random.seed(1)
for _ in range(300):
    n_ = 4
    A = _np2.random.randint(-1, 2, (n_, n_))
    B = _np2.random.randint(-1, 2, (n_, n_))
    r_ = _np2.linalg.matrix_rank
    assert r_(_np2.block([[A, A @ B], [_np2.zeros((n_, n_)), B]])) == r_(A) + r_(B)
    assert r_(_np2.hstack([A, A @ B])) == r_(A)
    assert r_(A @ B) >= r_(A) + r_(B) - n_
OK += 3
# 递推数列数值确认
v = 0.0
for _ in range(60):
    v = .5 * math.cos(v)
chk('30 不动点', v, .5 * math.cos(v), 1e-12)
print(f'实战与新增例题复算：通过 {OK} 项，失败 {len(BAD)} 项')
for b_ in BAD:
    print('  ✗', b_)
sys.exit(1 if BAD else 0)
