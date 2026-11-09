#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2022 数学一 · 精解答案独立复算（sympy 符号 / 数值 / 蒙特卡洛）。跑：python3 _build/rich/chk/2022.py"""
import itertools, math, random
import numpy as np
import sympy as sp
from scipy import integrate

ok = []
def check(no, cond, msg=''):
    ok.append((no, bool(cond)))
    print(('✓' if cond else '✗'), '第 %s 题' % no, msg)

x, y, z, t, u, lam, n, th = sp.symbols('x y z t u lambda n theta', real=True)

# 1 反例：f(x)=ln x (x≠1)，f(1)=5 满足题设，A、C 失败；D 用 f=ln x+(x-1)^2 sin(1/(x-1)) 打掉
f1 = sp.log(x) + (x - 1)**2 * sp.sin(1 / (x - 1))
lim1 = sp.limit(f1 / sp.log(x), x, 1)
fp = sp.diff(f1, x)
# f'(x) 在 x→1 时振荡：取两列点看 f' 的值
s1 = [float(fp.subs(x, 1 + 1 / (2 * k * math.pi))) for k in range(50, 53)]
s2 = [float(fp.subs(x, 1 + 1 / ((2 * k + 1) * math.pi))) for k in range(50, 53)]
check(1, lim1 == 1 and abs(s1[0] - s2[0]) > 1.5, 'f=ln x+(x-1)²sin(1/(x-1))：极限=%s，f\'沿两列点 ≈ %.3f / %.3f ⟹ lim f\' 不存在，B' % (lim1, s1[0], s2[0]))

# 2 z=xy f(y/x)，x z_x + y z_y = 2z ⟹ 2xy f(u)=y^2 ln u ⟹ f(u)=u ln u / 2
F = sp.Function('f')
zz = x * y * F(y / x)
lhs = sp.simplify(x * sp.diff(zz, x) + y * sp.diff(zz, y) - 2 * zz)
fsol = u * sp.log(u) / 2
zz2 = x * y * fsol.subs(u, y / x)
rhs = sp.simplify(x * sp.diff(zz2, x) + y * sp.diff(zz2, y) - y**2 * (sp.log(y) - sp.log(x)))
check(2, lhs == 0 and sp.simplify(rhs.subs({x: 2, y: 3})) == 0 and fsol.subs(u, 1) == 0 and sp.diff(fsol, u).subs(u, 1) == sp.Rational(1, 2),
      'f(1)=0, f\'(1)=1/2 ⟹ B')

# 3 x_n=(-1)^n：sin(cos x_n) 常数 → 有极限；x_n 不收敛；cos(sin x_n) 也是常数但 sin x_n=±sin1 不收敛 ⟹ A、B、C 错，D 对
xs = [(-1)**k for k in range(1, 9)]
c1 = len({round(math.sin(math.cos(v)), 12) for v in xs}) == 1
c2 = len({round(math.sin(v), 12) for v in xs}) == 2
# D：sin 在 [0,1] 上严格增连续 ⟹ 反函数连续；随机数列检验 arcsin(sin(cos x_n)) = cos x_n
xr = [random.uniform(-math.pi / 2, math.pi / 2) for _ in range(1000)]
c3 = all(abs(math.asin(math.sin(math.cos(v))) - math.cos(v)) < 1e-12 for v in xr)
check(3, c1 and c2 and c3, 'x_n=(-1)^n 打掉 A、B、C；arcsin∘sin 在 [0,1] 上恒等 ⟹ D')

# 4 数值积分
I1 = integrate.quad(lambda v: v / (2 * (1 + math.cos(v))), 0, 1)[0]
I2 = integrate.quad(lambda v: math.log(1 + v) / (1 + math.cos(v)), 0, 1)[0]
I3 = integrate.quad(lambda v: 2 * v / (1 + math.sin(v)), 0, 1)[0]
check(4, I1 < I2 < I3, 'I1=%.5f < I2=%.5f < I3=%.5f ⟹ A' % (I1, I2, I3))

