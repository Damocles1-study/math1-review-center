#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2021 数学一 · 精解答案独立复算（sympy 符号 / 数值 / 蒙特卡洛）。跑通即全过。"""
import math, random
import sympy as sp
from sympy import Rational as R

x, y, z, t, n, a = sp.symbols('x y z t n a', real=True)
ok = []
def chk(name, cond):
    assert cond, name
    ok.append(name)

# 1 f'(0)
f = (sp.exp(x) - 1) / x
chk('1 f(0)连续', sp.limit(f, x, 0) == 1)
chk('1 f\'(0)=1/2', sp.limit((f - 1) / x, x, 0) == R(1, 2))
chk('1 f\'\'(0)=1/3', sp.series(f, x, 0, 4).removeO().coeff(x, 2) * 2 == R(1, 3))

# 2 df(1,1)：解两个线性方程
f1, f2 = sp.symbols('f1 f2')
e1 = sp.Eq(f1 + f2, sp.diff(x * (x + 1)**2, x).subs(x, 0))
e2 = sp.Eq(f1 + 2 * f2, sp.diff(2 * x**2 * sp.log(x), x).subs(x, 1))
s = sp.solve([e1, e2], [f1, f2])
chk('2 f1=0,f2=1', s[f1] == 0 and s[f2] == 1)

# 3 泰勒
ser = sp.series(sp.sin(x) / (1 + x**2), x, 0, 4).removeO()
chk('3 a,b,c', [ser.coeff(x, k) for k in (1, 2, 3)] == [1, 0, R(-7, 6)])

# 4 黎曼和：取 f(x)=x^2 数值比较四个选项
F = lambda u: u * u
N = 20000
A = sum(F((2 * k - 1) / (2 * N)) / (2 * N) for k in range(1, N + 1))
B = sum(F((2 * k - 1) / (2 * N)) / N for k in range(1, N + 1))
C = sum(F((k - 1) / (2 * N)) / N for k in range(1, 2 * N + 1))
D = sum(F(k / (2 * N)) * 2 / N for k in range(1, 2 * N + 1))
chk('4 B=∫, A=½∫, C=2∫, D=4∫', abs(B - 1 / 3) < 1e-6 and abs(A - 1 / 6) < 1e-6 and abs(C - 2 / 3) < 1e-4 and abs(D - 4 / 3) < 1e-3)

# 5 惯性指数
x1, x2, x3 = sp.symbols('x1 x2 x3')
q = sp.expand((x1 + x2)**2 + (x2 + x3)**2 - (x3 - x1)**2)
M = sp.Matrix(3, 3, lambda i, j: sp.Rational(1, 2) * sp.diff(q, [x1, x2, x3][i], [x1, x2, x3][j]))
ev = M.eigenvals()
chk('5 矩阵', M == sp.Matrix([[0, 1, 1], [1, 2, 1], [1, 1, 0]]))
chk('5 特征值 3,0,-1', set(ev) == {3, 0, -1})
chk('5 变换矩阵奇异', sp.Matrix([[1, 1, 0], [0, 1, 1], [-1, 0, 1]]).det() == 0)
chk('5 配方 2z1^2-2z2^2', sp.expand(2 * (x1 + x2) * (x2 + x3) - q) == 0)

# 6 施密特
a1, a2, a3 = sp.Matrix([1, 0, 1]), sp.Matrix([1, 2, 1]), sp.Matrix([3, 1, 2])
b1 = a1; k = a2.dot(b1) / b1.dot(b1); b2 = a2 - k * b1
l1 = a3.dot(b1) / b1.dot(b1); l2 = a3.dot(b2) / b2.dot(b2); b3 = a3 - l1 * b1 - l2 * b2
chk('6 k=1,l1=5/2,l2=1/2', (k, l1, l2) == (1, R(5, 2), R(1, 2)) and b3.dot(b1) == 0 and b3.dot(b2) == 0)
chk('6 β3=(1/2,0,-1/2)', b3 == sp.Matrix([R(1, 2), 0, R(-1, 2)]))

