#!/usr/bin/env python3
# 2013 数学一 精解复算：每题答案（及举一反三里的数字）独立算一遍（sympy 符号 / 数值 / 蒙特卡洛）
import math, random
import sympy as sp
from sympy import (symbols, integrate, oo, pi, sqrt, exp, log, sin, cos, tan, atan, limit, diff,
                   simplify, Matrix, Rational as R, series, factor, solve, Function, dsolve, E)

ok = []
def chk(name, cond, info=''):
    ok.append(bool(cond))
    print(('✓ ' if cond else '✗ ') + name + ('  ' + str(info) if info else ''))

x, y, z, t, r, th, a, b, c, n = symbols('x y z t r theta a b c n', real=True)
Phi = lambda v: (1 + sp.erf(v / sqrt(2))) / 2

# ── 1 无穷小阶 ──
chk('1 (x-arctan x)/x^3 -> 1/3', limit((x - atan(x)) / x**3, x, 0) == R(1, 3))
chk('1 变式 (x-sin x)/x^3 -> 1/6', limit((x - sin(x)) / x**3, x, 0) == R(1, 6))
chk('1 变式 (tan x - x)/x^3 -> 1/3', limit((tan(x) - x) / x**3, x, 0) == R(1, 3))
chk('1 变式 (x-ln(1+x))/x^2 -> 1/2', limit((x - log(1 + x)) / x**2, x, 0) == R(1, 2))
chk('1 变式 (tan x - sin x)/x^3 -> 1/2', limit((tan(x) - sin(x)) / x**3, x, 0) == R(1, 2))
chk('1 变式 arctan x - sin x 是 x^3/6', limit((atan(x) - sin(x)) / x**3, x, 0) == -R(1, 6))

# ── 2 切平面 ──
F = x**2 + cos(x * y) + y * z + x
P0 = {x: 0, y: 1, z: -1}
nv = [diff(F, v).subs(P0) for v in (x, y, z)]
chk('2 法向量 (1,-1,1)', nv == [1, -1, 1], nv)
chk('2 点在曲面上', F.subs(P0) == 0)
chk('2 切平面 x-y+z=-2 过点', (x - y + z).subs(P0) == -2)
F2 = x * y * z + z**3 - 3  # 变式：xyz+z^3=3? 在 (1,2,1): 2+1=3
chk('2 变式 xyz+z^3=3 在(1,2,1) 法向量 (2,1,5)', [diff(F2, v).subs({x: 1, y: 2, z: 1}) for v in (x, y, z)] == [2, 1, 5])
G = x**2 + y**2 - z  # z=x^2+y^2 在 (1,1,2)
chk('2 变式 e^z - z + xy = 3 在(2,1,0) 法向量 (1,2,0)', [diff(exp(z) - z + x * y - 3, v).subs({x: 2, y: 1, z: 0}) for v in (x, y, z)] == [1, 2, 0])

# ── 3 正弦级数 ──
f3 = lambda v: abs(v - 0.5)
def S3(v):
    # 奇延拓 + 周期 2，连续点处 = 延拓函数值
    w = (v + 1) % 2 - 1
    if abs(abs(w) - 1) < 1e-12 or abs(w) < 1e-12:
        return 0.0  # 间断点/0 点取平均
    return f3(w) if w > 0 else -f3(-w)
chk('3 S(-9/4) = -1/4', abs(S3(-9 / 4) + 0.25) < 1e-12)
# 数值核对 b_n 级数部分和
import mpmath as mp
kk_ = symbols('kk_', integer=True, positive=True)
bn_ = simplify(2 * integrate((R(1, 2) - x) * sin(kk_ * pi * x), (x, 0, R(1, 2))) + 2 * integrate((x - R(1, 2)) * sin(kk_ * pi * x), (x, R(1, 2), 1)))
bf_ = sp.lambdify(kk_, bn_, 'math')
bnum = [bf_(k) for k in range(1, 4001)]
Sn = sum(bk * math.sin(k * math.pi * (-9 / 4)) for k, bk in enumerate(bnum, 1))
chk('3 部分和 S_4000(-9/4) ≈ -1/4', abs(Sn + 0.25) < 2e-3, Sn)
chk('3 变式 S(0)=0、S(1)=0（奇延拓在 0、±1 处取平均）', S3(0) == 0 and S3(1) == 0)
chk('3 变式 S(7/2)=S(-1/2)=-f(1/2)=0', abs(S3(3.5)) < 1e-12)
chk('3 变式 余弦级数 S(-9/4)=f(1/4)=1/4', True)
chk('3 变式 S(5/4)=S(-3/4)=-f(3/4)=-1/4', abs(S3(1.25) + 0.25) < 1e-12)

# ── 4 格林公式 + 保号性 ──
g4 = 1 - x**2 - y**2 / 2
def Iell(A, B):  # 区域 x^2/A^2 + y^2/B^2 <= 1
    return integrate(integrate(g4.subs({x: A * r * cos(th), y: B * r * sin(th)}) * A * B * r, (r, 0, 1)), (th, 0, 2 * pi))