# 5 A 只充分：E 可对角化但特征值不互异。C 反例：J（λ=1 三重、特征空间二维）有三个两两无关的特征向量却不可对角化；
#   D 反例：M5 的两个特征空间 span(e1)、span(e3) 互相正交，M5 仍不可对角化；B 是充要
M5 = sp.Matrix([[1, 1, 0], [0, 1, 0], [0, 0, 2]])
J = sp.Matrix([[1, 1, 0], [0, 1, 0], [0, 0, 1]])
c_vecs = [sp.Matrix([1, 0, 0]), sp.Matrix([0, 0, 1]), sp.Matrix([1, 0, 1])]
c_eig = all(J * v == v for v in c_vecs)
c_pair = all(sp.Matrix.hstack(a, b).rank() == 2 for a, b in itertools.combinations(c_vecs, 2))
ev = M5.eigenvects()
d_orth = (ev[0][2][0].T * ev[1][2][0])[0] == 0
check(5, c_eig and c_pair and not J.is_diagonalizable() and d_orth and not M5.is_diagonalizable() and sp.eye(3).is_diagonalizable(),
      'C 反例 J、D 反例 M5 都不可对角化；E 说明 A 不必要 ⟹ A')

# 6 随机构造 Ax=0 与 Bx=0 同解的 A,B（B=PA，P 可逆），检查 C 两个分块方程组同解，D 不一定
def nullspace_eq(M1, M2):
    N1, N2 = M1.nullspace(), M2.nullspace()
    if len(N1) != len(N2): return False
    if not N1: return True
    return sp.Matrix.hstack(*N1).rank() == sp.Matrix.hstack(*(N1 + N2)).rank()
random.seed(6)
okC, badD = True, False
for _ in range(30):
    A = sp.Matrix(3, 3, lambda i, j: random.randint(-2, 2)); A[2, :] = A[0, :] + A[1, :]
    P = sp.Matrix(3, 3, lambda i, j: random.randint(-2, 2))
    if P.det() == 0: continue
    B = P * A
    O = sp.zeros(3)
    C1 = sp.Matrix(sp.BlockMatrix([[A, B], [O, B]])); C2 = sp.Matrix(sp.BlockMatrix([[B, A], [O, A]]))
    D1 = sp.Matrix(sp.BlockMatrix([[A * B, B], [O, A]])); D2 = sp.Matrix(sp.BlockMatrix([[B * A, A], [O, B]]))
    okC &= nullspace_eq(C1, C2)
    if not nullspace_eq(D1, D2): badD = True
check(6, okC and badD, 'C 恒同解；D 找到不同解的实例 ⟹ C')

# 7 逐个 λ 判秩
def eqv(L):
    a1, a2, a3, a4 = (sp.Matrix(v) for v in ([L, 1, 1], [1, L, 1], [1, 1, L], [1, L, L**2]))
    r1 = sp.Matrix.hstack(a1, a2, a3).rank(); r2 = sp.Matrix.hstack(a1, a2, a4).rank(); r = sp.Matrix.hstack(a1, a2, a3, a4).rank()
    return r1 == r2 == r
d1 = sp.factor(sp.Matrix([[lam, 1, 1], [1, lam, 1], [1, 1, lam]]).det())
d2 = sp.factor(sp.Matrix([[lam, 1, 1], [1, lam, lam], [1, 1, lam**2]]).det())
res7 = {L: eqv(L) for L in (-2, -1, 0, 1, 2, 3, sp.Rational(1, 2))}
check(7, res7 == {-2: False, -1: False, 0: True, 1: True, 2: True, 3: True, sp.Rational(1, 2): True},
      '|α1α2α3|=%s，|α1α2α4|=%s；λ=-1、-2 不等价，其余等价 ⟹ C' % (d1, d2))

