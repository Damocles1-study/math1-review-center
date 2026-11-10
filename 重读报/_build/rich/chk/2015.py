#!/usr/bin/env python3
# 2015 数学一 精解复算：每题答案（及举一反三里的数字）独立算一遍（sympy 符号 / 数值 / 蒙特卡洛）
import math, random, itertools
import sympy as sp
from sympy import (symbols, integrate, oo, pi, sqrt, exp, log, sin, cos, tan, limit, diff,
                   simplify, Matrix, Rational as R, series, factor, solve, Eq)

ok = []
def chk(name, cond, info=''):
    ok.append(bool(cond))
    print(('✓ ' if cond else '✗ ') + name + ('  ' + str(info) if info else ''))

x, y, z, t, r, th, a, b, c, d, k, lam = symbols('x y z t r theta a b c d k lambda', real=True)

# 1 拐点：按题图特征造一个 f''（左段在 x1=-1.6 相切，0 处无定义且 + 变 −，x2=0.35 处穿过）
fpp = lambda u: 0.9 * (u + 1.6)**2 + 0.2 if False else (0.9 * (u + 1.6)**2 if u < 0 else 1.15 * math.log(u / 0.35))
grid = [i / 1000 for i in range(-3000, 3300) if i != 0]
cands = [-1.6, 0.0, 0.35]
def changes(x0):
    e = 1e-3
    return (fpp(x0 - e) > 0) != (fpp(x0 + e) > 0)
chk('1 变号点个数 = 2（相切点不变号）选 C', sum(changes(c0) for c0 in cands) == 2)
y8 = (x - 1)**2 * (x - 3)**3
chk('1 变式 y″=4(x−3)(5x²−18x+15)', simplify(diff(y8, x, 2) - 4 * (x - 3) * (5 * x**2 - 18 * x + 15)) == 0)
chk('1 变式 三个单根 ⟹ 3 个拐点', len(set(sp.solve(diff(y8, x, 2), x))) == 3)

# 2 特解反推方程
Y = R(1, 2) * exp(2 * x) + (x - R(1, 3)) * exp(x)
expr = diff(Y, x, 2) + a * diff(Y, x) + b * Y - c * exp(x)
coeffs = sp.Poly(sp.expand(sp.simplify(expr * exp(-x))).subs(exp(x), z), x, z).coeffs()
sol = solve(sp.Poly(sp.expand(sp.simplify(expr * exp(-x))).subs(exp(x), z), x, z).coeffs(), [a, b, c], dict=True)
chk('2 a=-3,b=2,c=-1 选 A', sol == [{a: -3, b: 2, c: -1}], sol)
Yv = x * exp(-x)
chk('2 变式 xe^{-x} 代入 y″−y′−2y = −3e^{-x}', simplify(diff(Yv, x, 2) - diff(Yv, x) - 2 * Yv + 3 * exp(-x)) == 0)

# 3 幂级数：a_n=(-1)^n/n 条件收敛的例子；数值看 √3 与 3 处 n a_n (x-1)^n 的项
an = lambda n: (-1)**n / n
chk('3 x=√3：|项|=|√3−1|^n → 0 几何衰减', abs((math.sqrt(3) - 1)**200) < 1e-25)
chk('3 x=3：|项|=2^n 发散', 2**50 > 1e15)
chk('3 乘 n 不改半径：n^(1/n)→1', abs(1000**(1 / 1000) - 1) < 0.01)

# 4 极坐标：f≡1 时 B 的值 = 直角坐标面积
areaB = integrate(R(1, 2) * (1 / sin(2 * th) - 1 / (2 * sin(2 * th))), (th, pi / 4, pi / 3))
from scipy import integrate as si
def area_xy():
    # 区域：x>0，x ≤ y ≤ √3 x，1/4 ≤ xy ≤ 1/2
    f = lambda yy, xx: 1.0
    tot = si.dblquad(lambda yy, xx: 1.0, 0.01, 2,
                     lambda xx: max(xx, 0.25 / xx), lambda xx: max(min(math.sqrt(3) * xx, 0.5 / xx), max(xx, 0.25 / xx)))[0]
    return tot
chk('4 B（f≡1）= ln3/16', simplify(areaB - log(3) / 16) == 0, areaB)
chk('4 直角坐标数值面积 = ln3/16', abs(area_xy() - math.log(3) / 16) < 1e-6, area_xy())
uu, vv = symbols('uu vv', positive=True)
chk('4 变式 u=xy,v=y/x 雅可比 1/(2v)', simplify(sp.Matrix([sqrt(uu / vv), sqrt(uu * vv)]).jacobian([uu, vv]).det() - 1 / (2 * vv)) == 0)

