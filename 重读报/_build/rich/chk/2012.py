#!/usr/bin/env python3
# 2012 数学一 · 逐题独立复算（sympy / 数值）。跑通即全部 OK。
import sympy as sp, random, math
from sympy import symbols, Rational as R, pi, sqrt, exp, log, sin, cos, oo, Matrix, integrate, diff, simplify, limit
x, y, z, t, a, n = symbols('x y z t a n', real=True)
ok = []
def chk(no, cond, msg=''):
    assert bool(cond), '第 %s 题失配 %s' % (no, msg)
    ok.append(no)

# 1 渐近线
f = (x**2 + x) / (x**2 - 1)
chk(1, limit(f, x, oo) == 1 and limit(f, x, -oo) == 1 and limit(f, x, -1) == R(1, 2) and abs(limit(f, x, 1, '+')) == oo)
g = (x**2 + x) / (x - 1)
chk('1v', limit(g / x, x, oo) == 1 and limit(g - x, x, oo) == 2)
chk('1v2', limit(f * exp(1 / x), x, 0, '+') == -oo and limit(f * exp(1 / x), x, oo) == 1)
# 2 f'(0)
for N in range(1, 7):
    F = sp.prod([exp(k * x) - k for k in range(1, N + 1)])
    chk(2, diff(F, x).subs(x, 0) == (-1) ** (N - 1) * sp.factorial(N - 1))
F = (exp(x) - 1) ** 2 * (exp(2 * x) - 2) * (exp(3 * x) - 3)
chk('2v', diff(F, x).subs(x, 0) == 0 and diff(F, x, 2).subs(x, 0) == 2 * 2)
# 3 反例（数值沿路径）
chk(3, limit(x / abs(x), x, 0, '+') == 1 and limit(x / abs(x), x, 0, '-') == -1 and limit(x / x**2, x, 0, '+') == oo)
# 4 积分比大小
I = [float(sp.Integral(exp(x**2) * sin(x), (x, 0, k * pi)).evalf(20)) for k in (1, 2, 3)]
chk(4, I[1] < I[0] < I[2], I)
J = [float(sp.Integral(exp(-x) * sin(x), (x, 0, k * pi)).evalf()) for k in (1, 2, 3)]
chk('4v', J[1] < J[2] < J[0])
chk('4v2', float(sp.Integral(exp(x**2) * cos(x), (x, 0, pi)).evalf()) < 0)
# 5 行列式
c1, c2, c3, c4 = symbols('c1:5')
a1, a2, a3, a4 = Matrix([0, 0, c1]), Matrix([0, 1, c2]), Matrix([1, -1, c3]), Matrix([-1, 1, c4])
d = lambda *v: sp.expand(Matrix.hstack(*v).det())
chk(5, d(a1, a3, a4) == 0 and d(a1, a2, a3) == -c1 and d(a1, a2, a4) == c1 and d(a2, a3, a4) == -c3 - c4)
# 6 相似
P = Matrix([[1, 2, 0], [0, 1, 3], [1, 0, 1]]); L = sp.diag(1, 1, 2); A = P * L * P.inv()
Q = Matrix.hstack(P[:, 0] + P[:, 1], P[:, 1], P[:, 2])
chk(6, Q.inv() * A * Q == L)
Q2 = Matrix.hstack(P[:, 0] + P[:, 2], P[:, 1], P[:, 2])
chk('6v', Q2.inv() * A * Q2 == Matrix([[1, 0, 0], [0, 1, 0], [1, 0, 2]]))
# 7 指数
xp, yp = symbols('xp yp', positive=True)
chk(7, integrate(exp(-xp) * integrate(4 * exp(-4 * yp), (yp, xp, oo)), (xp, 0, oo)) == R(1, 5))
chk('7v', integrate(4 * exp(-4 * yp) * exp(-2 * yp), (yp, 0, oo)) == R(2, 3))
# 8 相关系数
EX = R(1, 2); EXY = integrate(x * (1 - x), (x, 0, 1)); DX = integrate(x**2, (x, 0, 1)) - EX**2
chk(8, (EXY - EX * EX) / DX == -1)
# 9 微分方程
C1, C2 = symbols('C1 C2'); fx = C1 * exp(x) + C2 * exp(-2 * x)
chk(9, simplify(diff(fx, x, 2) + diff(fx, x) - 2 * fx) == 0)
res = sp.expand(diff(fx, x, 2) + fx - 2 * exp(x))
sol = sp.solve([res.subs(x, 0), diff(res, x).subs(x, 0)], [C1, C2])
chk(9, sol == {C1: 1, C2: 0}, sol)
# 10
chk(10, abs(float(sp.Integral(x * sqrt(2 * x - x**2), (x, 0, 2)).evalf()) - math.pi / 2) < 1e-9)
chk('10v', abs(float(sp.Integral(x**2 * sqrt(2 * x - x**2), (x, 0, 2)).evalf()) - 5 * math.pi / 8) < 1e-9)
chk('10v2', abs(float(sp.Integral(x * sqrt(2 * x - x**2), (x, 0, 1)).evalf()) - (math.pi / 4 - 1 / 3)) < 1e-9)
# 11
u = x * y + z / y; pt = {x: 2, y: 1, z: 1}
grad = [diff(u, v).subs(pt) for v in (x, y, z)]
chk(11, grad == [1, 1, 1] and R(1 + 2 + 2, 3) == R(5, 3))
# 12
chk(12, sqrt(3) * integrate(integrate(y**2, (x, 0, 1 - y)), (y, 0, 1)) == sqrt(3) / 12)
chk('12v', sqrt(3) * integrate(integrate(x * y, (x, 0, 1 - y)), (y, 0, 1)) == sqrt(3) / 24)
# 13
al = Matrix([1, 2, 2]) / 3
chk(13, (sp.eye(3) - al * al.T).rank() == 2 and (sp.eye(3) - 2 * al * al.T).det() == -1 and (sp.eye(3) - 2 * al * al.T).rank() == 3)
be = Matrix([1, 1, 0]); chk('13v', (sp.eye(3) - be * be.T).rank() == 3)
# 14
chk(14, R(1, 2) / (1 - R(1, 3)) == R(3, 4))
# 15 不等式
g = x * log((1 + x) / (1 - x)) + cos(x) - 1 - x**2 / 2
g1 = log((1 + x) / (1 - x)) + 2 * x / (1 - x**2) - sin(x) - x
chk(15, simplify(diff(g, x) - g1) == 0 and simplify(diff(g1, x) - (4 / (1 - x**2) ** 2 - 1 - cos(x))) == 0)
random.seed(1)
for _ in range(4000):
    v = random.uniform(-0.9999, 0.9999)
    chk(15, g.subs(x, v).evalf() >= -1e-13 and (v < 0 or g1.subs(x, v).evalf() >= -1e-13))
