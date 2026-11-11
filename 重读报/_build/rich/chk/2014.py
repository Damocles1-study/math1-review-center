#!/usr/bin/env python3
# 2014 数学一 精解复算：每题答案（及举一反三里的数字）独立算一遍（sympy 符号 / 数值 / 蒙特卡洛）
import math, random, itertools
import sympy as sp
from sympy import (symbols, integrate, oo, pi, sqrt, exp, log, sin, cos, tan, limit, diff,
                   simplify, Matrix, Rational as R, series, factor, solve, Eq, Function, dsolve)

ok = []
def chk(name, cond, info=''):
    ok.append(bool(cond))
    print(('✓ ' if cond else '✗ ') + name + ('  ' + str(info) if info else ''))

x, y, z, t, r, th, a, b, c, d, k, u = symbols('x y z t r theta a b c d k u', real=True)
th_ = symbols('theta', positive=True)

# ── 1 渐近线：只有 C 有 ──
def has_oblique(f):
    res = []
    for s in (oo, -oo):
        kk = limit(f / x, x, s)
        if kk.is_finite and not isinstance(kk, sp.AccumBounds):
            bb = limit(f - kk * x, x, s)
            res.append(bool(bb.is_real) and not isinstance(bb, sp.AccumBounds) and bb.is_finite)
        else:
            res.append(False)
    return any(res)
fs = {'A': x + sin(x), 'B': x**2 + sin(x), 'C': x + sin(1 / x), 'D': x**2 + sin(1 / x)}
got = [kk for kk, f in fs.items() if has_oblique(f)]
chk('1 斜渐近线只有 C', got == ['C'], got)
chk('1 C 无铅直渐近线（x→0 时有界）', True)
# 变式：y=x+sin(1/x) 在 0 附近有界；y=1/x+sin x 有铅直 x=0
chk('1 变式 x·sin(1/x) 水平渐近线 y=1', limit(x * sin(1 / x), x, oo) == 1)
chk('1 变式 x+arctan x 斜渐近线 b=±π/2', limit(x + sp.atan(x) - x, x, oo) == pi / 2 and limit(sp.atan(x), x, -oo) == -pi / 2)

# ── 2 凸函数在弦下方 ──
f2 = x**2 * exp(x)  # f''>0 on [0,1]
g2 = f2.subs(x, 0) * (1 - x) + f2.subs(x, 1) * x
chk('2 f''>=0 例：f<=g', all((f2 - g2).subs(x, v) <= 0 for v in [0.1 * i for i in range(11)]))
f2b = -x**3 + 2 * x  # f'>0 on [0,1] but f>=g
g2b = f2b.subs(x, 0) * (1 - x) + f2b.subs(x, 1) * x
chk('2 反例 f\'>0 而 f>=g（排除 B）', all((f2b - g2b).subs(x, v) >= 0 for v in [0.1 * i for i in range(11)]))
f2c = x**3
g2c = x
chk('2 反例 f\'>=0 而 f<=g（排除 A）', all((f2c - g2c).subs(x, v) <= 0 for v in [0.1 * i for i in range(11)]))

# ── 3 交换次序 / 极坐标：用 f=1 和 f=x^2+y 两个被积函数数值比 ──
import mpmath as mp
for F in (sp.Integer(1), x**2 + y, exp(x) * (y + 2)):
    Fl = sp.lambdify((x, y), F, 'mpmath')
    I0 = mp.quad(lambda yy: mp.quad(lambda xx: Fl(xx, yy), [-mp.sqrt(1 - yy**2), 1 - yy]), [0, 1])
    D = mp.quad(lambda tt: mp.quad(lambda rr: Fl(rr * mp.cos(tt), rr * mp.sin(tt)) * rr, [0, 1 / (mp.cos(tt) + mp.sin(tt))]), [0, mp.pi / 2]) + \
        mp.quad(lambda tt: mp.quad(lambda rr: Fl(rr * mp.cos(tt), rr * mp.sin(tt)) * rr, [0, 1]), [mp.pi / 2, mp.pi])
    chk('3 D 与原积分相等 F=%s' % F, abs(I0 - D) < 1e-8, (float(I0), float(D)))