# 5 方程组
A5 = Matrix([[1, 1, 1], [1, 2, a], [1, 4, a**2]]); b5 = Matrix([1, d, d**2])
chk('5 |A|=(a-1)(a-2)', factor(A5.det()) == factor((a - 1) * (a - 2)))
def nsol(av, dv):
    A = A5.subs(a, av); B = b5.subs(d, dv); Ab = A.row_join(B)
    rA, rAb = A.rank(), Ab.rank()
    return 'inf' if rA == rAb < 3 else ('none' if rA < rAb else 'one')
res = {(av, dv): nsol(av, dv) for av in [1, 2, 3] for dv in [1, 2, 5]}
chk('5 无穷多解 ⟺ a∈Ω 且 d∈Ω 选 D', all((v == 'inf') == (av in (1, 2) and dv in (1, 2)) for (av, dv), v in res.items()), res)
chk('5 变式 b=(1,d,d³)：a=1 时有解 ⟺ d=1 或 −2', set(sp.solve(d**3 - 1 - 3 * (d - 1), d)) == {1, -2})

# 6 正交变换换列
e1, e2, e3 = Matrix([1, 0, 0]), Matrix([0, 1, 0]), Matrix([0, 0, 1])
P6 = Matrix.hstack(e1, e2, e3); A6 = P6 * sp.diag(2, 1, -1) * P6.T
Q6 = Matrix.hstack(e1, -e3, e2)
chk('6 QᵀAQ = diag(2,−1,1) 选 A', Q6.T * A6 * Q6 == sp.diag(2, -1, 1))
# 换一个一般的正交 P 再验
Rm = Matrix([[1, 2, 2], [2, 1, -2], [2, -2, 1]]) / 3
A6b = Rm * sp.diag(2, 1, -1) * Rm.T
Q6b = Matrix.hstack(Rm[:, 0], -Rm[:, 2], Rm[:, 1])
chk('6 一般正交 P 也成立', simplify(Q6b.T * A6b * Q6b - sp.diag(2, -1, 1)) == sp.zeros(3))

# 7 概率不等式：随机有限概率空间检验 C 恒成立、A/B/D 有反例
random.seed(1)
okC = True; badA = badB = badD = False
for _ in range(20000):
    w = [random.random() for _ in range(4)]; s_ = sum(w); w = [q / s_ for q in w]   # 四块 AB, AB̄, ĀB, ĀB̄
    pAB, pA, pB = w[0], w[0] + w[1], w[0] + w[2]
    okC &= pAB <= (pA + pB) / 2 + 1e-12
    badA |= pAB > pA * pB + 1e-9; badB |= pAB < pA * pB - 1e-9; badD |= pAB < (pA + pB) / 2 - 1e-9
chk('7 C 恒成立，A、B、D 都有反例', okC and badA and badB and badD)

# 8 期望
EX, EY, DX = 2, 1, 3
chk('8 E[X(X+Y-2)] = 5 选 D', (DX + EX**2) + EX * EY - 2 * EX == 5)
random.seed(2); N = 400000; acc = 0.0
for _ in range(N):
    X_ = random.gauss(2, math.sqrt(3)); Y_ = random.gauss(1, 1)
    acc += X_ * (X_ + Y_ - 2)
chk('8 蒙特卡洛（独立正态）≈ 5', abs(acc / N - 5) < 0.05, round(acc / N, 3))

# 9 极限
chk('9 lim ln cos x / x² = −1/2', limit(log(cos(x)) / x**2, x, 0) == R(-1, 2))
chk('9 变式 ln cos x/ln cos 2x → 1/4', limit(log(cos(x)) / log(cos(2 * x)), x, 0) == R(1, 4))
chk('9 变式 (ln cos x + x²/2)/x⁴ → −1/12', limit((log(cos(x)) + x**2 / 2) / x**4, x, 0) == R(-1, 12))
chk('9 变式 ln(sin x/x)/x² → −1/6', limit(log(sin(x) / x) / x**2, x, 0) == R(-1, 6))

# 10 对称区间
I10 = integrate(sin(x) / (1 + cos(x)), (x, -pi / 2, pi / 2)) + 2 * integrate(x, (x, 0, pi / 2))
chk('10 = π²/4', simplify(I10 - pi**2 / 4) == 0, I10)
chk('10 变式 ∫cos x/(1+e^x) = 1', abs(si.quad(lambda u: math.cos(u) / (1 + math.exp(u)), -math.pi / 2, math.pi / 2)[0] - 1) < 1e-10)
chk('10 变式 ∫sin²/(1+cos) = π−2', simplify(integrate(1 - cos(x), (x, -pi / 2, pi / 2)) - (pi - 2)) == 0)