# 8
D8 = 4 * sp.Rational(9, 12) + 2 - 4 * (-1)
check(8, D8 == 9, 'D=4·3/4+2+4=%s ⟹ C' % D8)

# 9 蒙特卡洛：X~N(0,1)，μ2=1，μ4=3；n=50，ε=0.5 ⟹ 界 (3-1)/(50·0.25)=0.16，频率应 ≤ 0.16
rng = np.random.default_rng(9)
nn, eps = 50, 0.5
X = rng.standard_normal((200000, nn))
freq = np.mean(np.abs((X**2).mean(axis=1) - 1) >= eps)
check(9, freq <= (3 - 1) / (nn * eps**2), '频率 %.4f ≤ 界 %.3f（A）' % (freq, (3 - 1) / (nn * eps**2)))

# 10 Y=X+Z
Xs = rng.standard_normal(1000000); Ys = Xs + rng.standard_normal(1000000)
r = np.corrcoef(Xs, Ys)[0, 1]
check(10, abs(r - math.sqrt(2) / 2) < 3e-3, '蒙特卡洛 ρ≈%.4f，√2/2=%.4f ⟹ D' % (r, math.sqrt(2) / 2))

# 11
fx = x**2 + 2 * y**2
g = sp.Matrix([sp.diff(fx, x), sp.diff(fx, y)]).subs({x: 0, y: 1})
check(11, g.norm() == 4, '梯度 %s，模 4' % list(g))

# 12
xq = sp.symbols('xq', positive=True)
F12 = 2 * sp.sqrt(xq) * sp.log(xq) - 4 * sp.sqrt(xq)
num12 = integrate.quad(lambda v: math.log(v) / math.sqrt(v), 1, math.e**2)[0]
I12 = sp.simplify(F12.subs(xq, sp.E**2) - F12.subs(xq, 1))
check(12, sp.simplify(sp.diff(F12, xq) - sp.log(xq) / sp.sqrt(xq)) == 0 and I12 == 4 and abs(num12 - 4) < 1e-9, '原函数求导验证；积分=%s，数值 %.10f' % (I12, num12))

# 13 max (x^2+y^2) e^{-(x+y)} on x,y≥0
grid = np.linspace(0, 12, 1201)
GX, GY = np.meshgrid(grid, grid)
H = (GX**2 + GY**2) * np.exp(-(GX + GY))
check(13, abs(H.max() - 4 / math.e**2) < 1e-6 and abs(GX[np.unravel_index(H.argmax(), H.shape)] + GY[np.unravel_index(H.argmax(), H.shape)] - 2) < 1e-9,
      '网格最大值 %.6f，4/e²=%.6f，在 (2,0)/(0,2) 处 ⟹ k ≥ 4e^{-2}' % (H.max(), 4 / math.e**2))

# 14 比值极限 e^{-1-x}；端点 x=-1 通项 n! e^n / n^n → ∞
ratio = sp.limit(((n / (n + 1))**n), n, sp.oo)
term = [math.exp(math.lgamma(k + 1) + k - k * math.log(k)) for k in (10, 100, 150)]
check(14, ratio == sp.exp(-1) and term[0] < term[1] < term[2] and term[2] > 20, '(n/(n+1))^n→%s；x=-1 时通项 %s ↑∞ ⟹ a=-1' % (ratio, [round(v, 2) for v in term]))

# 15 随机矩阵验证 B-A=-E
random.seed(15)
for _ in range(5):
    A = sp.Matrix(3, 3, lambda i, j: random.randint(-3, 3))
    E = sp.eye(3)
    if A.det() == 0 or (E - A).det() == 0: continue
    B = (E - (E - A).inv()).inv() * A
    assert B - A == -E
check(15, True, 'B−A=−E（随机 3 阶矩阵直接解出 B 验证）')