# 16 极值
f = x * exp(-(x**2 + y**2) / 2)
st = sp.solve([diff(f, x), diff(f, y)], [x, y], dict=True)
chk(16, sorted((s[x], s[y]) for s in st) == [(-1, 0), (1, 0)])
for px, sign in ((1, -1), (-1, 1)):
    A_, B_, C_ = [diff(f, *v).subs({x: px, y: 0}) for v in ((x, x), (x, y), (y, y))]
    chk(16, simplify(A_ * C_ - B_**2 - 2 * exp(-1)) == 0 and sp.sign(A_) == sign and simplify(f.subs({x: px, y: 0}) - px * exp(-R(1, 2))) == 0)
chk(16, simplify(diff(f, x, 2) - x * (x**2 - 3) * exp(-(x**2 + y**2) / 2)) == 0 and simplify(diff(f, y, 2) - x * (y**2 - 1) * exp(-(x**2 + y**2) / 2)) == 0)
h = x * y * exp(-(x**2 + y**2) / 2)
chk('16v', simplify(h.subs({x: 1, y: 1}) - exp(-1)) == 0 and (diff(h, x, 2) * diff(h, y, 2) - diff(h, x, y) ** 2).subs({x: 0, y: 0}) == -1)
# 17 幂级数
S = (1 + x**2) / (1 - x**2) ** 2 + log((1 + x) / (1 - x)) / x
for v in (0.5, -0.3, 0.8):
    num = sum((4 * k * k + 4 * k + 3) / (2 * k + 1) * v ** (2 * k) for k in range(4000))
    chk(17, abs(num - float(S.subs(x, v))) < 1e-8, v)
chk(17, limit(S, x, 0) == 3 and simplify(S.subs(x, R(1, 2)) - (R(20, 9) + 2 * log(3))) == 0)
chk('17v', abs(sum((k * k + 1) / k * 0.4**k for k in range(1, 400)) - (0.4 / 0.36 - math.log(0.6))) < 1e-10 and abs(sum((k + 1) ** 2 * 0.4**k for k in range(400)) - 1.4 / 0.6**3) < 1e-10)
# 18 曳物线
ft = log(1 / cos(t) + sin(t) / cos(t)) - sin(t); fp = diff(ft, t)
chk(18, simplify(fp - sin(t) ** 2 / cos(t)) == 0 and ft.subs(t, 0) == 0)
for v in (0.3, 0.9, 1.4):
    fpv = float(fp.subs(t, v)); dist2 = (math.cos(v) / math.sin(v) * fpv) ** 2 + math.cos(v) ** 2
    chk(18, abs(dist2 - 1) < 1e-10)