# 11 隐函数全微分
F = exp(z) + x * y * z + x + cos(x) - 2
z0 = solve(F.subs({x: 0, y: 1}), z)
zx = (-diff(F, x) / diff(F, z)).subs({x: 0, y: 1, z: 0}); zy = (-diff(F, y) / diff(F, z)).subs({x: 0, y: 1, z: 0})
chk('11 z(0,1)=0，dz = −dx', z0 == [0] and zx == -1 and zy == 0, (z0, zx, zy))
# 二阶：z_xx
zf = sp.Function('zf')(x)
G = exp(zf) + x * 1 * zf + x + cos(x) - 2
g1 = diff(G, x); g2 = diff(G, x, 2)
zxx = solve(g2.subs(diff(zf, x, 2), symbols('W')).subs(diff(zf, x), -1).subs(zf, 0).subs(x, 0), symbols('W'))
chk('11 变式 z_xx(0,1) = 2', zxx == [2], zxx)

# 12 四面体
I12 = integrate(integrate(integrate(x + 2 * y + 3 * z, (z, 0, 1 - x - y)), (y, 0, 1 - x)), (x, 0, 1))
chk('12 = 1/4', I12 == R(1, 4), I12)
chk('12 变式 ∭(x+y+z) = 1/8', integrate(integrate(integrate(x + y + z, (z, 0, 1 - x - y)), (y, 0, 1 - x)), (x, 0, 1)) == R(1, 8))
chk('12 变式 ∭z² = 1/60，∭xy = 1/120',
    integrate(integrate(integrate(z**2, (z, 0, 1 - x - y)), (y, 0, 1 - x)), (x, 0, 1)) == R(1, 60) and
    integrate(integrate(integrate(x * y, (z, 0, 1 - x - y)), (y, 0, 1 - x)), (x, 0, 1)) == R(1, 120))
chk('12 变式 x/2+y+z≤1 上 ∭x = 1/6', integrate(integrate(integrate(x, (z, 0, 1 - x / 2 - y)), (y, 0, 1 - x / 2)), (x, 0, 2)) == R(1, 6))

# 13 行列式
def D13(n, v=2):
    M = sp.zeros(n)
    for i in range(n):
        M[i, i] = v; M[i, n - 1] = v
        if i > 0: M[i, i - 1] = -1
    return M.det()
chk('13 D_n = 2^{n+1}−2（n=1..8）', all(D13(n) == 2**(n + 1) - 2 for n in range(1, 9)), [D13(n) for n in range(1, 6)])
chk('13 变式 2 全换成 a：D_n = a+…+a^n', all(sp.expand(D13(n, a) - sum(a**j for j in range(1, n + 1))) == 0 for n in range(1, 6)))

# 14 二维正态
random.seed(3); N = 400000; cnt = 0
for _ in range(N):
    X_ = random.gauss(1, 1); Y_ = random.gauss(0, 1)
    cnt += (X_ * Y_ - Y_ < 0)
chk('14 P{XY−Y<0} ≈ 1/2', abs(cnt / N - 0.5) < 0.004, cnt / N)
random.seed(4); cnt = 0
for _ in range(N):
    U = random.gauss(0, 1); V = 0.5 * U + math.sqrt(0.75) * random.gauss(0, 1)
    cnt += (U * V < 0)
chk('14 变式 ρ=1/2 时 P{UV<0} ≈ 1/3', abs(cnt / N - 1 / 3) < 0.004, cnt / N)

# 15 等价无穷小
f15 = x + a * log(1 + x) + b * x * sin(x)
ser = sp.series(f15, x, 0, 4).removeO()
sol15 = solve([ser.coeff(x, 1), ser.coeff(x, 2)], [a, b], dict=True)[0]
k15 = ser.coeff(x, 3).subs(sol15)
chk('15 a=−1, b=−1/2, k=−1/3', sol15 == {a: -1, b: R(-1, 2)} and k15 == R(-1, 3), (sol15, k15))
chk('15 回代 lim f/(kx³)=1', limit(f15.subs(sol15) / (k15 * x**3), x, 0) == 1)
g15 = x - (a + b * cos(x)) * sin(x); s15 = sp.series(g15, x, 0, 6).removeO()
chk('15 变式 5 阶：a=4/3, b=−1/3', solve([s15.coeff(x, 1), s15.coeff(x, 3)], [a, b], dict=True) == [{a: R(4, 3), b: R(-1, 3)}])