# 7 反例 + 随机检验 A、B、D
Aa = sp.Matrix([[0, 1], [0, 0]]); Bb = sp.Matrix([[0, 0], [1, 0]])
blk = sp.BlockMatrix([[Aa, Bb * Aa], [sp.zeros(2), Aa * Aa.T]]).as_explicit()
chk('7 C 反例 r=3≠2', blk.rank() == 3 and Aa.rank() == 1)
Bb2 = sp.Matrix([[0, 1], [1, 0]])   # 原书反例
blk2 = sp.BlockMatrix([[Aa, Bb2 * Aa], [sp.zeros(2), Aa * Aa.T]]).as_explicit()
chk('7 原书反例 r=3', blk2.rank() == 3)
random.seed(7)
for _ in range(200):
    nn = 3; r0 = random.randint(0, 3)
    P = sp.randMatrix(nn, r0 if r0 else 1, -2, 2); Q = sp.randMatrix(r0 if r0 else 1, nn, -2, 2)
    AA = P * Q if r0 else sp.zeros(nn); BB = sp.randMatrix(nn, nn, -2, 2); rA = AA.rank()
    Z = sp.zeros(nn)
    assert sp.BlockMatrix([[AA, Z], [Z, AA.T * AA]]).as_explicit().rank() == 2 * rA
    assert sp.BlockMatrix([[AA, AA * BB], [Z, AA.T]]).as_explicit().rank() == 2 * rA
    assert sp.BlockMatrix([[AA, Z], [BB * AA, AA.T]]).as_explicit().rank() == 2 * rA
chk('7 A/B/D 随机 200 组恒成立', True)

# 8 D 的反例 A⊂B：P(A)=0.4,P(B)=0.6
PA, PB, PAB = 0.4, 0.6, 0.4
PU = PA + PB - PAB
chk('8 D 反例', PA / PU > (PB - PAB) / PU and not PA > PB)
# A、B、C 随机检验
random.seed(8)
for _ in range(20000):
    p = [random.random() for _ in range(4)]; S = sum(p); p = [v / S for v in p]   # AB, A~B, ~AB, ~A~B
    pab, pa_b, p_ab, p_a_b = p; pA = pab + pa_b; pB = pab + p_ab
    if not (1e-3 < pB < 1 - 1e-3): continue
    if pab / pB > pA + 1e-12: assert p_a_b / (1 - pB) > (1 - pA) - 1e-12        # B
    if pab / pB > pa_b / (1 - pB) + 1e-12: assert pab / pB > pA - 1e-12           # C
chk('8 B、C 随机 2 万组恒成立', True)

# 9 方差：蒙特卡洛
random.seed(9)
m1, m2, s1, s2, rho, nn = 1.0, -2.0, 2.0, 1.5, 0.6, 5
vals = []
for _ in range(100000):
    sx = sy = 0.0
    for _ in range(nn):
        g1, g2 = random.gauss(0, 1), random.gauss(0, 1)
        X = m1 + s1 * g1; Y = m2 + s2 * (rho * g1 + math.sqrt(1 - rho * rho) * g2)
        sx += X; sy += Y
    vals.append(sx / nn - sy / nn)
mu = sum(vals) / len(vals); var = sum((v - mu)**2 for v in vals) / len(vals)
chk('9 无偏', abs(mu - (m1 - m2)) < 0.02)
chk('9 方差', abs(var - (s1**2 + s2**2 - 2 * rho * s1 * s2) / nn) < 0.01)

# 10 第二类错误
Phi = lambda u: 0.5 * (1 + math.erf(u / math.sqrt(2)))
beta = Phi((11 - 11.5) / math.sqrt(4 / 16))
chk('10 β=1-Φ(1)', abs(beta - (1 - Phi(1))) < 1e-12)
chk('10 第一类错误最大=1-Φ(2)', abs((1 - Phi((11 - 10) / 0.5)) - (1 - Phi(2))) < 1e-12)

# 11
chk('11 π/4', sp.integrate(1 / (x**2 + 2 * x + 2), (x, 0, sp.oo)) == sp.pi / 4)