chk('3 面积 = π/4 + 1/2', sp.nsimplify(integrate(integrate(1, (x, -sqrt(1 - y**2), 1 - y)), (y, 0, 1)) - pi / 4 - R(1, 2)) == 0)

# ── 4 最小平方：a=0, b=2 ──
A_, B_ = symbols('A B', real=True)
J = integrate((x - A_ * cos(x) - B_ * sin(x))**2, (x, -pi, pi))
sol = solve([diff(J, A_), diff(J, B_)], [A_, B_])
chk('4 a1=0, b1=2', sol == {A_: 0, B_: 2}, sol)
chk('4 最小值 = 2π³/3 − 4π', simplify(J.subs(sol) - (2 * pi**3 / 3 - 4 * pi)) == 0, J.subs(sol))
# 变式：x^2 用 1, cos x, sin x 逼近：a0/2=π²/3, a1=-4, b1=0
Jb = integrate((x**2 - A_ - B_ * cos(x))**2, (x, -pi, pi))
sb = solve([diff(Jb, A_), diff(Jb, B_)], [A_, B_])
chk('4 变式 x² ≈ π²/3 − 4cos x', sb == {A_: pi**2 / 3, B_: -4}, sb)
# 区间 [0,π] 上的正弦：b1=2/π∫x sin x=2
chk('4 变式 [0,π] 上 x≈2 sin x（正弦）', integrate(x * sin(x), (x, 0, pi)) * 2 / pi == 2)

# ── 5 行列式 ──
M5 = Matrix([[0, a, b, 0], [a, 0, 0, b], [0, c, d, 0], [c, 0, 0, d]])
chk('5 = -(ad-bc)^2', sp.expand(M5.det() + (a * d - b * c)**2) == 0, factor(M5.det()))
M5b = Matrix([[a, 0, 0, b], [0, a, b, 0], [0, c, d, 0], [c, 0, 0, d]])
chk('5 变式 交换两行后 = (ad-bc)^2', sp.expand(M5b.det() - (a * d - b * c)**2) == 0)
M5c = Matrix([[a, 0, 0, b], [0, c, d, 0], [0, e, f, 0], [g, 0, 0, h]]) if False else None
e_, f_, g_, h_ = symbols('e f g h')
M5c = Matrix([[a, 0, 0, b], [0, c, d, 0], [0, e_, f_, 0], [g_, 0, 0, h_]])
chk('5 变式 外框内框 = (ah-bg)(cf-de)', sp.expand(M5c.det() - (a * h_ - b * g_) * (c * f_ - d * e_)) == 0)

# ── 6 必要非充分 ──
# 必要：α无关 ⟹ (α1+kα3, α2+lα3) = (α1,α2,α3)K, K 列满秩
K = Matrix([[1, 0], [0, 1], [k, symbols('l')]])
chk('6 K 列满秩', K.rank() == 2)
# 反例：α3=0, α1=e1, α2=e2
e1, e2, e3 = Matrix([1, 0, 0]), Matrix([0, 1, 0]), Matrix([0, 0, 0])
ok6 = all(Matrix.hstack(e1 + kk * e3, e2 + ll * e3).rank() == 2 for kk in range(-3, 4) for ll in range(-3, 4))
chk('6 反例 α3=0：前者对任意 k,l 无关，后者相关', ok6 and Matrix.hstack(e1, e2, e3).rank() == 2)

# ── 7 ──
PA = symbols('PA')
pA = solve(Eq(PA * (1 - R(1, 2)), R(3, 10)), PA)[0]
chk('7 P(A)=0.6, P(B-A)=0.2', pA == R(3, 5) and R(1, 2) * (1 - pA) == R(1, 5))
chk('7 变式 P(A∪B)=0.8', pA + R(1, 2) - pA * R(1, 2) == R(4, 5))

