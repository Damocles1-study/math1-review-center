#!/usr/bin/env python3
# 2010 数学一 · 逐题独立复算（sympy / 数值 / 蒙特卡洛）。跑通即全部 OK。
import sympy as sp, random, math, itertools
from sympy import symbols, Rational as R, pi, sqrt, exp, log, sin, cos, atan, oo, Matrix, integrate, diff, simplify, limit, eye, E
x, y, z, t, u = symbols('x y z t u', real=True)
a, b = symbols('a b', real=True)
ok = []
def chk(no, cond, msg=''):
    assert bool(cond), '第 %s 题失配 %s' % (no, msg)
    ok.append(no)
N = lambda e: float(sp.N(e, 20))
import mpmath as mp

# 1 1^∞ 型
for av, bv in ((2, 1), (-1, 3), (R(1, 2), 0)):
    L = limit((x**2 / ((x - av) * (x + bv)))**x, x, oo)
    chk(1, simplify(L - exp(av - bv)) == 0, (av, bv, L))
chk(1, simplify(x**2 - (x - a) * (x + b) - ((a - b) * x + a * b)) == 0)
chk('1v1', limit((x**2 / ((x - 2) * (x + 2)))**(x**2), x, oo) == exp(4))
chk('1v2', simplify(limit(((x + log(3)) / (x - log(3)))**x, x, oo) - 9) == 0)

# 2 隐函数：取几个具体 F 验 x z_x + y z_y = z
zz = symbols('zz')
for Fexpr in (lambda p, q: p + q - 1, lambda p, q: p**2 + q**3 - 2, lambda p, q: sp.sin(p) + q * p - q):
    G = Fexpr(y / x, zz / x)
    zx = -diff(G, x) / diff(G, zz); zy = -diff(G, y) / diff(G, zz)
    chk(2, simplify(x * zx + y * zy - zz) == 0)
G = (x - 2 * zz)**2 + sp.exp(y - 3 * zz) - 5   # F(x-az, y-bz), a=2, b=3
chk('2v', simplify(2 * (-diff(G, x) / diff(G, zz)) + 3 * (-diff(G, y) / diff(G, zz)) - 1) == 0)

# 3 反常积分：对若干 (m,n) 数值积分都有限，且与截断无关
def I3(m, n):
    g = lambda s: abs(mp.log(1 - s))**(2.0 / m) / s**(1.0 / n)
    return mp.quad(g, [0, 0.5, 1])
for m_, n_ in ((1, 1), (1, 5), (7, 1), (3, 2), (20, 1)):
    v = I3(m_, n_); chk(3, mp.isfinite(v) and v > 0, (m_, n_, v))
chk(3, abs(mp.quad(lambda s: mp.log(s)**2, [0, 1]) - 2) < 1e-9)
# 变式：分母 x^n，m=1,n=2 收敛（指数 0），m=2,n=2 发散（指数 -1）
chk('3v', mp.isfinite(mp.quad(lambda s: mp.log(1 - s)**2 / s**2, [0, 0.5])))
d1 = mp.quad(lambda s: abs(mp.log(1 - s)) / s**2, [1e-6, 0.5]); d2 = mp.quad(lambda s: abs(mp.log(1 - s)) / s**2, [1e-12, 0.5])
chk('3v', d2 - d1 > 10)   # 像 ln 一样增长 ⟹ 发散

# 4 二重和式
def S4(n_):
    return sum(1.0 / (n_ + i) for i in range(1, n_ + 1)) * sum(n_ / (n_ * n_ + j * j) for j in range(1, n_ + 1))
val4 = N(integrate(1 / ((1 + x) * (1 + y**2)), (y, 0, 1), (x, 0, 1)))
chk(4, abs(S4(200000) - val4) < 1e-5 and abs(val4 - math.pi * math.log(2) / 4) < 1e-12, (S4(200000), val4))
for nm, e in (('A', N(integrate(1 / ((1 + x) * (1 + y**2)), (y, 0, x), (x, 0, 1)))), ('B', N(integrate(1 / ((1 + x) * (1 + y)), (y, 0, x), (x, 0, 1)))), ('C', N(integrate(1 / ((1 + x) * (1 + y)), (y, 0, 1), (x, 0, 1))))):
    chk(4, abs(e - val4) > 1e-3, nm)