# 12 参数方程二阶导
X_ = 2 * sp.exp(t) + t + 1; Y_ = 4 * (t - 1) * sp.exp(t) + t**2
d1 = sp.simplify(sp.diff(Y_, t) / sp.diff(X_, t))
d2 = sp.simplify(sp.diff(d1, t) / sp.diff(X_, t))
chk('12 dy/dx=2t', sp.simplify(d1 - 2 * t) == 0)
chk('12 d2y/dx2|0=2/3', d2.subs(t, 0) == R(2, 3))
chk('12 点(3,-4)', (X_.subs(t, 0), Y_.subs(t, 0)) == (3, -4))

# 13 欧拉方程
yy = sp.Function('y')
sol = sp.dsolve(x**2 * yy(x).diff(x, 2) + x * yy(x).diff(x) - 4 * yy(x), yy(x), ics={yy(1): 1, yy(x).diff(x).subs(x, 1): 2})
chk('13 y=x^2', sp.simplify(sol.rhs - x**2) == 0)

# 14 高斯：∭(2x+2y+1) over 椭圆柱
r_, th = sp.symbols('r th', positive=True)
# x=2r cos, y=r sin, J=2r
I14 = sp.integrate(sp.integrate(sp.integrate((4 * r_ * sp.cos(th) + 2 * r_ * sp.sin(th) + 1) * 2 * r_, (r_, 0, 1)), (th, 0, 2 * sp.pi)), (z, 0, 2))
chk('14 4π', sp.simplify(I14 - 4 * sp.pi) == 0)
# 直接算曲面积分：上底 ∬z dxdy = 2·面积 = 4π，下底 0，侧面 x^2 n_x + y^2 n_y 积分 0
side = sp.integrate(sp.integrate(((2 * sp.cos(th))**2 * sp.cos(th) * 1 + (sp.sin(th))**2 * sp.sin(th) * 2), (th, 0, 2 * sp.pi)), (z, 0, 2))
chk('14 侧面为 0', sp.simplify(side) == 0)

# 15 伴随矩阵行和：随机构造行和为 2、|A|=3 的矩阵
random.seed(15)
cnt = 0
while cnt < 30:
    Mx = sp.Matrix(3, 3, lambda i, j: sp.Rational(random.randint(-5, 5), random.randint(1, 3)))
    Mx = Mx - sp.diag(*[sum(Mx.row(i)) - 2 for i in range(3)])  # 调对角使行和为 2
    d = Mx.det()
    if d == 0: continue
    # 用 P^{-1} D P 的思路太繁，直接缩放：行和 2 的条件保持需 det=3 —— 用相似变换 A' = A 仅检查公式 A* 行和 = |A|/2
    adj = Mx.adjugate()
    assert sum(adj.row(0)) == d / 2 and adj[0, 0] + adj[0, 1] + adj[0, 2] == d / 2
    cnt += 1
chk('15 A11+A21+A31=|A|/2=3/2', True)
Ex = sp.Matrix([[2, 0, 0], [1, 1, 0], [R(1, 2), 0, R(3, 2)]])   # 行和 2
chk('15 具体例 |A|=3 时 =3/2', Ex.det() == 3 and Ex.adjugate()[0, 0] + Ex.adjugate()[0, 1] + Ex.adjugate()[0, 2] == R(3, 2)
    and sp.Matrix(Ex).cofactor(0, 0) + Ex.cofactor(1, 0) + Ex.cofactor(2, 0) == R(3, 2))

# 16 相关系数：穷举
from fractions import Fraction as Fr
joint = {}
for xb in ['R', 'R', 'W', 'W']:
    box = ['R', 'R', 'W', 'W', xb]
    for yb in box:
        key = (xb == 'R', yb == 'R'); joint[key] = joint.get(key, 0) + Fr(1, 4 * 5)
EX = sum(p for (u, v), p in joint.items() if u); EY = sum(p for (u, v), p in joint.items() if v)
EXY = sum(p for (u, v), p in joint.items() if u and v)
cov = EXY - EX * EY; rho16 = cov / (EX * (1 - EX))  # DX=DY=1/4
chk('16 ρ=1/5', EX == Fr(1, 2) and EY == Fr(1, 2) and EXY == Fr(3, 10) and rho16 == Fr(1, 5))