# 16 构造样本空间验证：Ω=[0,1)，A=[0,1/3)，B=[1/3,2/3)?? 需 B、C 独立且都与 A 不交 ⟹ 在 [1/3,1) 上做
# 用离散均匀样本空间 9 点：A={0,1,2}，B={3,4,5}，C={3,6,7}? P(BC)=1/9=P(B)P(C) ✓
O9 = set(range(9)); A16 = {0, 1, 2}; B16 = {3, 4, 5}; C16 = {3, 6, 7}
P = lambda S: sp.Rational(len(S), 9)
assert not (A16 & B16) and not (A16 & C16) and P(B16 & C16) == P(B16) * P(C16)
ans16 = P((B16 | C16) & (A16 | B16 | C16)) / P(A16 | B16 | C16)
check(16, ans16 == sp.Rational(5, 8), '九点样本空间实例：%s' % ans16)

# 17 解 ODE、验渐近线
yy = sp.Function('y')
xp = sp.symbols('x', positive=True)
sol = sp.dsolve(sp.Eq(yy(xp).diff(xp) + yy(xp) / (2 * sp.sqrt(xp)), 2 + sp.sqrt(xp)), yy(xp), ics={yy(1): 3}).rhs
target = 2 * xp + sp.exp(1 - sp.sqrt(xp))
k17 = sp.limit(sol / xp, xp, sp.oo); b17 = sp.limit(sol - k17 * xp, xp, sp.oo); l0 = sp.limit(sol, xp, 0, '+')
check(17, sp.simplify(sol - target) == 0 and k17 == 2 and b17 == 0 and l0 == sp.E,
      'y=%s；k=%s，b=%s，x→0⁺ 时 y→%s ⟹ 渐近线只有 y=2x' % (sp.simplify(sol), k17, b17, l0))

# 18 数值二重积分
g18 = lambda yv, xv: (xv - yv)**2 / (xv**2 + yv**2) if (xv, yv) != (0, 0) else 0
# D = {(x,y): y-2 ≤ x ≤ sqrt(4-y^2), 0≤y≤2}
I18 = integrate.dblquad(lambda xv, yv: (xv - yv)**2 / (xv**2 + yv**2), 0, 2, lambda yv: yv - 2, lambda yv: math.sqrt(4 - yv**2), epsabs=1e-10)[0]
check(18, abs(I18 - (2 * math.pi - 2)) < 1e-6, '数值 %.8f，2π−2=%.8f' % (I18, 2 * math.pi - 2))

# 19 直接参数化三段数值积分
def line_int(path, a, b, N=20001):
    ts = np.linspace(a, b, N); X_, Y_, Z_ = path(ts)
    dX, dY, dZ = np.gradient(X_, ts), np.gradient(Y_, ts), np.gradient(Z_, ts)
    Pv = Y_ * Z_**2 - np.cos(Z_); Qv = 2 * X_ * Z_**2; Rv = 2 * X_ * Y_ * Z_ + X_ * np.sin(Z_)
    return np.trapz(Pv * dX + Qv * dY + Rv * dZ, ts)
L1 = line_int(lambda s: (0.5 * np.cos(s), np.sin(s), 0 * s), 0, math.pi / 2)        # (1/2,0,0)→(0,1,0)
L2 = line_int(lambda s: (0 * s, np.cos(s), np.sin(s)), 0, math.pi / 2)              # (0,1,0)→(0,0,1)
L3 = line_int(lambda s: (0.5 * np.sin(s), 0 * s, np.cos(s)), 0, math.pi / 2)        # (0,0,1)→(1/2,0,0)
Pf = y * z**2 - sp.cos(z); Qf = 2 * x * z**2; Rf = 2 * x * y * z + x * sp.sin(z)
curl = [sp.simplify(sp.diff(Rf, y) - sp.diff(Qf, z)), sp.simplify(sp.diff(Pf, z) - sp.diff(Rf, x)), sp.simplify(sp.diff(Qf, x) - sp.diff(Pf, y))]
check(19, abs(L1 - 0.5) < 1e-6 and abs(L2) < 1e-6 and abs(L3 + 0.5) < 1e-6 and curl == [-2 * x * z, 0, z**2],
      'L1=%.6f L2=%.6f L3=%.6f，合计 %.2e；旋度 %s' % (L1, L2, L3, L1 + L2 + L3, curl))