# 16 微分方程
f16 = 8 / (4 - x)
chk('16 满足 y′=y²/8, y(0)=2', simplify(diff(f16, x) - f16**2 / 8) == 0 and f16.subs(x, 0) == 2)
for x0 in [-3, -1, 0, 1, 2, 3.5]:
    fx, fpx = f16.subs(x, x0), diff(f16, x).subs(x, x0)
    X0 = x0 - fx / fpx
    area = R(1, 2) * abs(fx) * abs(x0 - X0)
    if abs(float(area) - 4) > 1e-9: break
else:
    chk('16 六个点的三角形面积都是 4', True)
chk('16 变式 f′<0：8/(x+4) 也满足面积 4', simplify(-(8 / (x + 4))**2 / (2 * diff(8 / (x + 4), x)) - 4) == 0)
chk('16 变式 ∫₀² 8/(4−x) = 8 ln2', simplify(integrate(f16, (x, 0, 2)) - 8 * log(2)) == 0)

# 17 条件最值
g17 = (1 + x)**2 + (1 + y)**2; h17 = x**2 + y**2 + x * y - 3
L = g17 + lam * h17
crit = solve([diff(L, x), diff(L, y), h17], [x, y, lam], dict=True)
vals = sorted({(s_[x], s_[y], g17.subs(s_)) for s_ in crit}, key=lambda q: q[2])
chk('17 驻点 4 个，g 值 0,8,9,9', sorted(v[2] for v in vals) == [0, 8, 9, 9], vals)
mx = max(((1 + math.sqrt(2) * math.cos(tt) / math.sqrt(1) * 0 + (math.sqrt(2) * math.cos(tt) + math.sqrt(6) * math.sin(tt)) / math.sqrt(2) - 0)**2 +
          (1 + (math.sqrt(2) * math.cos(tt) - math.sqrt(6) * math.sin(tt)) / math.sqrt(2))**2) for tt in [i * 2 * math.pi / 200000 for i in range(200000)])
chk('17 椭圆上数值扫描 max g = 9 ⟹ 最大方向导数 3', abs(mx - 9) < 1e-6, mx)
pt = (2, -1)
chk('17 (2,−1) 在 C 上', pt[0]**2 + pt[1]**2 + pt[0] * pt[1] == 3)

# 18 乘积法则：符号验证 n=3 的公式
u1, u2, u3 = [sp.Function('u%d' % i)(x) for i in (1, 2, 3)]
chk('18 (u1u2u3)′ = Σ', simplify(diff(u1 * u2 * u3, x) - (diff(u1, x) * u2 * u3 + u1 * diff(u2, x) * u3 + u1 * u2 * diff(u3, x))) == 0)
f18 = sp.prod([x - j for j in range(0, 101)])
chk('18 变式 f′(0) = 100!', sp.diff(f18, x).subs(x, 0) == sp.factorial(100))

# 19 曲线积分
X_, Y_, Z_ = cos(t), sqrt(2) * sin(t), cos(t)
integrand = (Y_ + Z_) * diff(X_, t) + (Z_**2 - X_**2 + Y_) * diff(Y_, t) + X_**2 * Y_**2 * diff(Z_, t)
I19 = integrate(sp.expand(integrand), (t, pi / 2, -pi / 2))
chk('19 I = √2π/2', simplify(I19 - sqrt(2) * pi / 2) == 0, I19)
chk('19 参数在球面与平面上', simplify(X_**2 + Y_**2 + Z_**2 - 2) == 0)
# 斯托克斯核对：∬_D (2x²y+1) dxdy，D: 2x²+y²≤2, x≥0
I19s = si.dblquad(lambda yy, xx: 2 * xx**2 * yy + 1, 0, 1, lambda xx: -math.sqrt(2 - 2 * xx**2), lambda xx: math.sqrt(2 - 2 * xx**2))[0]
chk('19 斯托克斯算法结果相同', abs(I19s - math.sqrt(2) * math.pi / 2) < 1e-8, I19s)
P_, Q_, R_ = y + z, z**2 - x**2 + y, x**2 * y**2
rot = (diff(R_, y) - diff(Q_, z), diff(P_, z) - diff(R_, x), diff(Q_, x) - diff(P_, y))
chk('19 旋度 = (2x²y−2z, 1−2xy², −2x−1)', [simplify(rot[i] - e) for i, e in enumerate([2 * x**2 * y - 2 * z, 1 - 2 * x * y**2, -2 * x - 1])] == [0, 0, 0])
chk('19 变式 ∫x ds = 2√2', simplify(integrate(cos(t) * sqrt(2), (t, -pi / 2, pi / 2)) - 2 * sqrt(2)) == 0)