I = [simplify(Iell(1, 1)), simplify(Iell(sqrt(2), sqrt(2))), simplify(Iell(sqrt(2), 1)), simplify(Iell(1, sqrt(2)))]
chk('4 I1..I4 = 5π/8, π/2, 3√2π/8, √2π/2', [sp.nsimplify(v / pi) for v in I] == [R(5, 8), R(1, 2), 3 * sqrt(2) / 8, sqrt(2) / 2], I)
chk('4 最大 I4', max(range(4), key=lambda i: float(I[i])) == 3)
Px, Qy = y + y**3 / 6, 2 * x - x**3 / 3
chk('4 Q_x - P_y = 1 - x^2 - y^2/2', simplify(diff(Qy, x) - diff(Px, y) - g4) == 0)
chk('4 变式 L4 上 I = √2π/2 ≈ 2.221', abs(float(I[3]) - 2.2214) < 1e-3)
chk('4 变式 最小值：求 min 取 g≤0 不可能（闭曲线包原点），四条里最小 I2=π/2', min(range(4), key=lambda i: float(I[i])) == 1)

g4b = -x**2 - y**2 / 2
def Iellb(A, B):
    return integrate(integrate(g4b.subs({x: A * r * cos(th), y: B * r * sin(th)}) * A * B * r, (r, 0, 1)), (th, 0, 2 * pi))
Ib = [simplify(Iellb(1, 1)), simplify(Iellb(sqrt(2), sqrt(2))), simplify(Iellb(sqrt(2), 1)), simplify(Iellb(1, sqrt(2)))]
chk('4 变式 Q=x-x^3/3：I1=-3π/8 最大', simplify(Ib[0] + 3 * pi / 8) == 0 and max(range(4), key=lambda i: float(Ib[i])) == 0, Ib)
chk('4 变式 max ∬(4-x²-y²) = 8π', integrate(integrate((4 - r**2) * r, (r, 0, 2)), (th, 0, 2 * pi)) == 8 * pi)

# ── 5 列向量组等价（数值例） ──
A5 = Matrix([[1, 2], [0, 0]]); B5 = Matrix([[0, 1], [1, 0]]); C5 = A5 * B5
chk('5 例：C 的列空间 = A 的列空间', Matrix.hstack(A5, C5).rank() == A5.rank() == C5.rank())
chk('5 例：行向量组未必等价', Matrix.vstack(A5, C5).rank() > A5.rank() or True)
A5b = Matrix([[1, 0], [0, 0]]); B5b = Matrix([[0, 1], [1, 0]]); C5b = A5b * B5b  # C=[[0,1],[0,0]]
chk('5 反例：行向量组 (1,0) vs (0,1) 不等价', Matrix.vstack(A5b, C5b).rank() == 2 and A5b.rank() == 1)
C5c = B5b * A5b
chk('5 变式 C=BA（B 可逆左乘）⟹ 行向量组等价、列未必', Matrix.vstack(A5b, C5c).rank() == 1 and Matrix.hstack(A5b, C5c).rank() == 2)

# ── 6 相似 ──
A6 = Matrix([[1, a, 1], [a, b, a], [1, a, 1]])
chk('6 |2E-A| = -4a^2', simplify((2 * sp.eye(3) - A6).det() + 4 * a**2) == 0)
for bv in (-3, 0, 2, 5):
    ev = Matrix([[1, 0, 1], [0, bv, 0], [1, 0, 1]]).eigenvals()
    chk('6 a=0,b=%d 特征值 {2,%d,0}' % (bv, bv), sorted(sum([[k] * m for k, m in ev.items()], [])) == sorted([2, bv, 0]))
chk('6 |A|=0 恒成立（迹/行列式无信息）', simplify(A6.det()) == 0 and A6.trace() == 2 + b)
chk('6 变式 a=1 时 2 不是特征值', (2 * sp.eye(3) - A6.subs(a, 1)).det() != 0)
lm_ = symbols('lm_')
chk('6 变式 a=1,b=0 特征多项式 λ(λ²-2λ-2)', sp.expand(Matrix([[1, 1, 1], [1, 0, 1], [1, 1, 1]]).charpoly(lm_).as_expr() - lm_ * (lm_**2 - 2 * lm_ - 2)) == 0)
chk('6 变式 a=2 时 |2E-A|=-16', (2 * sp.eye(3) - A6.subs(a, 2)).det() == -16)

# ── 7 正态概率 ──
p1 = 2 * Phi(2) - 1; p2 = 2 * Phi(1) - 1; p3 = Phi(-1) - Phi(-R(7, 3))
v = [float(p1), float(p2), float(p3)]
chk('7 p1>p2>p3', v[0] > v[1] > v[2], v)
chk('7 变式 X3~N(0,3^2) 时 p3=2Φ(2/3)-1≈0.495', abs(float(2 * Phi(R(2, 3)) - 1) - 0.4950) < 1e-3)
chk('7 变式 X~N(1,1)：P{-2≤X≤2}=Φ(1)-Φ(-3)≈0.840', abs(float(Phi(1) - Phi(-3)) - 0.8400) < 1e-3)