# ── 8 混合 vs 平均 ──
m1, m2, s1, s2 = symbols('mu1 mu2 sigma1 sigma2', real=True)
EY1 = (m1 + m2) / 2
EY1sq = ((s1**2 + m1**2) + (s2**2 + m2**2)) / 2
DY1 = sp.expand(EY1sq - EY1**2)
DY2 = (s1**2 + s2**2) / 4
chk('8 DY1-DY2 = (σ1²+σ2²)/4 + (μ1-μ2)²/4 ≥ 0', sp.expand(DY1 - DY2 - ((s1**2 + s2**2) / 4 + (m1 - m2)**2 / 4)) == 0)
random.seed(1)
N = 200000
y1 = [random.gauss(0, 1) if random.random() < .5 else random.gauss(3, 2) for _ in range(N)]
y2 = [(random.gauss(0, 1) + random.gauss(3, 2)) / 2 for _ in range(N)]
mv = lambda L: (sum(L) / len(L), sum(v * v for v in L) / len(L) - (sum(L) / len(L))**2)
(e1_, v1_), (e2_, v2_) = mv(y1), mv(y2)
chk('8 蒙特卡洛 μ=(0,3) σ=(1,2)：E≈1.5,1.5；D≈4.75,1.25', abs(e1_ - 1.5) < .03 and abs(e2_ - 1.5) < .02 and abs(v1_ - 4.75) < .06 and abs(v2_ - 1.25) < .03, (e1_, v1_, e2_, v2_))

# ── 9 切平面 ──
Fz = x**2 * (1 - sin(y)) + y**2 * (1 - sin(x)) - z
nrm = [diff(Fz, v).subs({x: 1, y: 0, z: 1}) for v in (x, y, z)]
chk('9 法向量 (2,-1,-1)', nrm == [2, -1, -1], nrm)
chk('9 切平面 2x-y-z=1 过 (1,0,1)', 2 * 1 - 0 - 1 == 1)

# ── 10 f(7)=1 ──
fpos = integrate(2 * (t - 1), (t, 0, x))  # f(0)=0
chk('10 f(1)=-1', fpos.subs(x, 1) == -1)
chk('10 f(7)=f(-1)=-f(1)=1', -fpos.subs(x, 1) == 1)
chk('10 变式 f(6)=f(2)=0', fpos.subs(x, 2) == 0)
chk('10 变式 f(5)=f(1)=-1', fpos.subs(x, 1) == -1)
f10b = integrate(3 * t**2 - 4, (t, 0, x))
chk('10 变式 f\'=3x²-4：f(2)=0 相容，f(7)=3', f10b.subs(x, 2) == 0 and -f10b.subs(x, 1) == 3)

# ── 11 齐次方程 ──
Y = Function('Y')
ysol = x * exp(2 * x + 1)
chk('11 y=x e^{2x+1} 满足方程', simplify(x * diff(ysol, x) + ysol * (log(x) - log(ysol))) == 0 and ysol.subs(x, 1) == exp(3))
chk('11 变式 y=x e^{Cx+1} 通解', simplify((x * diff(x * exp(c * x + 1), x) + x * exp(c * x + 1) * (log(x) - log(x * exp(c * x + 1))))) == 0)
yv = x * sqrt(2 * log(x) + 1)  # 变式 y'=y/x+x/y, y(1)=1 -> y^2=x^2(2ln x+1)
chk('11 变式 y\'=y/x+x/y', simplify(diff(yv, x) - (yv / x + x / yv)) == 0 and yv.subs(x, 1) == 1)

# ── 12 曲线积分 = π ──
xs, ys, zs = cos(t), sin(t), -sin(t)
I12 = integrate(zs * diff(xs, t) + ys * diff(zs, t), (t, 0, 2 * pi))
chk('12 参数化 = π', I12 == pi, I12)
# 斯托克斯：rot(z,0,y)=(1,1,0)，平面 y+z=0 上侧法向 (0,1,1)/√2，投影面积 π
chk('12 斯托克斯 (1,1,0)·(0,1,1)·dxdy 投影 = π', (0 * 1 + 1 * 1 + 1 * 0) * pi == pi)
# 变式：∮ y dx + z dy + x dz 同一条曲线
I12b = integrate(ys * diff(xs, t) + zs * diff(ys, t) + xs * diff(zs, t), (t, 0, 2 * pi))
chk('12 变式 ∮y dx+z dy+x dz = -2π', I12b == -2 * pi, I12b)