# 18 和函数
S2 = (1 - x) * sp.log(1 - x) + x
for xv in [0.1, 0.5, 0.9, -0.5]:
    num = sum(xv**(k + 1) / (k * (k + 1)) for k in range(1, 4000))
    assert abs(num - float(S2.subs(x, xv))) < 1e-9
chk('18 s2=(1-x)ln(1-x)+x', True)
chk('18 s2(1)=1 且左连续', sp.limit(S2, x, 1, '-') == 1 and sp.summation(1 / (n * (n + 1)), (n, 1, sp.oo)) == 1)
chk('18 几何部分', abs(sum(math.exp(-k * 0.7) for k in range(1, 400)) - 1 / (math.exp(0.7) - 1)) < 1e-12)
chk('18 x=-1 收敛 x>1 发散', abs(sum((-1)**(k + 1) / (k * (k + 1)) for k in range(1, 20000)) - float(S2.subs(x, -1))) < 1e-6)
chk('18 S\'\'=1/(1-x)', sp.simplify(sp.diff(S2, x, 2) - 1 / (1 - x)) == 0)

# 19 条件极值
lam, mu_ = sp.symbols('lam mu')
L = z**2 + lam * (x**2 + 2 * y**2 - z - 6) + mu_ * (4 * x + 2 * y + z - 30)
sols = sp.solve([sp.diff(L, v) for v in (x, y, z, lam, mu_)], [x, y, z, lam, mu_], dict=True)
zs = sorted(set(s_[z] for s_ in sols if all(v.is_real for v in s_.values())))
chk('19 驻点 z=12,66', zs == [12, 66])
# 参数化检验：椭圆 (x+2)^2+2(y+1/2)^2 = 81/2
mx = -1e9; mn = 1e9
for i in range(200000):
    th_ = 2 * math.pi * i / 200000
    xx = -2 + math.sqrt(81 / 2) * math.cos(th_); yy_ = -0.5 + math.sqrt(81 / 4) * math.sin(th_)
    zz = 30 - 4 * xx - 2 * yy_
    assert abs(xx * xx + 2 * yy_ * yy_ - zz - 6) < 1e-8
    mx = max(mx, abs(zz)); mn = min(mn, abs(zz))
chk('19 最大 66 最小 12', abs(mx - 66) < 1e-6 and abs(mn - 12) < 1e-6)

# 20
I20 = sp.integrate((4 - r_**2) * r_, (r_, 0, 2)) * 2 * sp.pi
chk('20(I) 8π', I20 == 8 * sp.pi)
E = sp.exp(x**2 + 4 * y**2)
P = (x * E + y) / (x**2 + 4 * y**2); Q = (4 * y * E - x) / (x**2 + 4 * y**2)
chk('20 Qx=Py', sp.simplify(sp.diff(Q, x) - sp.diff(P, y)) == 0)
# 数值沿 x^2+y^2=4 逆时针积分
def integrand(th_):
    xx, yy_ = 2 * math.cos(th_), 2 * math.sin(th_); dx, dy = -2 * math.sin(th_), 2 * math.cos(th_)
    e = math.exp(xx * xx + 4 * yy_ * yy_); d = xx * xx + 4 * yy_ * yy_
    return ((xx * e + yy_) * dx + (4 * yy_ * e - xx) * dy) / d
Nn = 200000
I20b = sum(integrand(2 * math.pi * (i + .5) / Nn) for i in range(Nn)) * 2 * math.pi / Nn
chk('20(II) -π', abs(I20b + math.pi) < 1e-6)