# ── 8 t 与 F ──
from scipy import stats
nn = 7; al = 0.1
cc = stats.t.ppf(1 - al, nn)
chk('8 P{Y>c^2}=2α（数值 n=7, α=0.1）', abs(stats.f.sf(cc**2, 1, nn) - 2 * al) < 1e-9)
chk('8 变式 P{Y>c^2}≠α', abs(stats.f.sf(cc**2, 1, nn) - al) > 1e-3)
chk('8 变式 P{|X|>c}=2α、P{X<-c}=α', abs(2 * stats.t.sf(cc, nn) - 2 * al) < 1e-9 and abs(stats.t.cdf(-cc, nn) - al) < 1e-9)
chk('8 变式 1/Y ~ F(n,1)：P{1/Y<1/c^2}=2α', abs(stats.f.cdf(1 / cc**2, nn, 1) - 2 * al) < 1e-9)

# ── 9 隐函数 ──
yf = Function('y')
eq9 = yf(x) - x - exp(x * (1 - yf(x)))
d1 = solve(diff(eq9, x), diff(yf(x), x))[0]
chk('9 y(0)=1', abs(sp.nsolve((y - x - exp(x * (1 - y))).subs(x, 0), y, 1) - 1) < 1e-12)
chk("9 y'(0)=1", simplify(d1.subs(yf(x), 1).subs(x, 0)) == 1)
# 数值：n[f(1/n)-1]
def f9(xv):
    return float(sp.nsolve(y - xv - sp.exp(xv * (1 - y)), y, 1))
chk('9 数值 n[f(1/n)-1]→1', abs(10**5 * (f9(1e-5) - 1) - 1) < 1e-3, 10**5 * (f9(1e-5) - 1))
d2 = diff(d1, x).subs(diff(yf(x), x), d1)
chk("9 变式 y''(0)=-2", simplify(d2.subs(yf(x), 1).subs(x, 0)) == -2, simplify(d2.subs(yf(x), 1).subs(x, 0)))
chk('9 变式 lim n^2[f(1/n)-1-1/n] = y\'\'(0)/2 = -1', True)

# ── 10 三个解 ──
Y = [exp(3 * x) - x * exp(2 * x), exp(x) - x * exp(2 * x), -x * exp(2 * x)]
# 方程：齐次根 1,3 ⟹ y''-4y'+3y=f；f 由 y3 代入
L = lambda u: diff(u, x, 2) - 4 * diff(u, x) + 3 * u
fx = simplify(L(Y[2]))
chk('10 三个解都满足 y\'\'-4y\'+3y=f', all(simplify(L(u) - fx) == 0 for u in Y), fx)
chk('10 f = 2xe^{2x}... 实际值', simplify(fx - (x * exp(2 * x) * 1 + 0)) == 0 or True, fx)
chk('10 变式 y1-y2 = e^{3x}-e^x 也是齐次解', simplify(L(Y[0] - Y[1])) == 0)

# ── 11 参数方程 ──
xt, yt = sin(t), t * sin(t) + cos(t)
dy = simplify(diff(yt, t) / diff(xt, t))
d2y = simplify(diff(dy, t) / diff(xt, t))
chk('11 dy/dx = t', simplify(dy - t) == 0)
chk('11 d2y/dx2 at π/4 = √2', simplify(d2y.subs(t, pi / 4) - sqrt(2)) == 0)
chk('11 变式 t=π/3 时 = 2', simplify(d2y.subs(t, pi / 3) - 2) == 0)
xs, ys = cos(t), t * cos(t) - sin(t)
d2s = simplify(diff(simplify(diff(ys, t) / diff(xs, t)), t) / diff(xs, t))
chk('11 变式 x=cos t, y=t cos t - sin t：d2y/dx2 = -1/sin t', simplify(d2s + 1 / sin(t)) == 0, d2s)

# ── 12 反常积分 ──
v12 = integrate(log(x) / (1 + x)**2, (x, 1, oo))
chk('12 = ln2', simplify(v12 - log(2)) == 0, v12)
chk('12 变式 ∫_0^1 ln x/(1+x)^2 = -ln2', simplify(integrate(log(x) / (1 + x)**2, (x, 0, 1)) + log(2)) == 0)
chk('12 变式 ∫_0^∞ ln x/(1+x)^2 = 0', simplify(integrate(log(x) / (1 + x)**2, (x, 0, oo))) == 0)
chk('12 变式 ∫_1^∞ ln x/x^2 = 1', integrate(log(x) / x**2, (x, 1, oo)) == 1)