# 20 证明题：数值抽查结论两个方向（凸函数满足；非凸函数在 f''<0 处的小区间上不等式反向）
def mid_vs_avg(f, a, b):
    return f((a + b) / 2) - integrate.quad(f, a, b)[0] / (b - a)
conv = all(mid_vs_avg(fn, a, b) <= 1e-12 for fn in (math.exp, lambda v: v**4, lambda v: math.cosh(v)) for a, b in ((-2, 1), (0.3, 0.31), (-5, 7)))
nonc = mid_vs_avg(math.sin, 1.4, 1.8) > 0   # sin''=-sin<0 在 [1.4,1.8]
# 法二的极限：∫_{x0-δ}^{x0+δ} f − 2δ f(x0) ~ f''(x0) δ^3 / 3
ff = sp.sin(x); x0 = sp.Rational(3, 2); d = sp.symbols('d', positive=True)
expr = sp.integrate(ff, (x, x0 - d, x0 + d)) - 2 * d * ff.subs(x, x0)
lim20 = sp.limit(expr / d**3, d, 0, '+')
check(20, conv and nonc and sp.simplify(lim20 - sp.diff(ff, x, 2).subs(x, x0) / 3) == 0, '凸函数中点值 ≤ 平均值；sin 在 [1.4,1.8] 反向；极限 = f\'\'(x0)/3')

# 21
A21 = sp.Matrix(3, 3, lambda i, j: (i + 1) * (j + 1))
Q = sp.Matrix.hstack(sp.Matrix([1, 2, 3]) / sp.sqrt(14), sp.Matrix([-2, 1, 0]) / sp.sqrt(5), sp.Matrix([-3, -6, 5]) / sp.sqrt(70))
xv = sp.Matrix(sp.symbols('x1:4'))
fq = sp.expand((xv.T * A21 * xv)[0])
check(21, sp.simplify(Q.T * Q) == sp.eye(3) and sp.simplify(Q.T * A21 * Q) == sp.diag(14, 0, 0)
      and sp.expand(fq - (xv[0] + 2 * xv[1] + 3 * xv[2])**2) == 0 and sorted(A21.eigenvals().items()) == [(0, 2), (14, 1)],
      'Q^T A Q = diag(14,0,0)，f=(x1+2x2+3x3)²')

# 22 符号求 MLE + 蒙特卡洛方差
xs_, ys_ = sp.symbols('Sx Sy', positive=True); nn_, mm_ = sp.symbols('n m', positive=True)
lnL = -nn_ * sp.log(th) - xs_ / th - mm_ * sp.log(2 * th) - ys_ / (2 * th)
th_hat = sp.solve(sp.diff(lnL, th), th)[0]
nn2, mm2, theta0 = 5, 7, 1.7
Xs22 = rng.exponential(theta0, (400000, nn2)); Ys22 = rng.exponential(2 * theta0, (400000, mm2))
est = (Xs22.sum(axis=1) + Ys22.sum(axis=1) / 2) / (nn2 + mm2)
check(22, sp.simplify(th_hat - (xs_ + ys_ / 2) / (nn_ + mm_)) == 0 and abs(est.mean() - theta0) < 5e-3 and abs(est.var() - theta0**2 / (nn2 + mm2)) / (theta0**2 / (nn2 + mm2)) < 0.02,
      'θ̂=%s；MC 方差 %.5f，θ²/(n+m)=%.5f' % (th_hat, est.var(), theta0**2 / (nn2 + mm2)))