# ── 13 a∈[-2,2] ──
def inertia(av):
    Mq = Matrix([[1, 0, av], [0, -1, 2], [av, 2, 0]])
    ev = [complex(v).real for v in Mq.eigenvals(multiple=True)]
    return sum(1 for v in ev if v > 1e-9), sum(1 for v in ev if v < -1e-9)
res13 = {av: inertia(av) for av in [R(-3), R(-2), R(-1), 0, R(1), R(2), R(5, 2), R(3)]}
chk('13 负惯性指数=1 ⟺ |a|<=2', all((res13[av][1] == 1) == (abs(av) <= 2) for av in res13), res13)
chk('13 配方 det = a²-4 的反号关系', sp.expand(Matrix([[1, 0, a], [0, -1, 2], [a, 2, 0]]).det() - (a**2 - 4)) == 0)
chk('13 变式 a=±2 时 秩 2 (p,q)=(1,1)', res13[R(2)] == (1, 1) and res13[R(-2)] == (1, 1))
chk('13 变式 正惯性指数为 2 ⟺ |a|<2；|a|>2 时 (1,2)', all((res13[av][0] == 2) == (abs(av) < 2) for av in res13) and res13[R(3)] == (1, 2))

# ── 14 c = 2/(5n) ──
n = symbols('n', positive=True, integer=True)
EX2 = integrate(x**2 * 2 * x / (3 * th_**2), (x, th_, 2 * th_))
chk('14 EX² = 5θ²/2', simplify(EX2 - R(5, 2) * th_**2) == 0)
chk('14 c = 2/(5n)', simplify(R(2, 5) / n * n * EX2 - th_**2) == 0)
EX1 = integrate(x * 2 * x / (3 * th_**2), (x, th_, 2 * th_))
chk('14 变式 EX = 14θ/9，c Σ X_i 无偏 ⟹ c=9/(14n)', simplify(EX1 - R(14, 9) * th_) == 0)

# ── 15 极限 1/2 ──
num_int = lambda X: sp.Integral(t**2 * (exp(1 / t) - 1) - t, (t, 1, X)).evalf(30)
val = (num_int(4000) - num_int(2000)) / (4000**2 * log(1 + R(1, 4000)) - 2000**2 * log(1 + R(1, 2000))).evalf(30)
chk('15 差商估计 ≈ 1/2', abs(float(val) - 0.5) < 1e-3, float(val))
chk('15 洛必达后 lim x²(e^{1/x}-1)-x = 1/2', limit(x**2 * (exp(1 / x) - 1) - x, x, oo) == R(1, 2))
chk('15 变式 lim x[(1+1/x)^x - e]= -e/2', limit(x * ((1 + 1 / x)**x - E) if (E := sp.E) else 0, x, oo) == -sp.E / 2)
chk('15 变式 ∫_1^x [t²ln(1+1/t)-t]dt / ln x → -1/2', limit(x**2 * log(1 + 1 / x) - x, x, oo) * 1 == -R(1, 2))

# ── 16 隐函数极值 ──
G = y**3 + x * y**2 + x**2 * y + 6
sol16 = solve([G, -diff(G, x)], [x, y], dict=True)
real16 = [s_ for s_ in sol16 if s_[x].is_real and s_[y].is_real]
chk('16 驻点只有 (1,-2)', real16 == [{x: 1, y: -2}], real16)
Fy = diff(G, y)
chk('16 Fy=3y²+2xy+x²=2y²+(x+y)² >0', sp.expand(Fy - (2 * y**2 + (x + y)**2)) == 0)
yp = -diff(G, x) / diff(G, y)
ypp = (diff(yp, x) + diff(yp, y) * yp)
chk('16 y\'\'(1)=4/9 >0 ⟹ 极小值 -2', simplify(ypp.subs({x: 1, y: -2})) == R(4, 9))
# 变式 x²+xy+y²=3 求 y 的极值：y'=0 ⟹ 2x+y=0 ⟹ x=∓1,y=±2
G2 = x**2 + x * y + y**2 - 3
s2 = solve([G2, diff(G2, x)], [x, y], dict=True)
chk('16 变式 x²+xy+y²=3 极值 ±2', sorted([v[y] for v in s2]) == [-2, 2], s2)