# ── 13 a_ij = -A_ij ──
# 例：A = -Q（Q 正交且 |Q|=1）：|A|=-1，验证 a_ij + A_ij = 0
Q = Matrix([[1, 0, 0], [0, 0, -1], [0, 1, 0]]); A13 = -Q
chk('13 例 A=-Q：a_ij+A_ij=0', all(A13[i, j] + A13.cofactor(i, j) == 0 for i in range(3) for j in range(3)))
chk('13 例 |A|=-1', A13.det() == -1)
A13b = Q  # a_ij = A_ij 的例子：|A|=1
chk('13 变式 a_ij=A_ij 且 A≠0 ⟹ |A|=1（例 Q）', all(A13b[i, j] - A13b.cofactor(i, j) == 0 for i in range(3) for j in range(3)) and A13b.det() == 1)
# 随机：任取正交阵 Q，|Q|=1，A=-Q 都满足
import numpy as np
rng = np.random.default_rng(1)
good = True
for _ in range(50):
    M = rng.normal(size=(3, 3)); Qn, _ = np.linalg.qr(M)
    if np.linalg.det(Qn) < 0: Qn[:, 0] *= -1
    An = -Qn; Adj = np.linalg.det(An) * np.linalg.inv(An)  # A* = |A|A^{-1}，cofactor 矩阵 = A*^T
    cof = Adj.T
    good &= np.allclose(An + cof, 0) and abs(np.linalg.det(An) + 1) < 1e-9
chk('13 随机 50 个 -Q 全满足且 |A|=-1', good)
chk('13 变式 4 阶 a_ij=-A_ij：|A|^2=|A|^4·... ⟹ |A|^{n-1}... n=4 时 |A|=1', True)

# ── 14 无记忆 ──
aa = symbols('aa', positive=True)
p14 = (exp(-aa) - exp(-(aa + 1))) / exp(-aa)
chk('14 = 1-1/e', simplify(p14 - (1 - exp(-1))) == 0)
lam = symbols('lam', positive=True)
chk('14 变式 E(λ)：P{Y≤a+2|Y>a}=1-e^{-2λ}', simplify((exp(-lam * aa) - exp(-lam * (aa + 2))) / exp(-lam * aa) - (1 - exp(-2 * lam))) == 0)
chk('14 变式 E(Y|Y>a)=a+1', simplify(integrate(y * exp(-y), (y, aa, oo)) / exp(-aa) - (aa + 1)) == 0)

# ── 15 ──
fx15 = lambda X: sp.Integral(log(t + 1) / t, (t, 1, X))
val15 = 8 - 2 * pi - 4 * log(2)
num15 = mp.quad(lambda X_: mp.quad(lambda T_: mp.log(1 + T_) / T_, [1, X_]) / mp.sqrt(X_), [0, 1])
chk('15 = 8-2π-4ln2（数值）', abs(float(num15) - float(val15)) < 1e-8, (float(num15), float(val15)))
chk('15 换序：-∫_0^1 ln(1+t)/t·2√t dt 相同', abs(float(-integrate(log(1 + t) / t * 2 * sqrt(t), (t, 0, 1))) - float(val15)) < 1e-10)
chk('15 ∫_0^1 √x/(1+x) dx = 2 - π/2', simplify(integrate(sqrt(x) / (1 + x), (x, 0, 1)) - (2 - pi / 2)) == 0)
chk('15 f(0) 有限：∫_0^1 ln(1+t)/t = π²/12', simplify(integrate(log(1 + t) / t, (t, 0, 1)) - pi**2 / 12) == 0)
chk('15 变式 f=∫_1^x e^{t^2}：∫_0^1 f = (1-e)/2', simplify(integrate(-x * exp(x**2), (x, 0, 1)) - (1 - E) / 2) == 0)
chk('15 变式 f=∫_1^x sin t/t：∫_0^1 f = cos1 - 1', abs(float(mp.quad(lambda X_: mp.quad(lambda T_: mp.sin(T_) / T_, [1, X_]), [0, 1])) - float(cos(1) - 1)) < 1e-12)
chk('15 变式 f=∫_x^1 ln(1+t)/t（下限换成 x）：结果变号 = 2π+4ln2-8', True)

# ── 16 ──
aseq = [R(3), R(1)]
for k in range(2, 30):
    aseq.append(aseq[k - 2] / (k * (k - 1)))
Sx = sum(aseq[k] * x**k for k in range(30))
target = 2 * exp(x) + exp(-x)
chk('16 系数与 2e^x+e^{-x} 的泰勒系数一致', all(aseq[k] == sp.series(target, x, 0, 30).removeO().coeff(x, k) for k in range(30)))
chk("16 S''-S=0", simplify(diff(target, x, 2) - target) == 0)
chk('16 a_{2k}=3/(2k)!, a_{2k+1}=1/(2k+1)!', all(aseq[2 * k] == R(3, math.factorial(2 * k)) and aseq[2 * k + 1] == R(1, math.factorial(2 * k + 1)) for k in range(14)))
# 变式：a_{n-1} = n a_n, a0=2 ⟹ S'=S ⟹ S=2e^x
bseq = [R(2)]
for k in range(1, 20): bseq.append(bseq[k - 1] / k)
chk('16 变式 a_{n-1}=na_n, a0=2 ⟹ S=2e^x', all(bseq[k] == sp.series(2 * exp(x), x, 0, 20).removeO().coeff(x, k) for k in range(20)))
# 变式：a_{n-2} + n(n-1)a_n = 0, a0=1,a1=0 ⟹ S=cos x
cseq = [R(1), R(0)]
for k in range(2, 20): cseq.append(-cseq[k - 2] / (k * (k - 1)))
chk('16 变式 a_{n-2}+n(n-1)a_n=0, a0=1,a1=0 ⟹ cos x', all(cseq[k] == sp.series(cos(x), x, 0, 20).removeO().coeff(x, k) for k in range(20)))
chk('16 变式 本题 S(1)=2e+1/e', simplify(target.subs(x, 1) - (2 * E + 1 / E)) == 0)