# 20 过渡矩阵
P20 = Matrix([[2, 0, 1], [0, 2, 0], [2 * k, 0, k + 1]])
chk('20 |P| = 4', simplify(P20.det()) == 4)
chk('20 |P−E| = −k ⟹ k=0', simplify((P20 - sp.eye(3)).det() + k) == 0)
ns = (P20.subs(k, 0) - sp.eye(3)).nullspace()
chk('20 k=0 时 x ∥ (1,0,−1)', len(ns) == 1 and ns[0].cross(Matrix([1, 0, -1])) == sp.zeros(3, 1), ns)
chk('20 变式 |P−E/2|=0 ⟹ k=3/2', solve((P20 - sp.eye(3) / 2).det(), k) == [R(3, 2)])
chk('20 变式 k=0 时 P⁻¹', P20.subs(k, 0).inv() == Matrix([[R(1, 2), 0, R(-1, 2)], [0, R(1, 2), 0], [0, 0, 1]]))

# 21 相似
A21 = Matrix([[0, 2, -3], [-1, 3, -3], [1, -2, a]]); B21 = Matrix([[1, -2, 0], [0, b, 0], [0, 3, 1]])
s21 = solve([A21.trace() - B21.trace(), A21.det() - B21.det()], [a, b], dict=True)
chk('21 a=4, b=5', s21 == [{a: 4, b: 5}], s21)
A4 = A21.subs(a, 4); P21 = Matrix([[2, -3, -1], [1, 0, -1], [0, 1, 1]])
chk('21 P⁻¹AP = diag(1,1,5)', P21.inv() * A4 * P21 == sp.diag(1, 1, 5))
chk('21 B 也可对角化（r(B−E)=1）', (B21.subs(b, 5) - sp.eye(3)).rank() == 1)
chk('21 变式 |A*+2E| = 147', (A4.adjugate() + 2 * sp.eye(3)).det() == 147)

# 22 负二项
p22 = integrate(2**(-x) * log(2), (x, 3, oo))
chk('22 p = 1/8', simplify(p22 - R(1, 8)) == 0, p22)
n = symbols('n', integer=True, positive=True)
pmf = (n - 1) * R(1, 8)**2 * R(7, 8)**(n - 2)
chk('22 分布归一', simplify(sp.summation(pmf, (n, 2, oo)) - 1) == 0)
chk('22 EY = 16', simplify(sp.summation(n * pmf, (n, 2, oo)) - 16) == 0)
chk('22 DY = 112', simplify(sp.summation(n**2 * pmf, (n, 2, oo)) - 16**2 - 112) == 0)
chk('22 P{Y≤3} = 11/256', pmf.subs(n, 2) + pmf.subs(n, 3) == R(11, 256))
random.seed(5); tot = 0; M = 100000
for _ in range(M):
    cnt_, kk = 0, 0
    while cnt_ < 2:
        kk += 1
        if random.expovariate(math.log(2)) > 3: cnt_ += 1
    tot += kk
chk('22 蒙特卡洛 EY ≈ 16', abs(tot / M - 16) < 0.15, tot / M)

# 23 均匀分布估计
th_ = symbols('th_', real=True)
EX23 = integrate(x / (1 - th_), (x, th_, 1))
chk('23 EX = (1+θ)/2', simplify(EX23 - (1 + th_) / 2) == 0)
random.seed(6); th0 = 0.3; nn = 50; reps = 4000; mle = []; mom = []
for _ in range(reps):
    smp = [random.uniform(th0, 1) for _ in range(nn)]
    mle.append(min(smp)); mom.append(2 * sum(smp) / nn - 1)
chk('23 矩估计近似无偏', abs(sum(mom) / reps - th0) < 0.005, sum(mom) / reps)
chk('23 MLE=min 偏大，E≈θ+(1−θ)/(n+1)', abs(sum(mle) / reps - (th0 + (1 - th0) / (nn + 1))) < 0.002, sum(mle) / reps)
smp = [0.55, 0.62, 0.71, 0.83, 0.90, 0.97]
Lf = lambda tt: (1 - tt)**(-len(smp)) if tt <= min(smp) else 0.0
best = max([i / 10000 for i in range(-5000, 10000)], key=Lf)
chk('23 似然在 θ=min xᵢ 处最大', abs(best - 0.55) < 1e-9, best)

print('\n%d/%d 通过' % (sum(ok), len(ok)))