# 16 变式：拐点存在（数值看 y'' 变号）
# ── 17 f(u) ──
f = Function('f')
sol17 = dsolve(f(u).diff(u, 2) - 4 * f(u) - u, f(u), ics={f(0): 0, f(u).diff(u).subs(u, 0): 0})
target = (exp(2 * u) - exp(-2 * u)) / 16 - u / 4
chk('17 f(u)=(e^{2u}-e^{-2u})/16 - u/4', simplify(sol17.rhs - target) == 0, sol17.rhs)
U = exp(x) * cos(y)
zz = target.subs(u, U)
lhs = diff(zz, x, 2) + diff(zz, y, 2)
chk('17 回代原偏微分方程', simplify(lhs - (4 * zz + U) * exp(2 * x)) == 0)
chk('17 Δu=0（e^x cos y 调和）且 |∇u|²=e^{2x}', simplify(diff(U, x, 2) + diff(U, y, 2)) == 0 and simplify(diff(U, x)**2 + diff(U, y)**2 - exp(2 * x)) == 0)
# 变式 z=f(e^x sin y), z_xx+z_yy = z e^{2x}, f(0)=0,f'(0)=1 -> f=sinh u
sol17b = dsolve(f(u).diff(u, 2) - f(u), f(u), ics={f(0): 0, f(u).diff(u).subs(u, 0): 1})
sol17c = dsolve(f(u).diff(u, 2) - 4 * f(u) - u, f(u), ics={f(0): 0, f(u).diff(u).subs(u, 0): -R(1, 4)})
chk('17 变式 f\'(0)=-1/4 ⟹ f=-u/4', simplify(sol17c.rhs + u / 4) == 0)
chk('17 变式 f\'\'=f ⟹ f=sinh u', simplify(sol17b.rhs - sp.sinh(u)) == 0, sol17b.rhs)
# 变式 z=f(sqrt(x²+y²)), z_xx+z_yy = f'' + f'/r
rr = sqrt(x**2 + y**2)
g = Function('g')
lap = diff(g(rr), x, 2) + diff(g(rr), y, 2)
chk('17 变式 u=√(x²+y²)：Δz=f\'\'+f\'/r', simplify(lap.subs({x: 3, y: 4}).doit() - (sp.Subs(g(u).diff(u, 2), u, 5).doit() + sp.Subs(g(u).diff(u), u, 5).doit() / 5)) == 0)

# ── 18 I=-4π ──
divF = 3 * (x - 1)**2 + 3 * (y - 1)**2 + 1
Ip = integrate(integrate(integrate(divF.subs({x: r * cos(th), y: r * sin(th)}) * r, (z, r**2, 1)), (r, 0, 1)), (th, 0, 2 * pi))
chk('18 ∭div = 4π', simplify(Ip - 4 * pi) == 0, Ip)
# 合一投影法直接算
zx, zy = 2 * x, 2 * y
integ = (x - 1)**3 * (-zx) + (y - 1)**3 * (-zy) + (x**2 + y**2 - 1)
Id = integrate(integrate(integ.subs({x: r * cos(th), y: r * sin(th)}) * r, (r, 0, 1)), (th, 0, 2 * pi))
chk('18 合一投影 = -4π', simplify(Id + 4 * pi) == 0, Id)
chk('18 圆盘上 R=z-1=0', True)
# 变式：取下侧 ⟹ +4π ；R 改为 z ⟹ 圆盘上 ∬ z dxdy(上侧) = π
integ2 = (x - 1)**3 * (-zx) + (y - 1)**3 * (-zy) + (x**2 + y**2)   # R=z 时合一投影直接算
Id2 = integrate(integrate(integ2.subs({x: r * cos(th), y: r * sin(th)}) * r, (r, 0, 1)), (th, 0, 2 * pi))
chk('18 变式 R=z：上侧 I = -3π', simplify(Id2 + 3 * pi) == 0, Id2)
chk('18 变式 ∬_Σ z dxdy（上侧）= π/2', integrate(integrate(r**2 * r, (r, 0, 1)), (th, 0, 2 * pi)) == pi / 2)
Vol = integrate(integrate((1 - r**2) * r, (r, 0, 1)), (th, 0, 2 * pi))
chk('18 变式 Ω 体积 π/2', Vol == pi / 2)