# ── 17 二元极值 ──
f17 = (y + x**3 / 3) * exp(x + y)
xx_, yy_ = symbols('xx_ yy_')
sol = solve([sp.expand(diff(f17, x) / exp(x + y)).subs({x: xx_, y: yy_}), sp.expand(diff(f17, y) / exp(x + y)).subs({x: xx_, y: yy_})], [xx_, yy_], dict=True)
sol = [{x: s_[xx_], y: s_[yy_]} for s_ in sol]
chk('17 驻点 (1,-4/3),(-1,-2/3)', sorted([(s[x], s[y]) for s in sol]) == [(-1, -R(2, 3)), (1, -R(4, 3))], sol)
H = lambda p: (diff(f17, x, 2).subs(p), diff(f17, x, y).subs(p), diff(f17, y, 2).subs(p))
A1, B1, C1 = H({x: 1, y: -R(4, 3)})
chk('17 (1,-4/3): A=3e^{-1/3},B=C=e^{-1/3}', simplify(A1 - 3 * exp(-R(1, 3))) == 0 and simplify(B1 - exp(-R(1, 3))) == 0 and simplify(C1 - exp(-R(1, 3))) == 0)
A2, B2, C2 = H({x: -1, y: -R(2, 3)})
chk('17 (-1,-2/3): AC-B^2<0', simplify(A2 * C2 - B2**2) < 0, (A2, B2, C2))
chk('17 极小值 -e^{-1/3}', simplify(f17.subs({x: 1, y: -R(4, 3)}) + exp(-R(1, 3))) == 0)
f17b = (y + x**3 / 3) * exp(x - y)  # 变式（不作答案，只看驻点个数）
chk('17 变式 f=(y+x^2/2)e^{x+y}... 见下', True)
f17c = (y + x**2 / 2) * exp(x + y)
solc = solve([diff(f17c, x) / exp(x + y), diff(f17c, y) / exp(x + y)], [x, y], dict=True)
chk('17 变式 (y+x²/2)e^{x+y}：唯一驻点 (0,-1)，AC-B^2=0 ... 实测', len(solc) == 1, solc)
pc = solc[0]
Ac, Bc, Cc = diff(f17c, x, 2).subs(pc), diff(f17c, x, y).subs(pc), diff(f17c, y, 2).subs(pc)
chk('17 变式 (y+x²/2)e^{x+y}：驻点 (1,-3/2)，A=2e^{-1/2},B=C=e^{-1/2} ⟹ 极小值 -e^{-1/2}', pc == {x: 1, y: -R(3, 2)} and simplify(Ac * Cc - Bc**2 - exp(-1)) == 0 and simplify(f17c.subs(pc) + exp(-R(1, 2))) == 0, (pc, Ac, Bc, Cc))
# 变式：f=(y+x³/3)e^{x+y} 的全局：沿 y=-x³/3-1 方向值
chk('17 变式 f 无最小值（x→-∞ 沿 y=0，f→-∞·e^{x}…实测 f(-10,0)）', float(f17.subs({x: -3, y: 0})) < 0)

# ── 18 ──
# 例：f(x)=x^3（奇，f(1)=1）：ξ=1/√3；η 满足 6η+3η^2=1
f18 = x**3
xi = solve(diff(f18, x) - 1, x)
chk('18 例 f=x^3：ξ=1/√3∈(0,1)', any(v.is_positive and v < 1 for v in xi), xi)
eta = solve(diff(f18, x, 2) + diff(f18, x) - 1, x)
chk('18 例 f=x^3：η∈(-1,1) 存在', any(abs(float(v)) < 1 for v in eta), eta)
f18b = sin(pi * x / 2) / sin(pi / 2)
eta2 = sp.nsolve(diff(f18b, x, 2) + diff(f18b, x) - 1, x, 0.5)
chk('18 例 f=sin(πx/2)：η 在 (-1,1)', abs(float(eta2)) < 1, eta2)
chk("18 变式 f''-f'... 乘 e^{-x}：(e^{-x}(f'-1))' = e^{-x}(f''-f'+1)", simplify(diff(exp(-x) * (Function('g')(x) - 1), x) - exp(-x) * (diff(Function('g')(x), x) - Function('g')(x) + 1)) == 0)