def S4t(n_):
    return sum(sum(n_ / ((n_ + i) * (n_ * n_ + j * j)) for j in range(1, i + 1)) for i in range(1, n_ + 1))
chk('4v', abs(S4t(1500) - N(integrate(1 / ((1 + x) * (1 + y**2)), (y, 0, x), (x, 0, 1)))) < 2e-3)

# 5 AB=E 夹秩：随机构造
random.seed(1)
for m_, n_ in ((1, 2), (2, 3), (2, 5), (3, 3)):
    A = Matrix(m_, n_, lambda i, j: random.randint(-3, 3))
    while A.rank() < m_: A = Matrix(m_, n_, lambda i, j: random.randint(-3, 3))
    B = A.T * (A * A.T).inv()
    chk(5, A * B == eye(m_) and A.rank() == m_ and B.rank() == m_)
chk(5, (Matrix([[1, 0]]) * Matrix([[1], [0]])) == eye(1))

# 6 A^2+A=O，实对称，秩 3
Q, _ = Matrix(4, 4, lambda i, j: random.randint(-2, 3) + (5 if i == j else 0)).QRdecomposition()
A6 = Q * sp.diag(-1, -1, -1, 0) * Q.T
chk(6, simplify(A6**2 + A6) == sp.zeros(4) and A6.rank() == 3 and A6 == A6.T)
chk(6, [r for r in sp.solve(t**2 + t, t)] == [-1, 0])
Pn = Matrix([[1, 2, 0, 1], [0, 1, 3, 0], [1, 0, 1, 2], [2, 1, 0, 1]])   # 非对称的例子
A6n = Pn * sp.diag(-1, -1, -1, 0) * Pn.inv()
chk('6v', A6n != A6n.T and A6n**2 + A6n == sp.zeros(4) and (A6n + eye(4)).rank() == 1 and A6n.is_diagonalizable())
chk('6v2', (sp.diag(1, 1, 1, 0) - 2 * eye(4)).det() == 2)

# 7 分布函数跳跃
F1 = 1 - exp(-1)
chk(7, simplify(F1 - R(1, 2) - (R(1, 2) - exp(-1))) == 0)
chk(7, simplify(R(1, 2) + (R(1, 2) - exp(-1)) + exp(-1) - 1) == 0)
chk('7v', simplify(integrate(x * exp(-x), (x, 1, oo)) - 2 * exp(-1)) == 0)
random.seed(7); M = 400000; cnt1 = 0; tot = 0.0   # 模拟：P{X=0}=1/2，P{X=1}=1/2-1/e，其余为 1+ 之后的指数尾
for _ in range(M):
    r = random.random()
    v = 0.0 if r < 0.5 else (1.0 if r < 1 - math.exp(-1) else -math.log(1 - r))
    cnt1 += (v == 1.0); tot += v
chk(7, abs(cnt1 / M - (0.5 - math.exp(-1))) < 4e-3 and abs(tot / M - (0.5 + math.exp(-1))) < 6e-3, (cnt1 / M, tot / M))

# 8 拼接密度
f1 = exp(-x**2 / 2) / sqrt(2 * pi)
tot8 = a * integrate(f1, (x, -oo, 0)) + b * integrate(R(1, 4), (x, 0, 3))
chk(8, simplify(tot8 - (a / 2 + 3 * b / 4)) == 0 and sp.solve(tot8 - 1, a)[0].equals(2 - 3 * b / 2))
chk('8v', simplify(a * integrate(x * f1, (x, -oo, 0)) + b * integrate(x / 4, (x, 0, 3)) - (R(9, 8) * b - a / sqrt(2 * pi))) == 0)

# 9 参数方程二阶导
xt = exp(-t); yp = log(1 + t**2)            # y'(t)
d1 = simplify(yp / diff(xt, t)); d2 = simplify(diff(d1, t) / diff(xt, t))
chk(9, d2.subs(t, 0) == 0 and simplify(d2 - exp(2 * t) * (log(1 + t**2) + 2 * t / (1 + t**2))) == 0)
chk('9v', simplify(d2.subs(t, 1) - E**2 * (log(2) + 1)) == 0)
d1b = log(1 + t) / diff(xt, t); chk('9v', simplify((diff(d1b, t) / diff(xt, t)).subs(t, 0)) == 1)