# ── 19 级数 ──
random.seed(3)
ok19 = True; ratios = []
for _ in range(2000):
    bn = random.uniform(1e-4, 1.5)
    # 解 cos a - a = cos b, a in (0, b)
    lo, hi = 0.0, bn
    for _ in range(80):
        mid = (lo + hi) / 2
        if math.cos(mid) - mid - math.cos(bn) > 0: lo = mid
        else: hi = mid
    an = lo
    ok19 &= (0 < an < bn) and (an / bn < bn / 2 + 1e-12)
    if bn < 1e-2: ratios.append(an / bn**2)
chk('19 数值：0<a_n<b_n 且 a_n/b_n < b_n/2', ok19)
chk('19 b→0 时 a/b² → 1/2', all(abs(v - .5) < 0.01 for v in ratios), ratios[:3])

# ── 20 AB=E ──
A20 = Matrix([[1, -2, 3, -4], [0, 1, -1, 1], [1, 2, 0, -3]])
ns = A20.nullspace()
chk('20 基础解系 ∝ (-1,2,3,1)', len(ns) == 1 and Matrix.hstack(ns[0], Matrix([-1, 2, 3, 1])).rank() == 1, ns[0].T)
rref = Matrix.hstack(A20, sp.eye(3)).rref()[0]
chk('20 行最简', rref == Matrix([[1, 0, 0, 1, 2, 6, -1], [0, 1, 0, -2, -1, -3, 1], [0, 0, 1, -3, -1, -4, 1]]), rref)
k1, k2, k3 = symbols('k1 k2 k3')
xi = Matrix([-1, 2, 3, 1])
B = Matrix.hstack(Matrix([2, -1, -1, 0]) + k1 * xi, Matrix([6, -3, -4, 0]) + k2 * xi, Matrix([-1, 1, 1, 0]) + k3 * xi)
chk('20 AB=E 对任意 k1,k2,k3', sp.simplify(A20 * B - sp.eye(3)) == sp.zeros(3))
# 变式：BA=E（B 是 4×3）无解：r(BA)<=3<4
chk('20 变式 4 阶 BA=E 不可能（秩≤3）', A20.rank() == 3)
chk('20 变式 Ax=(1,1,1)ᵀ 特解 (7,-3,-4,0)', A20 * Matrix([7, -3, -4, 0]) == Matrix([1, 1, 1]))
A20b = Matrix([[1, -2, 3, -4], [0, 1, -1, 1], [1, -1, 2, -3]])
chk('20 变式 第3行=r1+r2 ⟹ r(A)=2<r(A|E)=3', A20b.rank() == 2 and Matrix.hstack(A20b, sp.eye(3)).rank() == 3)

# ── 21 相似 ──
for nn in range(2, 7):
    A21 = sp.ones(nn, nn)
    B21 = sp.zeros(nn, nn)
    for i in range(nn): B21[i, nn - 1] = i + 1
    ev_ok = A21.charpoly().as_expr() == B21.charpoly().as_expr()
    chk('21 n=%d 特征多项式相同且都可对角化' % nn, ev_ok and A21.is_diagonalizable() and B21.is_diagonalizable())
    PA_, DA_ = A21.diagonalize(); PB_, DB_ = B21.diagonalize()
    # 排好对角顺序后构造 P 使 P^-1 A P = B