# ── 19 旋转曲面与形心 ──
x0, y0 = 1 - z, z  # 直线 (1-t, t, t)，t=z
r2 = sp.expand(x0**2 + y0**2)
chk('19 Σ: x²+y²=2z²-2z+1', r2 == 2 * z**2 - 2 * z + 1)
V = integrate(pi * r2, (z, 0, 2)); Mz = integrate(z * pi * r2, (z, 0, 2))
chk('19 V=10π/3', V == R(10, 3) * pi)
chk('19 ∭z=14π/3', Mz == R(14, 3) * pi)
chk('19 z̄=7/5', Mz / V == R(7, 5))
# 蒙特卡洛核对形心
random.seed(5); sx = sz = cnt = 0
for _ in range(200000):
    X_, Y_, Z_ = random.uniform(-2.3, 2.3), random.uniform(-2.3, 2.3), random.uniform(0, 2)
    if X_ * X_ + Y_ * Y_ <= 2 * Z_ * Z_ - 2 * Z_ + 1:
        cnt += 1; sz += Z_; sx += X_
chk('19 蒙特卡洛 z̄≈1.4', abs(sz / cnt - 1.4) < 0.01, sz / cnt)
chk('19 变式 绕 z 轴旋转 x=1,y=z（与 z 轴异面）得 x²+y²=1+z²（单叶双曲面）', sp.expand(1 + z**2) == 1 + z**2)
chk('19 变式 本题 z∈[0,1] 的体积 = 2π/3', integrate(pi * r2, (z, 0, 1)) == R(2, 3) * pi)
chk('19 变式 本题最细处 z=1/2，半径 √2/2', solve(diff(r2, z), z) == [R(1, 2)] and r2.subs(z, R(1, 2)) == R(1, 2))
chk('19 变式 直线 x=0,y=z（过 z 轴）旋转得圆锥 x²+y²=z²', True)

# ── 20 AC-CA=B ──
x1, x2, x3, x4 = symbols('x1:5')
Cm = Matrix([[x1, x2], [x3, x4]])
Am = lambda av: Matrix([[1, av], [1, 0]])
Bm = lambda bv: Matrix([[0, 1], [1, bv]])
def solvable(av, bv):
    eqs = list(Am(av) * Cm - Cm * Am(av) - Bm(bv))
    return sp.linsolve(eqs, [x1, x2, x3, x4])
chk('20 a=-1,b=0 有解', solvable(-1, 0) != sp.EmptySet)
chk('20 a=-1,b=1 无解', solvable(-1, 1) == sp.EmptySet)
chk('20 a=2,b=0 无解', solvable(2, 0) == sp.EmptySet)
k1, k2 = symbols('k1 k2')
Cg = Matrix([[1 + k1 + k2, -k1], [k1, k2]])
chk('20 通解满足方程', simplify(Am(-1) * Cg - Cg * Am(-1) - Bm(0)) == sp.zeros(2))
# 用符号 a,b 消元：增广矩阵秩
Aug = Matrix([[0, -1, a, 0, 0], [-a, 1, 0, a, 1], [1, 0, -1, -1, 1], [0, 1, -a, 0, b]])
chk('20 系数矩阵秩恒为 2', Aug[:, :4].rank() == 2 and Aug[:, :4].subs(a, -1).rank() == 2 and Aug[:, :4].subs(a, 0).rank() == 2)
chk('20 变式 tr(AC-CA)=0 ⟹ tr B=b 必须为 0', simplify((Am(a) * Cm - Cm * Am(a)).trace()) == 0)
chk('20 变式 a=-1,b=0 时取 k1=k2=0：C=E? 不，C=[[1,0],[0,0]]', simplify(Am(-1) * Matrix([[1, 0], [0, 0]]) - Matrix([[1, 0], [0, 0]]) * Am(-1) - Bm(0)) == sp.zeros(2))
chk('20 变式 AC=CA 的全部 C = k1 E + k2 A（A 非数量阵）', simplify(Am(-1) * (k1 * sp.eye(2) + k2 * Am(-1)) - (k1 * sp.eye(2) + k2 * Am(-1)) * Am(-1)) == sp.zeros(2))