# 21
Am = sp.Matrix([[a, 1, -1], [1, a, -1], [-1, -1, a]])
lmb = sp.symbols('lmb')
chk('21 特征多项式', sp.factor(Am.charpoly(lmb).as_expr()) == sp.factor((lmb - a + 1)**2 * (lmb - a - 2)))
Pm = sp.Matrix([[1 / sp.sqrt(2), 1 / sp.sqrt(6), 1 / sp.sqrt(3)], [-1 / sp.sqrt(2), 1 / sp.sqrt(6), 1 / sp.sqrt(3)], [0, 2 / sp.sqrt(6), -1 / sp.sqrt(3)]])
chk('21 P 正交', sp.simplify(Pm.T * Pm) == sp.eye(3))
chk('21 P^TAP 对角', sp.simplify(Pm.T * Am * Pm - sp.diag(a - 1, a - 1, a + 2)) == sp.zeros(3))
Cm = sp.Matrix([[5, -1, 1], [-1, 5, 1], [1, 1, 5]]) / 3
chk('21 C^2=(a+3)E-A', sp.simplify(Cm * Cm - ((a + 3) * sp.eye(3) - Am)) == sp.zeros(3))
chk('21 C 正定', all(v > 0 for v in Cm.eigenvals()))
chk('21 C=2E-uu^T', Cm == 2 * sp.eye(3) - sp.Matrix([1, 1, -1]) * sp.Matrix([[1, 1, -1]]) / 3)

# 22
random.seed(22)
Ns = 400000; cntX = 0; cntZ = 0; ex = 0.0
for _ in range(Ns):
    w = random.uniform(0, 2); X = min(w, 2 - w); Y = 2 - X
    cntX += X < 0.3; cntZ += (Y / X) <= 3; ex += X / Y
chk('22 X~U(0,1)', abs(cntX / Ns - 0.3) < 0.005)
chk('22 F_Z(3)=1-2/4', abs(cntZ / Ns - 0.5) < 0.005)
chk('22 E(X/Y)=2ln2-1', abs(ex / Ns - (2 * math.log(2) - 1)) < 0.003)
chk('22 符号积分', sp.simplify(sp.integrate(x / (2 - x), (x, 0, 1)) - (2 * sp.log(2) - 1)) == 0
    and sp.integrate(2 / (z + 1)**2, (z, 1, sp.oo)) == 1
    and sp.simplify(sp.integrate(2 / (z * (z + 1)**2), (z, 1, sp.oo)) - (2 * sp.log(2) - 1)) == 0)
chk('22 EZ 发散', sp.integrate((2 - x) / x, (x, 0, 1)) == sp.oo)


# ───────── 举一反三的答案 ─────────
N2 = 4000
chk('v4 Σn/(n²+k²)→π/4', abs(sum(N2 / (N2 * N2 + k * k) for k in range(1, N2 + 1)) - math.pi / 4) < 1e-3)
chk('v4 Σf(k/n²)/n→f(0)', abs(sum(math.cos(k / N2**2) for k in range(1, N2 + 1)) / N2 - 1) < 1e-3)
chk('v4 2/n Σf(2k/n)→∫0^2', abs(2 / N2 * sum((2 * k / N2)**2 for k in range(1, N2 + 1)) - 8 / 3) < 1e-2)
q2 = sp.expand((x1 + x2)**2 + (x2 + x3)**2 + (x3 + x1)**2)
M2 = sp.hessian(q2, (x1, x2, x3)) / 2
chk('v5 (x3+x1)² 正定', all(v > 0 for v in M2.eigenvals()) and sp.Matrix([[1, 1, 0], [0, 1, 1], [1, 0, 1]]).det() == 2)
q3 = sp.expand((x1 + x2)**2 + (x2 + x3)**2 + (x3 - x1)**2)
M3 = sp.hessian(q3, (x1, x2, x3)) / 2
chk('v5 全加号 秩2半正定', M3.rank() == 2 and all(v >= 0 for v in M3.eigenvals()))
chk('v5 规范形/零点', sp.expand(2 * (x1 + x2) * (x2 + x3) - q) == 0)
a3b = sp.Matrix([1, 1, 1]); L1 = a3b.dot(b1) / b1.dot(b1); L2 = a3b.dot(b2) / b2.dot(b2)
chk('v6 α3=(1,1,1) ⟹ β3=0', (L1, L2) == (1, R(1, 2)) and a3b - L1 * b1 - L2 * b2 == sp.zeros(3, 1))
random.seed(70)
for _ in range(100):
    AA = sp.randMatrix(3, 3, -3, 3); BB = sp.randMatrix(3, 3, -3, 3)
    if AA.det() != 0:
        assert sp.BlockMatrix([[AA, BB * AA], [sp.zeros(3), AA * AA.T]]).as_explicit().rank() == 6
    assert sp.BlockMatrix([[AA, AA * BB], [sp.zeros(3), BB]]).as_explicit().rank() == AA.rank() + BB.rank()