# 10
chk(10, abs(mp.quad(lambda s: mp.sqrt(s) * mp.cos(mp.sqrt(s)), [0, mp.pi**2]) + 4 * mp.pi) < 1e-9)
chk(10, integrate(2 * t**2 * cos(t), (t, 0, pi)) == -4 * pi and integrate(t * sin(t), (t, 0, pi)) == pi)
chk('10v', integrate(2 * t * cos(t), (t, 0, pi)) == -4 and simplify(integrate(2 * t**2 * sin(t), (t, 0, pi)) - (2 * pi**2 - 8)) == 0)

# 11 折线上的曲线积分
s1 = integrate(x * (1 + x) + x**2, (x, -1, 0)); s2 = integrate(x * (1 - x) - x**2, (x, 0, 1))
chk(11, s1 == R(1, 6) and s2 == -R(1, 6) and s1 + s2 == 0)
chk(11, integrate(integrate(x, (x, y - 1, 1 - y)), (y, 0, 1)) == 0)
chk('11v', integrate(1 + x, (x, -1, 0)) + integrate(1 - x, (x, 0, 1)) == 1)

# 12 形心
r, th = symbols('r th', positive=True)
V = integrate(r, (z, r**2, 1), (r, 0, 1), (th, 0, 2 * pi)); Mz = integrate(z * r, (z, r**2, 1), (r, 0, 1), (th, 0, 2 * pi))
chk(12, V == pi / 2 and Mz == pi / 3 and Mz / V == R(2, 3))
chk('12v', integrate(z**3, (z, 0, 1)) / integrate(z**2, (z, 0, 1)) == R(3, 4) and integrate(z * (1 - z**2), (z, 0, 1)) / integrate(1 - z**2, (z, 0, 1)) == R(3, 8))

# 13
M13 = Matrix([[1, 1, 2], [2, 1, 1], [-1, 0, 1], [0, 2, a]])
chk(13, M13.subs(a, 6).rank() == 2 and M13.subs(a, 5).rank() == 3 and M13.subs(a, 0).rank() == 3)
chk(13, -Matrix([1, 2, -1, 0]) + 3 * Matrix([1, 1, 0, 2]) == Matrix([2, 1, 1, 6]))

# 14 泊松
k = symbols('k', integer=True, nonnegative=True)
chk(14, sp.summation(1 / sp.factorial(k), (k, 0, oo)) == E)
chk(14, simplify(sp.summation(k**2 / sp.factorial(k), (k, 0, oo)) / E) == 2)
chk('14v', simplify(sp.summation(k**2 * 2**k / sp.factorial(k), (k, 0, oo)) * exp(-2)) == 6)
chk('14v', simplify(sp.summation(k**2 / sp.factorial(k), (k, 1, oo)) / (E - 1) - 2 * E / (E - 1)) == 0)

# 15 微分方程
C1, C2 = symbols('C1 C2')
yy = C1 * exp(x) + C2 * exp(2 * x) - x * (x + 2) * exp(x)
chk(15, simplify(diff(yy, x, 2) - 3 * diff(yy, x) + 2 * yy - 2 * x * exp(x)) == 0)
ys = (a * x**2 + b * x) * exp(x)
chk(15, sp.expand(simplify((diff(ys, x, 2) - 3 * diff(ys, x) + 2 * ys) / exp(x)) - (-2 * a * x + 2 * a - b)) == 0)
for yv, lhs, rhs in (((x - R(3, 2)) * exp(3 * x), lambda w: diff(w, x, 2) - 3 * diff(w, x) + 2 * w, 2 * x * exp(3 * x)),
                     (x**3 * exp(x) / 3, lambda w: diff(w, x, 2) - 2 * diff(w, x) + w, 2 * x * exp(x)),
                     (x + R(3, 2), lambda w: diff(w, x, 2) - 3 * diff(w, x) + 2 * w, 2 * x)):
    chk('15v', simplify(lhs(yv) - rhs) == 0)