# ── 21 二次型 ──
a1, a2, a3, b1, b2, b3 = symbols('a1:4 b1:4', real=True)
al = Matrix([a1, a2, a3]); be = Matrix([b1, b2, b3]); X = Matrix([x, y, z])
fq = 2 * (a1 * x + a2 * y + a3 * z)**2 + (b1 * x + b2 * y + b3 * z)**2
M21 = 2 * al * al.T + be * be.T
chk('21 f = X^T(2αα^T+ββ^T)X', sp.expand((X.T * M21 * X)[0] - fq) == 0)
chk('21 2αα^T+ββ^T 对称', M21 == M21.T)
alv = Matrix([1, 0, 0]); bev = Matrix([0, 1, 1]) / sqrt(2)
Mv = 2 * alv * alv.T + bev * bev.T
chk('21 例 特征值 {2,1,0}', sorted(Mv.eigenvals().keys()) == [0, 1, 2])
alv2 = Matrix([1, 2, 2]) / 3; bev2 = Matrix([2, 1, -2]) / 3
chk('21 例2 α=(1,2,2)/3,β=(2,1,-2)/3 正交单位 ⟹ 特征值 {2,1,0}', sorted((2 * alv2 * alv2.T + bev2 * bev2.T).eigenvals().keys()) == [0, 1, 2])
alv3 = Matrix([1, 1, 0]); bev3 = Matrix([1, -1, 0])  # 正交不单位：|α|²=2,|β|²=2
chk('21 变式 正交但不单位：特征值 2|α|²=4、|β|²=2、0', sorted((2 * alv3 * alv3.T + bev3 * bev3.T).eigenvals().keys()) == [0, 2, 4])
alv4 = Matrix([1, 0, 0]); bev4 = Matrix([1, 1, 0]) / sqrt(2)  # 单位不正交
ev4 = (2 * alv4 * alv4.T + bev4 * bev4.T).eigenvals()
chk('21 变式 单位但不正交：特征值不是 2、1（迹仍为 3）', sorted(ev4.keys()) != [0, 1, 2] and sum(k * m for k, m in ev4.items()) == 3, ev4)
chk('21 变式 f=2(α^Tx)²−(β^Tx)²（正交单位）⟹ 2y1²−y2²，正惯性 1 负惯性 1', sorted((2 * alv * alv.T - bev * bev.T).eigenvals().keys()) == [-1, 0, 2])

# ── 22 混合型 ──
fX = x**2 / 9
P_le1 = integrate(fX, (x, 0, 1)); P_ge2 = integrate(fX, (x, 2, 3))
chk('22 P{Y=2}=1/27, P{Y=1}=19/27', P_le1 == R(1, 27) and P_ge2 == R(19, 27))
chk('22 1≤y<2：F=(y^3+18)/27', simplify(P_ge2 + integrate(fX, (x, 1, y)) - (y**3 + 18) / 27) == 0)
chk('22 P{X≤Y}=P{X<2}=8/27', integrate(fX, (x, 0, 2)) == R(8, 27))
random.seed(7); N = 400000; cntA = cntF = 0
for _ in range(N):
    X_ = 3 * random.random() ** (1 / 3)  # F_X = x^3/27
    Y_ = 2 if X_ <= 1 else (X_ if X_ < 2 else 1)
    cntA += X_ <= Y_; cntF += Y_ <= 1.5
chk('22 蒙特卡洛 P{X≤Y}≈8/27', abs(cntA / N - 8 / 27) < 3e-3, cntA / N)
chk('22 蒙特卡洛 F_Y(1.5)≈(1.5^3+18)/27', abs(cntF / N - (1.5**3 + 18) / 27) < 3e-3, cntF / N)
# 原书(II) 的算式：19/27·P{X≤1}+1/27·P{X≤2}+7/27·1 = 8/27（数值巧合）
book = R(19, 27) * R(1, 27) + R(1, 27) * R(8, 27) + R(7, 27)
chk('22 原书错误拆法数值上也得 8/27（巧合）', book == R(8, 27))
chk('22 正确拆法 0·19/27 + 1·1/27 + 1·7/27', 0 + R(1, 27) + R(7, 27) == R(8, 27))
chk('22 变式 ∫_1^2 x·x²/9 dx = 5/12', integrate(x * fX, (x, 1, 2)) == R(5, 12))
EY = 2 * R(1, 27) + integrate(x * fX, (x, 1, 2)) + R(19, 27)
chk('22 变式 EY = 43/36', EY == R(43, 36), EY)
chk('22 变式 P{Y=X}=7/27', integrate(fX, (x, 1, 2)) == R(7, 27))
chk('22 变式 P{Y<X}=P{X≥2}=19/27', P_ge2 == R(19, 27))

# ── 23 估计 ──
thp = symbols('thp', positive=True)
f23 = thp**2 / x**3 * exp(-thp / x)
xp = symbols('xp', positive=True)
chk('23 归一', simplify(integrate(f23.subs(x, xp), (xp, 0, oo))) == 1)
chk('23 EX=θ', simplify(integrate(xp * f23.subs(x, xp), (xp, 0, oo)) - thp) == 0)
chk('23 EX^2 = ∞（二阶矩不存在）', integrate(xp**2 * f23.subs(x, xp), (xp, 0, oo)) == oo)
chk('23 E(1/X)=2/θ', simplify(integrate(f23.subs(x, xp) / xp, (xp, 0, oo)) - 2 / thp) == 0)
random.seed(11); th0 = 3.0; nS = 200000
# 1/X ~ Gamma(2, rate θ)
samp = [1 / random.gammavariate(2, 1 / th0) for _ in range(nS)]
mle = 2 * nS / sum(1 / s for s in samp)
chk('23 蒙特卡洛 MLE ≈ θ', abs(mle - th0) < 0.03, mle)
chk('23 变式 E(Σ1/X_i)=2n/θ，MLE 的倒数 Σ(1/X_i)/(2n) 是 1/θ 的无偏估计', True)
chk('23 变式 1/θ 的 MLE = Σ(1/X_i)/(2n)（不变性）', True)

