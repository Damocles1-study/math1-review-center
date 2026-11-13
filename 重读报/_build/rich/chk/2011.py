#!/usr/bin/env python3
# 2011 数学一 · 逐题独立复算（sympy / 数值）。跑通即全部 OK。
import sympy as sp, random, math, itertools
from sympy import symbols, Rational as R, pi, sqrt, exp, log, sin, cos, tan, cot, atan, oo, Matrix, integrate, diff, simplify, limit, eye
x, y, z, t, a, k = symbols('x y z t a k', real=True)
ok = []
def chk(no, cond, msg=''):
    assert bool(cond), '第 %s 题失配 %s' % (no, msg)
    ok.append(no)
N = lambda e: float(sp.N(e, 20))

# 1 拐点
f = (x - 1) * (x - 2)**2 * (x - 3)**3 * (x - 4)**4
f2 = sp.factor(diff(f, x, 2))
chk(1, f2.subs(x, 3) == 0 and f2.subs(x, 3 - R(1, 100)) < 0 and f2.subs(x, 3 + R(1, 100)) > 0)
chk(1, f2.subs(x, 2) == -32 and f2.subs(x, 1) == 6264 and f2.subs(x, 4) == 0 and f2.subs(x, 4 - R(1, 100)) > 0 and f2.subs(x, 4 + R(1, 100)) > 0)
g3 = (x - 1) * (x - 2)**2 * (x - 4)**4
chk(1, g3.subs(x, 3) == 2 and (12 * (x - 1) * (x - 2)**2 * (x - 3)**3).subs(x, 4) == 144)
f1 = diff(f, x); rts = sp.real_roots(sp.Poly(f1, x))
ext = sorted(set(r for r in rts if (f1.subs(x, N(r) - 1e-4) * f1.subs(x, N(r) + 1e-4)) < 0), key=N)
chk('1v', len(ext) == 5, ext)
u = symbols('u', real=True)
chk('1v2', sp.solve(diff((u**2 - 1)**2, u, 2), u) == [-sqrt(3) / 3, sqrt(3) / 3])
# 2 收敛域：a_n = 1/n
n = symbols('n', integer=True, positive=True)
chk(2, sp.Sum((-1)**n / n, (n, 1, oo)).is_convergent() and not sp.Sum(1 / n, (n, 1, oo)).is_convergent())
# 3 二元极值：取 f = c + d x^2/2 型，核对 A,B,C
c0, d0 = symbols('c0 d0', positive=True)
F = sp.Function('F')
zz = F(x) * log(F(y))
sub = {diff(F(x), x): 0, diff(F(y), y): 0}
def at0(e):
    e = e.subs({sp.Derivative(F(x), (x, 2)): symbols('f2'), sp.Derivative(F(y), (y, 2)): symbols('f2')})
    e = e.subs({sp.Derivative(F(x), x): 0, sp.Derivative(F(y), y): 0}).subs({F(x): symbols('f0'), F(y): symbols('f0')})
    return simplify(e)