# 16 变限积分的单调性与极值
f16 = lambda s: mp.quad(lambda w: (s * s - w) * mp.exp(-w * w), [1, s * s])
fp16 = lambda s: 2 * s * mp.quad(lambda w: mp.exp(-w * w), [1, s * s])
for s0 in (-2.3, -1.4, -0.6, -0.2, 0.3, 0.8, 1.7, 2.5):
    chk(16, abs(mp.diff(f16, s0) - fp16(s0)) < 1e-8, s0)
sg = [mp.sign(fp16(s0)) for s0 in (-1.5, -0.5, 0.5, 1.5)]
chk(16, sg == [-1, 1, -1, 1], sg)
chk(16, abs(f16(1)) < 1e-15 and abs(f16(-1)) < 1e-15 and abs(f16(0) - (1 - math.exp(-1)) / 2) < 1e-12)
fpp = lambda s: 2 * mp.quad(lambda w: mp.exp(-w * w), [1, s * s]) + 4 * s * s * mp.exp(-s**4)
chk(16, abs(fpp(1) - 4 / math.e) < 1e-12 and fpp(0) < 0)
gs = [fpp(i / 400) for i in range(0, 2401)]   # x∈[0,6]
chk('16v', sum(1 for p, q in zip(gs, gs[1:]) if p * q < 0) == 1 and gs[-1] > 0)
h = sp.Function('h')
F16 = x * sp.Integral(exp(-t**2), (t, 0, x)) - sp.Integral(t * exp(-t**2), (t, 0, x))
chk('16v', simplify(diff(F16, x) - sp.Integral(exp(-t**2), (t, 0, x))) == 0)

# 17 积分不等式与夹逼
n = symbols('n', integer=True, positive=True)
chk(17, simplify(integrate(-t**n * log(t), (t, 0, 1)) - 1 / (n + 1)**2) == 0)
un = lambda nn: mp.quad(lambda w: abs(mp.log(w)) * mp.log(1 + w)**nn, [0, 0.5, 1])
for nn in (1, 2, 5, 20):
    chk(17, 0 < un(nn) < 1.0 / (nn + 1)**2 and un(nn) <= math.log(2)**nn + 1e-15, nn)
chk(17, un(60) < 1e-8 and 60**2 * un(60) < 1e-4)
In = lambda nn: nn * mp.quad(lambda w: w**nn / (1 + w), [0, 1])
chk('17v', abs(In(4000) - 0.5) < 1e-3)
chk('17v', abs(mp.quad(lambda w: abs(mp.log(w)), [0, 1]) - 1) < 1e-10)

# 18 幂级数
S18 = lambda xv: mp.nsum(lambda j: (-1)**(j - 1) * xv**(2 * j) / (2 * j - 1), [1, mp.inf])
for xv in (0.3, -0.7, 0.95, 1.0, -1.0):
    chk(18, abs(S18(xv) - xv * mp.atan(xv)) < 1e-8, xv)
chk('18v', abs(mp.nsum(lambda j: (-1)**(j - 1) / (2 * j - 1), [1, mp.inf]) - mp.pi / 4) < 1e-10)
for xv in (0.4, -0.8, 1.0):
    chk('18v', abs(mp.nsum(lambda j: (-1)**(j - 1) * xv**(2 * j) / (j * (2 * j - 1)), [1, mp.inf]) - (2 * xv * mp.atan(xv) - mp.log(1 + xv**2))) < 1e-8)
chk('18v', abs(mp.nsum(lambda j: 0.6**(2 * j) / (2 * j - 1), [1, mp.inf]) - 0.3 * mp.log(1.6 / 0.4)) < 1e-10)