# ── 详解 / 变式里的数抽查 ──
A6 = sp.Matrix([[1, 0], [0, 0]]); B6 = sp.Matrix([[0, 0], [1, 0]])
check('6变', nullspace_eq(A6, B6) and not nullspace_eq(A6 * B6, B6 * A6), 'D 的显式反例：Ax=0 与 Bx=0 同解，ABx=0 与 BAx=0 不同解')
check('7变', d1.subs(lam, 2) == 4 and d2.subs(lam, 2) == 9 and d1.subs(lam, -1) == 4 and d2.subs(lam, -2) == 9, 'λ=2 两行列式 4、9；λ=-1 第一组 4；λ=-2 第二组 9')
F12b = 2 * sp.sqrt(xq) * sp.log(xq)**2 - 8 * sp.sqrt(xq) * sp.log(xq) + 16 * sp.sqrt(xq)
check('12变', sp.simplify(sp.diff(F12b, xq) - sp.log(xq)**2 / sp.sqrt(xq)) == 0 and sp.simplify(F12b.subs(xq, sp.E**2) - F12b.subs(xq, 1) - (8 * sp.E - 16)) == 0
      and sp.simplify(F12.subs(xq, sp.E**4) - F12.subs(xq, 1) - (4 * sp.E**2 + 4)) == 0, '∫ln²x/√x = 8e−16；上限 e⁴ 时 4e²+4')
sol2 = sp.dsolve(sp.Eq(yy(xp).diff(xp) + yy(xp) / (2 * sp.sqrt(xp)), sp.sqrt(xp)), yy(xp)).rhs
C1 = sp.Symbol('C1')
check('17变', sp.simplify(sol2.subs(C1, 0) - (2 * xp - 4 * sp.sqrt(xp) + 4)) == 0, '去掉 2 后通解 2x−4√x+4+Ce^{-√x}')
I18b = integrate.dblquad(lambda r, t: math.sin(2 * t) * r, 0, math.pi / 2, 0, 2)[0]
I18c = integrate.quad(lambda t: 2 / (math.sin(t) - math.cos(t))**2, math.pi / 2, math.pi)[0]
check('18变', abs(I18b - 2) < 1e-9 and abs(I18c - 2) < 1e-9, 'D1 上 ∬2xy/(x²+y²)=2；三角形面积极坐标验算 2')
# ∮ z dx + x dy + y dz 在同一条 L 上 = π/2
def line_int2(path, a, b, N=20001):
    ts = np.linspace(a, b, N); X_, Y_, Z_ = path(ts)
    return np.trapz(Z_ * np.gradient(X_, ts) + X_ * np.gradient(Y_, ts) + Y_ * np.gradient(Z_, ts), ts)
J19 = sum(line_int2(pth, 0, math.pi / 2) for pth in (lambda s_: (0.5 * np.cos(s_), np.sin(s_), 0 * s_), lambda s_: (0 * s_, np.cos(s_), np.sin(s_)), lambda s_: (0.5 * np.sin(s_), 0 * s_, np.cos(s_))))
check('19变', abs(J19 - math.pi / 2) < 1e-6, '∮z dx+x dy+y dz = %.6f，π/2=%.6f' % (J19, math.pi / 2))
B21 = sp.Matrix(3, 3, lambda i, j: (i + 1) + (j + 1))
check('21变', B21.rank() == 2 and A21**3 == 14**2 * A21, 'a_ij=i+j 秩 2；A³=14²A')
check('10变', abs(np.corrcoef(Xs, 2 * Xs + rng.standard_normal(1000000))[0, 1] - 2 / math.sqrt(5)) < 3e-3, 'Y|X~N(2x,1) 时 ρ=2/√5')

bad = [no for no, c in ok if not c]
print('\n全部通过' if not bad else '\n✗ 未通过：%s' % bad)
raise SystemExit(1 if bad else 0)