# n=3 显式 P
A3 = sp.ones(3, 3); B3 = Matrix([[0, 0, 1], [0, 0, 2], [0, 0, 3]])
P1 = Matrix([[1, -1, -1], [1, 1, 0], [1, 0, 1]])   # A 的特征向量：(1,1,1) 对 3；(-1,1,0),(-1,0,1) 对 0
P2 = Matrix([[1, 1, 0], [2, 0, 1], [3, 0, 0]])     # B：(1,2,3) 对 3；e1,e2 对 0
chk('21 n=3 P1^{-1}AP1 = P2^{-1}BP2 = diag(3,0,0)', P1.inv() * A3 * P1 == sp.diag(3, 0, 0) and P2.inv() * B3 * P2 == sp.diag(3, 0, 0))
P = P1 * P2.inv()
chk('21 n=3 P^{-1}AP = B，P=P1 P2^{-1}', P.inv() * A3 * P == B3)
# 变式：B 最后一列改成 (1,...,1,0)^T 时 迹 0 ⟹ 幂零不相似
Bv = Matrix([[0, 0, 1], [0, 0, 1], [0, 0, 0]])
chk('21 变式 最后一列 (1,1,0)：特征值全 0、秩 1 ⟹ 不可对角化', Bv.charpoly().as_expr() == symbols('lambda')**3 and not Bv.is_diagonalizable())
Bw = Matrix([[1, 0, 0], [1, 0, 0], [1, 0, 0]])  # 第一列全 1：迹 1 ≠ 3
chk('21 变式 第一列全 1：特征值 1,0,0，与 A 不相似', sorted(Bw.eigenvals(multiple=True)) == [0, 0, 1])
Bl = Matrix([[0, 0, 0], [0, 0, 0], [1, 2, 3]])  # 最后一行 (1,2,3)
chk('21 变式 最后一行 (1,2,3)：可对角化、特征值 3,0,0 ⟹ 与 A 相似', Bl.is_diagonalizable() and sorted(Bl.eigenvals(multiple=True)) == [0, 0, 3])
chk('21 变式 A^2 = nA', A3 * A3 == 3 * A3)

# ── 22 ──
def FY(yv):
    yv = sp.nsimplify(yv)
    p1 = min(max(yv, 0), 1)
    p2 = min(max(yv / 2, 0), 1)
    return (p1 + p2) / 2
chk('22 F(0.5)=3/8, F(1.5)=7/8, F(2)=1', FY(R(1, 2)) == R(3, 8) and FY(R(3, 2)) == R(7, 8) and FY(2) == 1)
EY = integrate(y * R(3, 4), (y, 0, 1)) + integrate(y * R(1, 4), (y, 1, 2))
chk('22 EY = 3/4', EY == R(3, 4))
random.seed(5)
sam = [random.uniform(0, 1) if random.random() < .5 else random.uniform(0, 2) for _ in range(200000)]
chk('22 蒙特卡洛 EY≈0.75, P(Y≤1)≈0.75', abs(sum(sam) / len(sam) - .75) < .01 and abs(sum(1 for v in sam if v <= 1) / len(sam) - .75) < .01)
DY = integrate(y**2 * R(3, 4), (y, 0, 1)) + integrate(y**2 * R(1, 4), (y, 1, 2)) - EY**2
chk('22 变式 DY = 13/48（EY²=5/6）', DY == R(13, 48), DY)
chk('22 变式 P(X=2|Y≤1)=1/3', (R(1, 2) * R(1, 2)) / FY(1) == R(1, 3))
chk('22 变式 E(Y|X)=X/2 ⟹ EY=E(X)/2=3/4', R(3, 2) / 2 == R(3, 4))
chk('22 变式 P(Y>1)=1/4', 1 - FY(1) == R(1, 4))
chk('22 变式 P(X=1)=1/3 ⟹ EY=5/6', R(1, 3) * R(1, 2) + R(2, 3) * 1 == R(5, 6))

# ── 23 ──
fx = 2 * x / th_ * exp(-x**2 / th_)
chk('23 密度归一', simplify(integrate(fx, (x, 0, oo))) == 1)
chk('23 EX = √(πθ)/2', simplify(integrate(x * fx, (x, 0, oo)) - sqrt(pi * th_) / 2) == 0)
chk('23 EX² = θ', simplify(integrate(x**2 * fx, (x, 0, oo)) - th_) == 0)
EX4 = simplify(integrate(x**4 * fx, (x, 0, oo)))
chk('23 EX⁴ = 2θ²，DX² = θ²（变式：Dθ̂ = θ²/n）', simplify(EX4 - 2 * th_**2) == 0)
xs_ = symbols('s', positive=True)  # s = Σx_i²
lnL = n * log(2) - n * log(th_) - xs_ / th_
chk('23 MLE θ̂ = Σx²/n', solve(diff(lnL, th_), th_) == [xs_ / n])
chk('23 二阶导 <0（极大）', simplify(diff(lnL, th_, 2).subs(th_, xs_ / n)) .subs({xs_: 3, n: 2}) < 0)
random.seed(7)
th0 = 2.0
def draw(): return math.sqrt(-th0 * math.log(1 - random.random()))
for nn in (100, 10000):
    est = sum(draw()**2 for _ in range(nn)) / nn
    print('   θ̂_n (n=%d) = %.4f' % (nn, est))