# 19 轨迹与曲面积分
Fs = x**2 + y**2 + z**2 - y * z - 1
nvec = [diff(Fs, v) for v in (x, y, z)]
chk(19, nvec == [2 * x, 2 * y - z, -y + 2 * z])
chk(19, simplify(Fs.subs(z, y / 2) - (x**2 + R(3, 4) * y**2 - 1)) == 0)
num = sp.expand(nvec[0]**2 + nvec[1]**2 + nvec[2]**2)
chk(19, sp.expand(num - 4 * Fs - (4 + y**2 + z**2 - 4 * y * z)) == 0)
# 数值：对上半片 z=(y+sqrt(4-4x^2-3y^2))/2 直接做曲面积分
def I19(sign=1, w=lambda X_: X_ + math.sqrt(3)):
    def g(rr, tt):
        X_ = rr * mp.cos(tt); Y_ = 2 / mp.sqrt(3) * rr * mp.sin(tt)
        disc = 4 - 4 * X_**2 - 3 * Y_**2
        if disc <= 0: return mp.mpf(0)
        Z_ = (Y_ + sign * mp.sqrt(disc)) / 2
        zx = -2 * X_ / (2 * Z_ - Y_); zy = -(2 * Y_ - Z_) / (2 * Z_ - Y_)
        dS = mp.sqrt(1 + zx**2 + zy**2)
        return w(X_) * abs(Y_ - 2 * Z_) / mp.sqrt(4 + Y_**2 + Z_**2 - 4 * Y_ * Z_) * dS * 2 / mp.sqrt(3) * rr
    return mp.quad(g, [0, 1], [0, 2 * mp.pi])
mp.mp.dps = 12
chk(19, abs(I19(1) - 2 * mp.pi) < 1e-5, I19(1))
chk('19v', abs(I19(-1) - 2 * mp.pi) < 1e-5)
chk('19v', abs(I19(1, lambda X_: X_**2) - mp.pi / (2 * mp.sqrt(3))) < 1e-5)
sol = sp.solve([Fs.subs({x: 0, z: 2 * y})], y); chk('19v', set(s_[0] for s_ in sol) == {sqrt(3) / 3, -sqrt(3) / 3})
mp.mp.dps = 15

# 20 方程组
lam = symbols('lam')
A20 = Matrix([[lam, 1, 1], [0, lam - 1, 0], [1, 1, lam]]); b20 = Matrix([a, 1, 1])
chk(20, sp.factor(A20.det()) == (lam - 1)**2 * (lam + 1))
A1 = A20.subs(lam, 1); chk(20, A1.rank() == 1 and A1.row_join(b20).rank() == 2)
Am = A20.subs(lam, -1)
chk(20, Am.rank() == 2 and Am.row_join(b20.subs(a, -2)).rank() == 2 and Am.row_join(b20.subs(a, 0)).rank() == 3)
kk = symbols('kk')
chk(20, simplify(Am * (Matrix([R(3, 2), -R(1, 2), 0]) + kk * Matrix([1, 0, 1])) - b20.subs(a, -2)) == sp.zeros(3, 1))
chk('20v', Am * Matrix([-R(1, 2), -R(1, 2), -2]) == b20.subs(a, -2))

# 21 二次型
q3 = Matrix([sqrt(2) / 2, 0, sqrt(2) / 2]); q1 = Matrix([0, 1, 0]); q2 = Matrix([-1, 0, 1]) / sqrt(2)
Q21 = q1.row_join(q2).row_join(q3)
A21 = simplify(Q21 * sp.diag(1, 1, 0) * Q21.T)
chk(21, A21 == Matrix([[R(1, 2), 0, -R(1, 2)], [0, 1, 0], [-R(1, 2), 0, R(1, 2)]]) and simplify(Q21.T * Q21) == eye(3))
chk(21, simplify(eye(3) - q3 * q3.T - A21) == sp.zeros(3) and simplify(A21 * q3) == sp.zeros(3, 1))
chk(21, sorted((A21 + eye(3)).eigenvals(multiple=True)) == [1, 2, 2] and (A21 + eye(3)).is_positive_definite)
chk('21v', simplify(2 * eye(3) + 3 * q3 * q3.T - Matrix([[R(7, 2), 0, R(3, 2)], [0, 2, 0], [R(3, 2), 0, R(7, 2)]])) == sp.zeros(3))
# y1^2 - y2^2 不唯一：两种分法给出不同的 A
B1 = q1 * q1.T - q2 * q2.T; B2 = q2 * q2.T - q1 * q1.T
chk('21v', simplify(B1 - B2) != sp.zeros(3) and simplify(B1 * q3) == sp.zeros(3, 1) and simplify(B2 * q3) == sp.zeros(3, 1))