chk(18, integrate(sin(t) ** 2, (t, 0, pi / 2)) == pi / 4 and integrate(cos(t) * sin(t) / cos(t), (t, 0, pi / 2)) == 1 and pi * integrate(sin(t) ** 2 * cos(t), (t, 0, pi / 2)) == pi / 3)
# 19 曲线积分：直接参数化
P_ = lambda X, Y: 3 * X**2 * Y; Q_ = lambda X, Y: X**3 + X - 2 * Y
def line(X, Y, lo, hi): return integrate(P_(X, Y) * diff(X, t) + Q_(X, Y) * diff(Y, t), (t, lo, hi))
I19 = line(1 - cos(t), sin(t), 0, pi) + line(2 * cos(t), 2 * sin(t), 0, pi / 2)
chk(19, simplify(I19 - (pi / 2 - 4)) == 0, I19)
P2 = lambda X, Y: 3 * X**2 * Y; Q2_ = lambda X, Y: X**3 - 2 * Y
I19b = integrate(P2(1 - cos(t), sin(t)) * sin(t) + Q2_(1 - cos(t), sin(t)) * cos(t), (t, 0, pi)) + integrate(P2(2 * cos(t), 2 * sin(t)) * (-2 * sin(t)) + Q2_(2 * cos(t), 2 * sin(t)) * 2 * cos(t), (t, 0, pi / 2))
chk('19v', simplify(I19b + 4) == 0)
chk('19v2', simplify(line(1 - cos(t), sin(t), 0, pi) + line(2 * cos(t), 2 * sin(t), 0, pi) - 3 * pi / 2) == 0)
# 20
A = Matrix([[1, a, 0, 0], [0, 1, a, 0], [0, 0, 1, a], [a, 0, 0, 1]]); b = Matrix([1, -1, 0, 0])
chk(20, sp.expand(A.det()) == 1 - a**4)
A1 = A.subs(a, 1); Am = A.subs(a, -1)
chk(20, A1.rank() == 3 and A1.row_join(b).rank() == 4 and Am.rank() == 3 and Am.row_join(b).rank() == 3)
chk(20, Am * Matrix([0, -1, 0, 0]) == b and Am * Matrix([1, 1, 1, 1]) == sp.zeros(4, 1))
b2 = Matrix([1, -1, 1, -1])
chk('20v', A1.row_join(b2).rank() == 4 and Am * Matrix([1, 0, 1, 0]) == b2)
for N in (3, 4, 5, 6):
    M = sp.eye(N) + a * Matrix(N, N, lambda i, j: 1 if j == (i + 1) % N else 0)
    chk('20v', sp.expand(M.det()) == 1 + (-1) ** (N + 1) * a**N)
# 21
A = Matrix([[1, 0, 1], [0, 1, 1], [-1, 0, a], [0, a, -1]])
chk(21, sp.solve(sp.factor((A.T * A).det()), a) == [-1] and A.subs(a, -1).rank() == 2 and A.subs(a, 0).rank() == 3)
B = (A.T * A).subs(a, -1)
chk(21, B == Matrix([[2, 0, 2], [0, 2, 2], [2, 2, 4]]) and B.eigenvals() == {0: 1, 2: 1, 6: 1})
for lam, v in ((0, [-1, -1, 1]), (2, [1, -1, 0]), (6, [1, 1, 2])):
    chk(21, B * Matrix(v) == lam * Matrix(v))
Qm = Matrix([[-1 / sqrt(3), 1 / sqrt(2), 1 / sqrt(6)], [-1 / sqrt(3), -1 / sqrt(2), 1 / sqrt(6)], [1 / sqrt(3), 0, 2 / sqrt(6)]])
chk(21, simplify(Qm.T * Qm) == sp.eye(3) and simplify(Qm.T * B * Qm) == sp.diag(0, 2, 6))
# 22
T = {(0, 0): R(1, 4), (0, 1): 0, (0, 2): R(1, 4), (1, 0): 0, (1, 1): R(1, 3), (1, 2): 0, (2, 0): R(1, 12), (2, 1): 0, (2, 2): R(1, 12)}
E = lambda fn: sum(p * fn(i, j) for (i, j), p in T.items())
chk(22, sum(T.values()) == 1 and sum(p for (i, j), p in T.items() if i == 2 * j) == R(1, 4))
cov = E(lambda i, j: (i - j) * j) - E(lambda i, j: i - j) * E(lambda i, j: j)
chk(22, cov == -R(2, 3) and E(lambda i, j: i * j) == R(2, 3) and E(lambda i, j: i) == R(2, 3))
DXm = E(lambda i, j: i * i) - R(4, 9); Dd = E(lambda i, j: (i - j) ** 2) - E(lambda i, j: i - j) ** 2
chk('22v', DXm == R(5, 9) and Dd == R(11, 9) and sum(p for (i, j), p in T.items() if i + j <= 1) == R(1, 4))
# 23
s2, zz = symbols('s2 zz', positive=True); m = symbols('m', positive=True, integer=True); Ssum = symbols('Ssum', positive=True)
lnL = -m / 2 * log(6 * pi * s2) - Ssum / (6 * s2)
chk(23, sp.solve(diff(lnL, s2), s2) == [Ssum / (3 * m)])
dens = exp(-z**2 / (6 * s2)) / sqrt(6 * pi * s2)
chk(23, simplify(integrate(dens, (z, -oo, oo)) - 1) == 0 and simplify(integrate(z**2 * dens, (z, -oo, oo)) - 3 * s2) == 0)
chk('23v', simplify(integrate(z**4 * dens, (z, -oo, oo)) - (3 * s2) ** 2 * 3) == 0)  # D(Z^2)=27s^4-9s^4=18s^4
print('2012 复算全部通过：', len(ok), '项')