chk('v7 A 可逆时 C 成立 / [[A,AB],[O,B]]', True)
chk('v7 [[A,E],[O,A]] A=O 时 n>0', sp.BlockMatrix([[sp.zeros(2), sp.eye(2)], [sp.zeros(2), sp.zeros(2)]]).as_explicit().rank() == 2)
chk('v10 μ=12 时 β', abs(Phi((11 - 12) / 0.5) - (1 - Phi(2))) < 1e-12)
chk('v10 n=64', abs(Phi((11 - 11.5) / 0.25) - (1 - Phi(2))) < 1e-12)
chk('v10 W={≥10.5}', abs(Phi((10.5 - 11.5) / 0.5) - (1 - Phi(2))) < 1e-12 and abs(1 - Phi((10.5 - 10) / 0.5) - (1 - Phi(1))) < 1e-12)
y2 = 4 * (t - 1) * sp.exp(t)
dd = sp.diff(sp.diff(y2, t) / sp.diff(X_, t), t) / sp.diff(X_, t)
chk('v12 去掉 t² ⟹ 4/9', sp.simplify(dd.subs(t, 0)) == R(4, 9))
chk('v12 曲率 2/3', R(2, 3) / (1 + 0)**R(3, 2) == R(2, 3))
def ode(lhs, ics=None):
    return sp.dsolve(lhs, yy(x), ics=ics).rhs
chk('v13 y(1)=1,y\'(1)=0', sp.simplify(ode(x**2 * yy(x).diff(x, 2) + x * yy(x).diff(x) - 4 * yy(x), {yy(1): 1, yy(x).diff(x).subs(x, 1): 0}) - (x**2 + x**-2) / 2) == 0)
for cand, eq in [(sp.cos(2 * sp.log(x)), x**2 * sp.diff(sp.cos(2 * sp.log(x)), x, 2) + x * sp.diff(sp.cos(2 * sp.log(x)), x) + 4 * sp.cos(2 * sp.log(x))),
                 (x * sp.log(x), x**2 * sp.diff(x * sp.log(x), x, 2) - x * sp.diff(x * sp.log(x), x) + x * sp.log(x)),
                 (-x / 3, x**2 * sp.diff(-x / 3, x, 2) + x * sp.diff(-x / 3, x) - 4 * (-x / 3) - x)]:
    assert sp.simplify(eq) == 0
chk('v13 三个变式解代回成立', True)
chk('v14 z² ⟹ 8π', sp.simplify(sp.integrate(sp.integrate(sp.integrate(2 * z * 2 * r_, (r_, 0, 1)), (th, 0, 2 * sp.pi)), (z, 0, 2)) - 8 * sp.pi) == 0)
chk('v14 圆柱 8π', sp.pi * 4 * 2 == 8 * sp.pi)
def colsum0(M): return M.cofactor(0, 0) + M.cofactor(0, 1) + M.cofactor(0, 2)
# 两个 |A|=3、行和 2 的矩阵，A11+A12+A13 不同
G1 = sp.Matrix([[2, 0, 0], [1, 1, 0], [R(1, 2), 0, R(3, 2)]]); G2 = sp.Matrix([[2, 0, 0], [0, 1, 1], [0, R(1, 4), R(7, 4)]])
assert G1.det() == 3 and G2.det() == 3 and all(sum(G.row(i)) == 2 for G in (G1, G2) for i in range(3))
chk('v15 A11+A12+A13 随矩阵变', colsum0(G1) != colsum0(G2))
GT = G1.T   # 列和 2
chk('v15 列和 2 ⟹ A11+A12+A13=3/2', colsum0(GT) == R(3, 2))
chk('v15 (A*)* 行和 6 / A²−2A+E 行和 1', sum(G1.adjugate().adjugate().row(0)) == 6 and sum((G1**2 - 2 * G1 + sp.eye(3)).row(0)) == 1)
for m in range(1, 6):
    j = {}
    box0 = ['R'] * m + ['W'] * m
    for xb in ['R', 'R', 'W', 'W']:
        for yb in box0 + [xb]:
            k_ = (xb == 'R', yb == 'R'); j[k_] = j.get(k_, 0) + Fr(1, 4 * (2 * m + 1))
    ey = sum(p for (u, v), p in j.items() if v); exy = sum(p for (u, v), p in j.items() if u and v)
    assert ey == Fr(1, 2) and (exy - Fr(1, 4)) / Fr(1, 4) == Fr(1, 2 * m + 1)