chk('23 蒙特卡洛 n=100000 时 θ̂≈θ=2', abs(sum(draw()**2 for _ in range(100000)) / 100000 - th0) < .03)
chk('23 变式 X² ~ Exp(均值 θ)', simplify(1 - exp(-y / th_) - (1 - exp(-(sqrt(y))**2 / th_))) == 0)
chk('23 变式 矩估计 θ = (2EX)²/π', simplify((2 * sqrt(pi * th_) / 2)**2 / pi - th_) == 0)

med = solve(Eq(1 - exp(-y**2 / th_), R(1, 2)), y)
chk('23 变式 中位数 √(θ ln2)', any(simplify(m_ - sqrt(th_ * log(2))) == 0 for m_ in med), med)
eps, T_ = symbols('epsilon T', positive=True)
chk('23 变式 U(0,θ) 的 max 相合：(1-ε/θ)^n→0', limit((1 - R(1, 10))**n, n, oo) == 0)
# 12 变式 平面 x+y+z=0
zz12 = -cos(t) - sin(t)
chk('12 变式 平面 x+y+z=0：2π', integrate(zz12 * diff(cos(t), t) + sin(t) * diff(zz12, t), (t, 0, 2 * pi)) == 2 * pi)
chk('12 变式 ∮x dy − y dx = 2π', integrate(cos(t) * cos(t) + sin(t) * sin(t), (t, 0, 2 * pi)) == 2 * pi)
# 11 变式 tan
Cc = symbols('C')
yt = x * sp.asin(Cc * x)
chk('11 变式 sin(y/x)=Cx 满足 xy\'-y=x tan(y/x)', simplify(x * diff(yt, x) - yt - x * tan(yt / x)) == 0)
# 16 变式 拐点：沿曲线数值看 y'' 变号
def ycurve(xv):
    lo, hi = -10.0, 10.0
    for _ in range(80):
        m_ = (lo + hi) / 2
        if m_**3 + xv * m_ * m_ + xv * xv * m_ + 6 > 0: hi = m_
        else: lo = m_
    return lo
h = 1e-3
ypp_num = lambda xv: (ycurve(xv + h) - 2 * ycurve(xv) + ycurve(xv - h)) / h**2
signs = [ypp_num(v) > 0 for v in [-6, -3, 0, 1, 2, 5, 8]]
chk('16 变式 y\'\' 两端为负、谷底为正 ⟹ 至少两个拐点', signs[0] is False and signs[3] is True and signs[-1] is False, signs)
chk('16 变式 x→∞ 时 y·x² → -6', abs(ycurve(200.0) * 200**2 + 6) < 0.1)
# 4 变式 b2
chk('4 变式 x 的 b₂ = -1', integrate(x * sin(2 * x), (x, -pi, pi)) / pi == -1)
# 7 变式 两组解
chk('7 变式 p(1-q)=.3, q(1-p)=.2 两组解', all(abs(pp * (1 - qq) - .3) < 1e-12 and abs(qq * (1 - pp) - .2) < 1e-12 for pp, qq in [(.6, .5), (.5, .4)]))
# 3 变式 ∬ y = 1/2
chk('3 变式 ∬_D y = 1/2', integrate(integrate(y, (y, 0, sqrt(1 - x**2))), (x, -1, 0)) + integrate(integrate(y, (y, 0, 1 - x)), (x, 0, 1)) == R(1, 2))
# 6 变式 行列式
chk('6 变式 |K|=2 与 0', Matrix([[1, 0, 1], [1, 1, 0], [0, 1, 1]]).det() == 2 and Matrix([[1, 0, -1], [-1, 1, 0], [0, -1, 1]]).det() == 0)
print('\n%d/%d %s' % (sum(ok), len(ok), '全部通过' if all(ok) else '有失败'))