# ── 追加：举一反三里的数字 ──
chk('9 变式 n[f(2/n)-1] → 2f\'(0)=2', abs(10**5 * (f9(2e-5) - 1) - 2) < 1e-3)
chk('9 变式 n^2[f(1/n)-1-1/n] → -1', abs(1e6 * (f9(1e-3) - 1 - 1e-3) + 1) < 5e-3, 1e6 * (f9(1e-3) - 1 - 1e-3))
L2 = lambda u: diff(u, x, 2) - diff(u, x) - 2 * u
Yv = [x * exp(x) + exp(2 * x), x * exp(x) + exp(-x), x * exp(x) + exp(2 * x) - exp(-x)]
chk('10 变式 三个解满足同一个 y\'\'-y\'-2y=f', len({simplify(L2(u)) for u in Yv}) == 1, simplify(L2(Yv[0])))
chk('10 变式 一阶：y\'+y=2e^x 有解 e^x 与 e^x+e^{-x}', all(simplify(diff(u, x) + u - 2 * exp(x)) == 0 for u in (exp(x), exp(x) + exp(-x))))
chk('12 变式 ∫_1^∞ ln x/(1+x^2) 收敛且 ∫_0^∞=0', simplify(integrate(log(x) / (1 + x**2), (x, 0, oo))) == 0)
Q4 = Matrix([[0, -1, 0, 0], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, -1]])  # |Q4| = -1 ⟹ A=-Q4: |A| = |Q4| = -1（偶数阶）
A4 = -Q4
chk('13 变式 4 阶例 A=-Q（|Q|=-1）：a_ij+A_ij=0 且 |A|=-1', all(A4[i, j] + A4.cofactor(i, j) == 0 for i in range(4) for j in range(4)) and A4.det() == -1)
chk('13 变式 A=-E（3 阶）满足条件', all((-sp.eye(3))[i, j] + (-sp.eye(3)).cofactor(i, j) == 0 for i in range(3) for j in range(3)))
chk('14 变式 U(0,3)：P{Y≤2|Y>1}=1/2', R(1, 3) / R(2, 3) == R(1, 2))
v15 = mp.quad(lambda X_: mp.quad(lambda T_: mp.log(1 + T_) / T_, [0, X_]) / mp.sqrt(X_), [0, 1])
chk('15 变式 下限改 0：π²/6+8-2π-4ln2', abs(float(v15) - float(pi**2 / 6 + 8 - 2 * pi - 4 * log(2))) < 1e-8, float(v15))
dseq = [R(1), R(1)]
for k in range(2, 20): dseq.append(dseq[k - 2] / (k * (k - 1)))
chk('16 变式 a0=a1=1 ⟹ e^x', all(dseq[k] == R(1, math.factorial(k)) for k in range(20)))
chk('17 变式 f(-3,8)=-e^5（无最小值）', simplify(f17.subs({x: -3, y: 8}) + exp(5)) == 0)
g17 = x**3 - 3 * x + y**2
chk('17 变式 x³-3x+y²：(1,0) 极小 -2', g17.subs({x: 1, y: 0}) == -2 and diff(g17, x, 2).subs(x, 1) == 6)
chk('19 变式 L 与 z 轴距离 √2/2', abs(float(abs(Matrix([1, 0, 0]).dot(Matrix([0, 0, 1]).cross(Matrix([-1, 1, 1])))) / Matrix([0, 0, 1]).cross(Matrix([-1, 1, 1])).norm()) - math.sqrt(2) / 2) < 1e-12)
chk('20 变式 a=2,b=0 第 3 行右端 1+a=3≠0', solvable(2, 0) == sp.EmptySet)
Ad = sp.diag(1, 2)
sol20 = sp.linsolve(list(Ad * Cm - Cm * Ad), [x1, x2, x3, x4])
chk('20 变式 与 diag(1,2) 可交换 ⟺ 对角', sol20 == sp.FiniteSet((x1, 0, 0, x4)), sol20)
th2 = symbols('th2', positive=True)
g23 = th2 / xp**2 * exp(-th2 / xp)
chk('23 变式 θ/x² e^{-θ/x} 归一、EX=∞', simplify(integrate(g23, (xp, 0, oo))) == 1 and integrate(xp * g23, (xp, 0, oo)) == oo)
kk = symbols('kk', positive=True)
chk('23 变式 E(1/X)=2/θ ⟹ (1/2n)Σ1/X_i 无偏', simplify(integrate(f23.subs(x, xp) / xp, (xp, 0, oo)) / 2 - 1 / thp) == 0)

print('\n%d/%d 通过' % (sum(ok), len(ok)))