# 22 二维正态型密度
chk(22, sp.expand(-2 * x**2 + 2 * x * y - y**2 - (-x**2 - (y - x)**2)) == 0)
fx = integrate(exp(-(y - x)**2), (y, -oo, oo)); chk(22, fx == sqrt(pi))
A22 = 1 / integrate(exp(-x**2) * sqrt(pi), (x, -oo, oo)); chk(22, A22 == 1 / pi)
fX = exp(-x**2) / sqrt(pi); fxy = exp(-2 * x**2 + 2 * x * y - y**2) / pi
chk(22, simplify(fxy / fX - exp(-(y - x)**2) / sqrt(pi)) == 0)
chk(22, abs(mp.quad(lambda p, q: mp.exp(-2 * p * p + 2 * p * q - q * q), [-mp.inf, mp.inf], [-mp.inf, mp.inf]) - mp.pi) < 1e-8)
fY = simplify(integrate(exp(-2 * (x - y / 2)**2), (x, -oo, oo)) * exp(-y**2 / 2) / pi)
chk('22v', simplify(fY - exp(-y**2 / 2) / sqrt(2 * pi)) == 0 and simplify(fxy / fY - sqrt(2 / pi) * exp(-2 * (x - y / 2)**2)) == 0)
random.seed(22); xs = [random.gauss(0, math.sqrt(.5)) for _ in range(200000)]; ys = [v + random.gauss(0, math.sqrt(.5)) for v in xs]
mx = sum(xs) / len(xs); my = sum(ys) / len(ys)
cov = sum((p - mx) * (q - my) for p, q in zip(xs, ys)) / len(xs); vx = sum((p - mx)**2 for p in xs) / len(xs); vy = sum((q - my)**2 for q in ys) / len(ys)
chk('22v', abs(cov / math.sqrt(vx * vy) - math.sqrt(2) / 2) < 6e-3)

# 23 无偏估计
th, nn_, a1, a2, a3 = symbols('theta n a1 a2 a3')
ET = sp.expand(a1 * nn_ * (1 - th) + a2 * nn_ * (th - th**2) + a3 * nn_ * th**2 - th)
solc = sp.solve(sp.Poly(ET, th).all_coeffs(), [a1, a2, a3], dict=True)[0]
chk(23, solc[a1] == 0 and solc[a2] == 1 / nn_ and solc[a3] == 1 / nn_)
random.seed(23); nv, tv, M = 12, 0.3, 120000; Ts = []
for _ in range(M):
    c = 0
    for _ in range(nv):
        c += (random.random() >= 1 - tv)   # 取到 2 或 3
    Ts.append(c / nv)
mT = sum(Ts) / M; vT = sum((w - mT)**2 for w in Ts) / M
chk(23, abs(mT - tv) < 2e-3 and abs(vT - tv * (1 - tv) / nv) < 5e-4, (mT, vT))
# 协方差非零：Cov(N2,N3) = -n p2 p3
chk(23, sp.expand(nn_ * (th - th**2) * (1 - th + th**2) + nn_ * th**2 * (1 - th**2) - 2 * nn_ * (th - th**2) * th**2 - nn_ * th * (1 - th)) == 0)
N1, N2, N3 = symbols('N1 N2 N3', positive=True)
lnL = (N2 + 2 * N3) * log(th) + (N1 + N2) * log(1 - th)
chk('23v', simplify(sp.solve(diff(lnL, th), th)[0] - (N2 + 2 * N3) / (N1 + 2 * N2 + 2 * N3)) == 0)
xb = symbols('xb', positive=True)
chk('23v', sp.expand((1 - th) + 2 * (th - th**2) + 3 * th**2 - (1 + th + th**2)) == 0 and simplify(((-1 + sqrt(4 * xb - 3)) / 2)**2 + (-1 + sqrt(4 * xb - 3)) / 2 + 1 - xb) == 0)

main = sorted(set(o for o in ok if isinstance(o, int)))
assert main == list(range(1, 24)), main
print('2010 复算全部通过：%d 项（主题 %d 题 + 举一反三）' % (len(ok), len(main)))