chk('v16 乙盒 m 红 m 白 ⟹ ρ=1/(2m+1)', True)
T2 = (1 - x) * sp.log(1 - x) / x + 1
for xv in [-1, -0.5, 0.3, 0.8]:
    assert abs(sum(xv**k / (k * (k + 1)) for k in range(1, 20000)) - float(T2.subs(x, xv))) < 1e-4
chk('v18 Σx^n/(n(n+1))', True)
chk('v18 S2(−1)=2ln2−1', sp.simplify(S2.subs(x, -1) - (2 * sp.log(2) - 1)) == 0)
mxx = max(abs(-2 + math.sqrt(81 / 2) * math.cos(2 * math.pi * i / 100000)) for i in range(100000))
chk('v19 max|x|=2+9√2/2', abs(mxx - (2 + 9 * math.sqrt(2) / 2)) < 1e-6)
I20c = sp.integrate(sp.integrate((1 - r_**2) * r_ / sp.sqrt(2), (r_, 0, 1)), (th, 0, 2 * sp.pi))
chk('v20 椭圆 √2π/4', sp.simplify(I20c - sp.sqrt(2) * sp.pi / 4) == 0)
def circ_int(f, cx_=0, cy_=0, rr=2, sgn=1):
    tot = 0
    for i in range(Nn):
        th_ = sgn * 2 * math.pi * (i + .5) / Nn
        xx, yy_ = cx_ + rr * math.cos(th_), cy_ + rr * math.sin(th_)
        dx, dy = -rr * math.sin(th_) * sgn, rr * math.cos(th_) * sgn
        Pp, Qq = f(xx, yy_); tot += Pp * dx + Qq * dy
    return tot * 2 * math.pi / Nn
def f20(xx, yy_):
    e = math.exp(xx * xx + 4 * yy_ * yy_); d = xx * xx + 4 * yy_ * yy_
    return (xx * e + yy_) / d, (4 * yy_ * e - xx) / d
def f20b(xx, yy_):
    e = math.exp(xx * xx + yy_ * yy_); d = xx * xx + yy_ * yy_
    return (xx * e + yy_) / d, (yy_ * e - xx) / d
chk('v20 不含原点 0', abs(circ_int(f20, 3, 0, 1)) < 1e-6)
chk('v20 顺时针 π', abs(circ_int(f20, sgn=-1) - math.pi) < 1e-6)
chk('v20 分母 x²+y² ⟹ −2π', abs(circ_int(f20b) + 2 * math.pi) < 1e-6)
e3 = sp.Matrix([1, 1, -1]) / sp.sqrt(3)
chk('v21 A^3 公式', sp.simplify(Am**3 - ((a - 1)**3 * sp.eye(3) + ((a + 2)**3 - (a - 1)**3) * e3 * e3.T)) == sp.zeros(3))
Cneg = Pm * sp.diag(2, 2, -1) * Pm.T
chk('v21 非正定根也满足', sp.simplify(Cneg * Cneg - ((a + 3) * sp.eye(3) - Am)) == sp.zeros(3) and Cneg != Cm)
chk('v21 a=1 秩 1、|C|=4', Am.subs(a, 1).rank() == 1 and Cm.det() == 4)
random.seed(222); c2 = 0
for _ in range(200000):
    w = random.uniform(0, 2); X = min(w, 2 - w); c2 += (2 - X) > 2 * X
chk('v22 P(Y>2X)=2/3', abs(c2 / 200000 - 2 / 3) < 0.005)

print('\n'.join('✓ ' + s for s in ok))
print('全部 %d 项通过' % len(ok))