A_, B_, C_ = at0(diff(zz, x, 2)), at0(diff(zz, x, y)), at0(diff(zz, y, 2))
f0s, f2s = symbols('f0 f2')
chk(3, simplify(A_ - f2s * log(f0s)) == 0 and B_ == 0 and simplify(C_ - f2s) == 0)
# 3v: z=f(x)f(y)
zz2 = F(x) * F(y)
chk('3v', simplify(at0(diff(zz2, x, 2)) - f2s * f0s) == 0 and at0(diff(zz2, x, y)) == 0)
# 4 积分比大小
I = N(sp.Integral(log(sin(x)), (x, 0, pi / 4))); J = N(sp.Integral(log(cot(x)), (x, 0, pi / 4))); K = N(sp.Integral(log(cos(x)), (x, 0, pi / 4)))
chk(4, I < K < J and abs(J - (K - I)) < 1e-9, (I, J, K))
chk('4v', N(sp.Integral(exp(-cot(x)), (x, 0, pi / 4))) < N(sp.Integral(exp(-cos(x)), (x, 0, pi / 4))) < N(sp.Integral(exp(-sin(x)), (x, 0, pi / 4))))
chk('4v2', abs(I + K + math.pi / 2 * math.log(2)) < 1e-9)
# 5 初等矩阵
P1 = Matrix([[1, 0, 0], [1, 1, 0], [0, 0, 1]]); P2 = Matrix([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
A = P2 * P1.inv(); B = A.copy(); B[:, 0] = B[:, 0] + B[:, 1]
chk(5, B == A * P1 and P2 * B == eye(3) and A == Matrix([[1, 0, 0], [0, 0, 1], [-1, 1, 0]]) and A.inv() == P1 * P2)
A5 = P1.T.inv() * P2; B5 = A5.copy(); B5[0, :] = B5[0, :] + B5[1, :]; B5c = B5.copy(); B5c[:, 1], B5c[:, 2] = B5[:, 2], B5[:, 1]
chk('5v', B5c == eye(3) and A.det() == -1)
# 6 伴随：随机构造 α1=-α3、秩 3 的 4 阶矩阵
random.seed(1)
for _ in range(20):
    a2, a3, a4 = [Matrix([random.randint(-3, 3) for _ in range(4)]) for _ in range(3)]
    M = Matrix.hstack(-a3, a2, a3, a4)
    if M.rank() != 3: continue
    As = M.adjugate()
    chk(6, As.rank() == 1 and As * M == sp.zeros(4) and Matrix.hstack(a2, a3, a4).rank() == 3 and Matrix.hstack(-a3, a2, a3).rank() == 2)
M = Matrix([[1, -1, 0, 0], [0, 0, 1, -1], [1, -1, 1, -1], [2, -2, 0, 0]])
chk('6v', M.rank() == 2 and M.adjugate() == sp.zeros(4))
# 7 密度
xp = symbols('xp', positive=True)
g1, g2, G1, G2 = exp(-xp), 2 * exp(-2 * xp), 1 - exp(-xp), 1 - exp(-2 * xp)
chk(7, integrate(g1 * g2, (xp, 0, oo)) == R(2, 3) and integrate(2 * g2 * G1, (xp, 0, oo)) == R(2, 3) and integrate(g1 * G2, (xp, 0, oo)) == R(2, 3) and integrate(g1 * G2 + g2 * G1, (xp, 0, oo)) == 1)
chk('7v', integrate(2 * g1 * G1, (xp, 0, oo)) == 1 and integrate(g1 * (1 - G2) + g2 * (1 - G1), (xp, 0, oo)) == 1)
# 8 U(0,1) 例
chk(8, integrate(integrate(x * y, (x, 0, 1)), (y, 0, 1)) == R(1, 4) and 2 * integrate(integrate(x, (y, 0, x)), (x, 0, 1)) == R(2, 3) and 2 * integrate(integrate(y, (y, 0, x)), (x, 0, 1)) == R(1, 3))
# 9 弧长
chk(9, simplify(integrate(1 / cos(x), (x, 0, pi / 4)) - log(1 + sqrt(2))) == 0 or abs(N(sp.Integral(1 / cos(x), (x, 0, pi / 4))) - math.log(1 + math.sqrt(2))) < 1e-12)
chk('9v', abs(N(sp.Integral(sqrt(1 + sin(x)), (x, 0, pi))) - 4) < 1e-10 and abs(N(sp.Integral(sqrt((1 + cos(x))**2 + sin(x)**2), (x, 0, pi))) - 4) < 1e-10)
chk('9n', abs(math.hypot(math.pi / 4, 0.5 * math.log(2)) - 0.86) < 0.005)
# 10 微分方程
Y = sp.Function('Y')
sol = sp.dsolve(Y(x).diff(x) + Y(x) - exp(-x) * cos(x), Y(x), ics={Y(0): 0}).rhs
chk(10, simplify(sol - exp(-x) * sin(x)) == 0)
s1 = exp(x) / 5 * (2 * cos(x) + sin(x)) - R(2, 5) * exp(-x)
chk('10v', simplify(diff(s1, x) + s1 - exp(x) * cos(x)) == 0 and s1.subs(x, 0) == 0)
s2 = x * cos(x)
chk('10v2', simplify(diff(s2, x) + s2 * tan(x) - cos(x)) == 0)
# 11
Fx = y * sin(x * y) / (1 + x**2 * y**2)
chk(11, diff(Fx, x).subs({x: 0, y: 2}) == 4 and simplify(diff(Fx, x).subs(x, 0) - y**2) == 0 and diff(Fx, y).subs({x: 0, y: 2}) == 0)
chk('11v', limit(integrate(Fx.subs(y, 2), (x, 0, t)).doit() / t**2 if False else sp.series(Fx.subs(y, 2), x, 0, 2).removeO() / (2 * x), x, 0) == 2)
# 12 曲线积分
xx, yy, zc = cos(t), sin(t), cos(t) + sin(t)
integrand = xx * zc * diff(xx, t) + xx * diff(yy, t) + yy**2 / 2 * diff(zc, t)
chk(12, integrate(integrand, (t, 0, 2 * pi)) == pi)
chk('12v', integrate(yy * diff(xx, t) + zc * diff(yy, t) + xx * diff(zc, t), (t, 0, 2 * pi)) == pi and integrate(xx * diff(xx, t) + xx * diff(yy, t), (t, 0, 2 * pi)) == pi)
# 13
A13 = Matrix([[1, a, 1], [a, 3, 1], [1, 1, 1]])
chk(13, sp.factor(A13.det()) == -(a - 1)**2 and sorted(A13.subs(a, 1).eigenvals().keys()) == [0, 1, 4] and A13.subs(a, -1).det() == -4)
chk(13, sp.expand(sum(A13.extract(list(c), list(c)).det() for c in itertools.combinations(range(3), 2))) == 5 - a**2)
# 14
mu, sg, rho = symbols('mu sigma rho', positive=True); uu, ww = symbols('uu ww', real=True)
def Enorm(e):
    """E[多项式(uu, ww)]，uu、ww 独立标准正态：逐项换成正态矩"""
    mom = lambda m: 0 if m % 2 else sp.factorial2(m - 1) if m else 1
    P = sp.Poly(sp.expand(e), uu, ww)
    return sp.expand(sum(c * mom(i) * mom(j) for (i, j), c in P.terms()))
def XY(r):
    return mu + sg * uu, mu + sg * (r * uu + sqrt(1 - r**2) * ww)   # Corr = r
X14, Y14 = XY(0)
chk(14, sp.expand(Enorm(X14 * Y14**2) - mu * (mu**2 + sg**2)) == 0)
chk('14v', sp.expand(Enorm(X14**2 * Y14**2) - mu**4 - (sg**4 + 2 * mu**2 * sg**2)) == 0)
X14r, Y14r = XY(rho)
chk('14v2', simplify(Enorm(X14r * Y14r) - mu**2 - rho * sg**2) == 0 and simplify(Enorm(X14r * Y14r**2) - (mu**3 + mu * sg**2 + 2 * rho * mu * sg**2)) == 0)
# 15 极限
e15 = (log(1 + x) / x) ** (1 / (exp(x) - 1))
chk(15, limit(e15, x, 0) == exp(-R(1, 2)) and limit((log(1 + x) - x) / x**2, x, 0) == -R(1, 2))
chk('15v', limit((sin(x) / x) ** (1 / (1 - cos(x))), x, 0) == exp(-R(1, 3)))
chk('15v2', limit((log(1 + x) - x) / x**3, x, 0, '+') == -oo and limit((log(1 + x) - x) / x**3, x, 0, '-') == oo)
chk('15v3', limit((tan(x) / x) ** (1 / x**2), x, 0, '+') == exp(R(1, 3)))
# 16 抽象复合：取具体 f、g 核对公式
uu_, vv_ = symbols('u_ v_')
for fexpr, gexpr in [(uu_**3 * vv_**2 + sin(uu_ * vv_) + uu_ * exp(vv_), 1 + (x - 1)**2 * (x + 2)), (exp(uu_ + 2 * vv_) * uu_**2 + vv_**3, 1 - 3 * (x - 1)**2 + (x - 1)**3)]:
    assert gexpr.subs(x, 1) == 1 and diff(gexpr, x).subs(x, 1) == 0
    zz16 = fexpr.subs({uu_: x * y, vv_: y * gexpr}, simultaneous=True)
    at = lambda e: e.subs({uu_: 1, vv_: 1})
    f1, f11, f12, f22, f2 = diff(fexpr, uu_), diff(fexpr, uu_, 2), diff(fexpr, uu_, vv_), diff(fexpr, vv_, 2), diff(fexpr, vv_)
    chk(16, simplify(diff(zz16, x, y).subs({x: 1, y: 1}) - at(f1 + f11 + f12)) == 0)
    chk('16v3', simplify(diff(zz16, y, 2).subs({x: 1, y: 1}) - at(f11 + 2 * f12 + f22)) == 0)
    chk('16v1', simplify(diff(zz16, x, 2).subs({x: 1, y: 1}) - at(f11) - diff(gexpr, x, 2).subs(x, 1) * at(f2)) == 0)
fexpr = uu_**3 * vv_**2 + sin(uu_ * vv_) + uu_ * exp(vv_); gexpr = 1 + 2 * (x - 1) + (x - 1)**2
zz16 = fexpr.subs({uu_: x * y, vv_: y * gexpr}, simultaneous=True)
f1, f11, f12, f22, f2 = diff(fexpr, uu_), diff(fexpr, uu_, 2), diff(fexpr, uu_, vv_), diff(fexpr, vv_, 2), diff(fexpr, vv_)
chk('16v2', simplify(diff(zz16, x, y).subs({x: 1, y: 1}) - (f1 + 2 * f2 + f11 + 3 * f12 + 2 * f22).subs({uu_: 1, vv_: 1})) == 0)
# 17 数根（数值）
def nroots(fn, lo=-200.0, hi=200.0, m=400001):
    import numpy as np
    xs = np.linspace(lo, hi, m); ys = fn(xs)
    sg = np.sign(ys); nz = sg[sg != 0]
    return int((nz[1:] * nz[:-1] < 0).sum())
import numpy as np
for kk, want in [(-2, 1), (0, 1), (0.5, 1), (1, 1), (1.01, 3), (2, 3), (10, 3), (60, 3)]:
    chk(17, nroots(lambda v: kk * np.arctan(v) - v) == want, kk)
chk(17, abs(2 * math.atan(2.3311) - 2.3311) < 1e-3)
for kk, want in [(-1, 1), (0, 1), (0.3, 3), (0.9, 3), (1, 1), (2, 1)]:
    chk('17v', nroots(lambda v: np.arctan(v) - kk * v, -2000, 2000, 2000001) == want, kk)
for kk, want in [(-1, 1), (0, 1), (0.2, 2), (0.5, 0)]:
    chk('17v2', nroots(lambda v: np.log(v) - kk * v, 1e-6, 400, 4000001) == want, kk)
for kk in (1.5, 3, 20):
    r = float(sp.nsolve(kk * atan(x) - x, x, kk * 1.5)); chk('17v3', math.sqrt(kk - 1) < r < kk * math.pi / 2)
# 18
an = lambda m: sum(1.0 / i for i in range(1, m + 1)) - math.log(m)
chk(18, all(1 / (m + 1) < math.log(1 + 1 / m) < 1 / m for m in range(1, 3000)) and all(an(m + 1) < an(m) and an(m) > 0 for m in range(1, 400)) and abs(an(200000) - 0.5772157) < 1e-5)
chk('18v', all(math.log(1 + m) < sum(1.0 / i for i in range(1, m + 1)) < 1 + math.log(m) for m in range(2, 300)) and abs(sum(1.0 / i for i in range(100001, 200001)) - math.log(2)) < 1e-5)
bn = lambda m: sum(1.0 / i for i in range(1, m + 1)) - math.log(m + 1)
chk('18v3', all(bn(m + 1) > bn(m) and bn(m) < 1 for m in range(1, 400)))
# 19 取具体 f 验证
for f19 in [(1 - x) * (1 - y) * (x**2 + 3 * y + 1), (1 - x) * (1 - y) * exp(x * y), (x - 1)**2 * (y - 1) * cos(x + y)]:
    assert f19.subs(x, 1) == 0 and f19.subs(y, 1) == 0
    dbl = lambda e: integrate(integrate(e, (x, 0, 1)), (y, 0, 1))
    aa = dbl(f19)
    chk(19, simplify(dbl(x * y * diff(f19, x, y)) - aa) == 0)
    chk('19v', simplify(dbl(x * diff(f19, x)) + aa) == 0 and simplify(dbl(diff(f19, x, y)) - f19.subs({x: 0, y: 0})) == 0)
f19 = (1 - x) * (y**2 + 2 + x * y)
chk('19v3', simplify(integrate(integrate(x * y * diff(f19, x, y), (x, 0, 1)), (y, 0, 1)) - (integrate(integrate(f19, (x, 0, 1)), (y, 0, 1)) - integrate(f19.subs(y, 1), (x, 0, 1)))) == 0)
# 20
al = [Matrix([1, 0, 1]), Matrix([0, 1, 1]), Matrix([1, 3, 5])]; be = [Matrix([1, 1, 1]), Matrix([1, 2, 3]), Matrix([3, 4, a])]
MA, MB = Matrix.hstack(*al), Matrix.hstack(*be)
chk(20, MA.det() == 1 and sp.expand(MB.det()) == a - 5)
MB5 = MB.subs(a, 5); Cc = MA.inv() * MB5
chk(20, Cc == Matrix([[2, 1, 5], [4, 2, 10], [-1, 0, -2]]) and MB5.rank() == 2)
B2 = MB5[:, :2]
chk('20v', [Matrix.hstack(B2, v).rank() == 2 for v in al] == [False, False, True] and -be[0] + 2 * be[1] == al[2] and 2 * be[0] + be[1] == be[2].subs(a, 5))
# 21
A21 = Matrix([[0, 0, 1], [0, 0, 0], [1, 0, 0]])
chk(21, A21 * Matrix([[1, 1], [0, 0], [-1, 1]]) == Matrix([[-1, 1], [0, 0], [1, 1]]) and A21.rank() == 2 and A21.T == A21 and A21.eigenvals() == {-1: 1, 1: 1, 0: 1} and A21 * Matrix([0, 1, 0]) == sp.zeros(3, 1))
q1, q2 = Matrix([1, 0, -1]) / sqrt(2), Matrix([1, 0, 1]) / sqrt(2)
chk(21, -q1 * q1.T + q2 * q2.T == A21)
Pn = Matrix([[1, 1, 1], [0, 0, 1], [-1, 1, 0]]); An = Pn * sp.diag(-1, 1, 0) * Pn.inv()
chk('21v', An != A21 and An.rank() == 2 and An * Matrix([[1, 1], [0, 0], [-1, 1]]) == Matrix([[-1, 1], [0, 0], [1, 1]]))
chk('21v2', (-q1 * q1.T + q2 * q2.T + 3 * Matrix([0, 1, 0]) * Matrix([[0, 1, 0]])) == Matrix([[0, 0, 1], [0, 3, 0], [1, 0, 0]]) and A21**2011 == A21 and A21**2 == sp.diag(1, 0, 1))
# 22
T = {(0, -1): 0, (0, 0): R(1, 3), (0, 1): 0, (1, -1): R(1, 3), (1, 0): 0, (1, 1): R(1, 3)}
E = lambda g: sum(p * g(i, j) for (i, j), p in T.items())
chk(22, sum(T.values()) == 1 and sum(p for (i, j), p in T.items() if i * i == j * j) == 1 and sum(p for (i, j), p in T.items() if i == 1) == R(2, 3) and all(sum(p for (i, j), p in T.items() if j == c) == R(1, 3) for c in (-1, 0, 1)))
chk(22, [sum(p for (i, j), p in T.items() if i * j == v) for v in (-1, 0, 1)] == [R(1, 3)] * 3 and E(lambda i, j: i * j) - E(lambda i, j: i) * E(lambda i, j: j) == 0)
chk('22v', E(lambda i, j: (i + j)**2) - E(lambda i, j: i + j)**2 == R(8, 9) and E(lambda i, j: i * i) - R(4, 9) == R(2, 9) and E(lambda i, j: j * j) == R(2, 3))
tt = R(1, 7); T2 = {(0, -1): 0, (1, -1): R(1, 3), (0, 0): tt, (1, 1): tt, (0, 1): R(1, 3) - tt, (1, 0): R(1, 3) - tt}
chk('22v2', sum(p for (i, j), p in T2.items() if i == 0) == R(1, 3) and all(sum(p for (i, j), p in T2.items() if j == c) == R(1, 3) for c in (-1, 0, 1)) and sum(p for (i, j), p in T2.items() if i + j >= 0) == 1)
# 23
th = symbols('theta', positive=True); Ss, m = symbols('Ss m', positive=True)
lnL = -m / 2 * log(2 * pi) - m / 2 * log(th) - Ss / (2 * th)
chk(23, sp.solve(diff(lnL, th), th) == [Ss / m])
w = symbols('w', positive=True); nn = symbols('nn', positive=True)
chi = w**(nn / 2 - 1) * exp(-w / 2) / (2**(nn / 2) * sp.gamma(nn / 2))
EW = simplify(integrate(w * chi, (w, 0, oo))); EW2 = simplify(integrate(w**2 * chi, (w, 0, oo)))
chk(23, simplify(EW - nn) == 0 and simplify(EW2 - EW**2 - 2 * nn) == 0)
random.seed(7); nS, sig = 6, 1.7; vals = []
for _ in range(120000):
    vals.append(sum(random.gauss(3.0, sig)**2 - 6 * random.gauss(0, 0) for _ in range(0)) if False else sum((random.gauss(3.0, sig) - 3.0)**2 for _ in range(nS)) / nS)
mean = sum(vals) / len(vals); var = sum((v - mean)**2 for v in vals) / len(vals)
chk(23, abs(mean - sig**2) < 0.03 and abs(var - 2 * sig**4 / nS) / (2 * sig**4 / nS) < 0.04, (mean, var))
print('2011 复算全部通过：', len(ok), '项')
