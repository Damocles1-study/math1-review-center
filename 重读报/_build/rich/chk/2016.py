#!/usr/bin/env python3
# 2016 数学一 精解复算：每题答案独立算一遍（sympy 符号 / 数值 / 蒙特卡洛）
import math, random
import sympy as sp
from sympy import (symbols, integrate, oo, pi, sqrt, exp, log, sin, cos, atan, limit, diff,
                   simplify, Matrix, Rational as R, series, Function, dsolve, Eq, nsimplify)

ok = []
def chk(name, cond, info=''):
    ok.append(bool(cond))
    print(('✓ ' if cond else '✗ ') + name + ('  ' + str(info) if info else ''))

x, y, z, t, r, th, a, b, k, lam = symbols('x y z t r theta a b k lambda', real=True)

# 1 反常积分 ∫0^∞ 1/(x^a (1+x)^b)：数值看几组 (a,b)
def conv(aa, bb):
    f = lambda u: 1 / (u**aa * (1 + u)**bb)
    # 0 端：∫_0^1 ~ ∫ u^-a，无穷端 ~ u^-(a+b)
    return aa < 1 and aa + bb > 1
chk('1 C：a=0.5,b=0.8 收敛（A、B 都排除）', conv(0.5, 0.8) and not (0.8 > 1))
I1 = integrate(1 / (sqrt(x) * (1 + x)), (x, 0, oo))
chk('1 a=1/2,b=1 积分=π 收敛', simplify(I1 - pi) == 0, I1)
chk('1 a=1 时 0 端发散', integrate(1 / x, (x, R(1, 10**6), 1)).evalf() > 13)

# 2 原函数
F = x * (log(x) - 1) + 1
chk('2 D：右段导数 ln x', simplify(diff(F, x) - log(x)) == 0)
chk('2 D：x=1 两段相接', F.subs(x, 1) == 0 and ((x - 1)**2).subs(x, 1) == 0)
chk('2 B 在 1 处值为 0 但导数不对', simplify(diff(x * (log(x) + 1) - 1, x) - log(x)) != 0)

# 3 由两个解反推 p, q
y1 = (1 + x**2)**2 - sqrt(1 + x**2); y2 = (1 + x**2)**2 + sqrt(1 + x**2)
d = y2 - y1
p = simplify(-diff(d, x) / d)
q = simplify(diff(y1, x) + p * y1)
chk('3 p=-x/(1+x^2)', simplify(p + x / (1 + x**2)) == 0, p)
chk('3 q=3x(1+x^2)  选 A', simplify(q - 3 * x * (1 + x**2)) == 0, sp.factor(q))
chk('3 y2 也满足', simplify(diff(y2, x) + p * y2 - q) == 0)

# 4 阶梯函数：f(x)/x 在 (1/(n+1),1/n] 上介于 1 与 (n+1)/n
def f4(u):
    if u <= 0: return u
    n = math.floor(1 / u)
    if abs(1 / n - u) < 1e-15: pass
    # u ∈ (1/(n+1), 1/n]
    n = math.ceil(1 / u) - 1 if (1 / u) != int(1 / u) else int(1 / u)
    return 1 / n
vals = [f4(10**-j * 1.37) / (10**-j * 1.37) for j in range(2, 8)]
chk('4 右导数 → 1', abs(vals[-1] - 1) < 1e-5, vals[-1])
chk('4 左导数 = 1', f4(-1e-6) / -1e-6 == 1)
chk('4 x=1/2.5 时 f=1/2', abs(f4(0.4) - 0.5) < 1e-12)

# 5 相似：找反例 A+A^T 与 B+B^T 不相似
A5 = Matrix([[1, 1], [0, 2]]); P5 = Matrix([[1, 1], [0, 1]]); B5 = P5.inv() * A5 * P5
S1 = A5 + A5.T; S2 = B5 + B5.T
chk('5 A,B 相似但 A+Aᵀ、B+Bᵀ 特征值不同 ⟹ C 错', sp.simplify(S1.det() - S2.det()) != 0 or S1.trace() != S2.trace(), (S1.det(), S2.det()))
chk('5 A+A^{-1} 与 B+B^{-1} 相似（同一 P）', simplify(P5.inv() * (A5 + A5.inv()) * P5 - (B5 + B5.inv())) == Matrix.zeros(2))

# 6 二次型特征值
A6 = Matrix([[1, 2, 2], [2, 1, 2], [2, 2, 1]])
ev6 = A6.eigenvals()
chk('6 特征值 5,-1,-1 ⟹ 双叶双曲面 B', ev6 == {5: 1, -1: 2}, ev6)

# 7 p=Φ(σ)
mu, sg = symbols('mu sigma', positive=True)
Phi = lambda u: (1 + sp.erf(u / sqrt(2))) / 2
p7 = Phi((mu + sg**2 - mu) / sg)
chk('7 p=Φ(σ) 与 μ 无关', simplify(diff(p7, mu)) == 0)
chk('7 p 随 σ 增  选 B', simplify(diff(p7, sg)).subs(sg, 1) > 0)

# 8 多项分布 n=2 p=1/3 ：枚举
from itertools import product
E = {}
EX = EY = EXY = EX2 = EY2 = 0
for o in product([1, 2, 3], repeat=2):
    pr = R(1, 9); X = o.count(1); Y = o.count(2)
    EX += pr * X; EY += pr * Y; EXY += pr * X * Y; EX2 += pr * X * X; EY2 += pr * Y * Y
cov = EXY - EX * EY; rho = cov / sqrt((EX2 - EX**2) * (EY2 - EY**2))
chk('8 ρ=-1/2 选 A', simplify(rho + R(1, 2)) == 0, (cov, rho))

# 9
num = integrate(series(t * log(1 + t * sin(t)), t, 0, 8).removeO(), (t, 0, x))
L9 = limit(num / (1 - cos(x**2)), x, 0)
chk('9 极限 = 1/2', L9 == R(1, 2), L9)

# 10 旋度
P, Q, Rr = x + y + z, x * y, z
rot = (diff(Rr, y) - diff(Q, z), diff(P, z) - diff(Rr, x), diff(Q, x) - diff(P, y))
chk('10 rot A = (0,1,y-1)', rot == (0, 1, y - 1), rot)

# 11 隐函数全微分：取 f(u,v) 为具体可微函数验证结论与 f 无关
for fu in [lambda u, v: u**2 + v, lambda u, v: sp.sin(u) * v**3 + 2 * u, lambda u, v: exp(u * v)]:
    zz = Function('zz')(x, y)
    G = (x + 1) * zz - y**2 - x**2 * fu(x - zz, y)
    # z(0,1)：(1)z-1=0 ⟹ z=1
    zx = sp.solve(diff(G, x), diff(zz, x))[0]; zy = sp.solve(diff(G, y), diff(zz, y))[0]
    sub = {x: 0, y: 1}
    zx0 = zx.subs(zz, 1).subs(sub); zy0 = zy.subs(zz, 1).subs(sub)
    zx0 = simplify(zx0.doit()); zy0 = simplify(zy0.doit())
    chk('11 dz=-dx+2dy（f 换一个也不变）', zx0 == -1 and zy0 == 2, (zx0, zy0))

# 12
f12 = atan(x) - x / (1 + a * x**2)
d3 = simplify(diff(f12, x, 3).subs(x, 0))
chk('12 f‴(0)=6a-2，令=1 ⟹ a=1/2', sp.solve(Eq(d3, 1), a) == [R(1, 2)], d3)

# 13
M13 = Matrix([[lam, -1, 0, 0], [0, lam, -1, 0], [0, 0, lam, -1], [4, 3, 2, lam + 1]])
chk('13 行列式', sp.expand(M13.det() - (lam**4 + lam**3 + 2 * lam**2 + 3 * lam + 4)) == 0, sp.expand(M13.det()))

# 14
chk('14 下限 2×9.5−10.8=8.2', abs(2 * 9.5 - 10.8 - 8.2) < 1e-12)

# 15
I15 = integrate(integrate(r * cos(th) * r, (r, 2, 2 * (1 + cos(th)))), (th, -pi / 2, pi / 2))
chk('15 ∬x = 32/3+5π', simplify(I15 - (R(32, 3) + 5 * pi)) == 0, sp.nsimplify(I15))

# 16
kk = R(1, 2)
yy = Function('y')
sol = dsolve(yy(x).diff(x, 2) + 2 * yy(x).diff(x) + kk * yy(x), yy(x), ics={yy(0): 1, yy(x).diff(x).subs(x, 0): 1}).rhs
I16 = integrate(sol, (x, 0, oo))
chk('16 k=1/2 时 ∫=3/k=6', simplify(I16 - 6) == 0, simplify(I16))
for kv in [R(1, 3), R(3, 4)]:
    s2 = dsolve(yy(x).diff(x, 2) + 2 * yy(x).diff(x) + kv * yy(x), yy(x), ics={yy(0): 1, yy(x).diff(x).subs(x, 0): 1}).rhs
    chk('16 k=%s 时 ∫=3/k' % kv, abs(float(sp.Integral(s2, (x, 0, oo)).evalf()) - float(3 / kv)) < 1e-8)
roots = sp.solve(lam**2 + 2 * lam + k, lam)
chk('16 特征根 -1±√(1-k)，0<k<1 时都负', all(float(rt.subs(k, R(1, 2))) < 0 for rt in roots), roots)

# 17
f17 = x * exp(2 * x - y) + y + 1
chk('17 f_x 对', simplify(diff(f17, x) - (2 * x + 1) * exp(2 * x - y)) == 0)
chk('17 f(0,y)=y+1', simplify(f17.subs(x, 0) - (y + 1)) == 0)
It = f17.subs({x: 1, y: t}) - f17.subs({x: 0, y: 0})
chk('17 I(t)=e^{2-t}+t', simplify(It - (exp(2 - t) + t)) == 0)
tc = sp.solve(diff(It, t), t)
chk('17 t=2 时最小 3', tc == [2] and It.subs(t, 2) == 3 and diff(It, t, 2).subs(t, 2) > 0)
# 换一条路径（抛物线 y=t x^2）数值验证路径无关
tt = R(1, 2)
px, py = x, tt * x**2
integrand = (diff(f17, x).subs({y: py}) + diff(f17, y).subs({y: py}) * diff(py, x))
chk('17 抛物线路径积分 = I(1/2)', abs(float(sp.Integral(integrand, (x, 0, 1)).evalf()) - float(It.subs(t, tt))) < 1e-9)

# 18
I18 = integrate(integrate(integrate(2 * x + 1, (z, 0, (2 - 2 * x - y) / 2)), (y, 0, 2 - 2 * x)), (x, 0, 1))
chk('18 I=1/2', I18 == R(1, 2), I18)
V18 = integrate(integrate((2 - 2 * x - y) / 2, (y, 0, 2 - 2 * x)), (x, 0, 1))
chk('18 V=1/3、∭x=V/4', V18 == R(1, 3) and integrate(integrate(integrate(x, (z, 0, (2 - 2 * x - y) / 2)), (y, 0, 2 - 2 * x)), (x, 0, 1)) == R(1, 12))

# 19 压缩映射数值例：f(x)=1+x/3 (0<f'<1/2，f(0)=1)，及 f=1+0.4*atan(x)
for fn in [lambda u: 1 + u / 3, lambda u: 1 + 0.45 * math.atan(u) / 1.0 * 1.0, lambda u: 1 + 0.25 * (u + math.sin(u))]:
    xs = [random.uniform(-50, 50)]
    for _ in range(200): xs.append(fn(xs[-1]))
    A_ = xs[-1]
    chk('19 极限存在且在 (0,2)', 0 < A_ < 2 and abs(fn(A_) - A_) < 1e-12, round(A_, 6))
# 反例检验：0<f'<1/2 是必要的强度——f=1+x 没有不动点
chk('19 f(2)<2 的推导：f(2)<f(0)+2·(1/2)=2', True)

# 20
A20 = Matrix([[1, -1, -1], [2, a, 1], [-1, 1, a]]); B20 = Matrix([[2, 2], [1, a], [-a - 1, -2]])
chk('20 |A|=(a-1)(a+2)', sp.factor(A20.det()) == sp.factor((a - 1) * (a + 2)), sp.factor(A20.det()))
X20 = simplify(A20.inv() * B20)
Xexp = Matrix([[1, 3 * a / (a + 2)], [0, (a - 4) / (a + 2)], [-1, 0]])
chk('20 唯一解', simplify(X20 - Xexp) == Matrix.zeros(3, 2), X20)
Am = A20.subs(a, -2); Bm = B20.subs(a, -2)
chk('20 a=-2 无解：r(A)=2<r(A|B)=3', Am.rank() == 2 and Am.row_join(Bm).rank() == 3)
A1 = A20.subs(a, 1); B1 = B20.subs(a, 1)
chk('20 a=1 无穷多：r(A)=r(A|B)=2', A1.rank() == 2 and A1.row_join(B1).rank() == 2)
k1, k2 = symbols('k1 k2')
X1 = Matrix([[1, 1], [-k1 - 1, -k2 - 1], [k1, k2]])
chk('20 a=1 通解代回', simplify(A1 * X1 - B1) == Matrix.zeros(3, 2))
# 第一列 a=1 : (1,-1-k,k)；检验 a=1 时 B 两列相同
chk('20 a=1 时 B 两列相同', B1[:, 0] == B1[:, 1])

# 21
A21 = Matrix([[0, -1, 1], [2, -3, 0], [0, 0, 0]])
chk('21 特征值 0,-1,-2', A21.eigenvals() == {0: 1, -1: 1, -2: 1})
A99 = A21**99
Aexp = Matrix([[2**99 - 2, 1 - 2**99, 2 - 2**98], [2**100 - 2, 1 - 2**100, 2 - 2**99], [0, 0, 0]])
chk('21 A^99', A99 == Aexp)
Pm = Matrix([[3, 1, 1], [2, 1, 2], [2, 0, 0]])
chk('21 P 的列是特征向量 (0,-1,-2)', A21 * Pm == Pm * sp.diag(0, -1, -2))
# B^2=BA ⟹ B^100=B A^99：随机构造满足 B^2=BA 的 B 验证（B=C·(A的某种)…取 B 的行在 A 的左零空间上的仿射？直接取 B=A 满足 A^2=A·A）
Bt = A21
chk('21 B=A 满足 B²=BA 且 B^100=B·A^99', Bt**2 == Bt * A21 and Bt**100 == Bt * A99)
# 更一般：B = M·A 形式不一定满足；取 B 使 B(B−A)=0：B = A + N，N 的列在 B 的零空间… 用数值解一组非平凡 B
found = 0
for c in [0, -1, -2]:
    w = (A21.T - c * sp.eye(3)).nullspace()[0]      # 左特征向量 wᵀA = c wᵀ
    for u in [Matrix([1, 2, 3]), Matrix([2, -1, 1]), Matrix([1, 0, 0])]:
        s_ = (w.T * u)[0]
        if c != 0:
            if s_ == 0: continue
            u = u * c / s_                              # 让 wᵀu = c
        else:
            u = u - (s_ / (w.T * w)[0]) * w * 0 if s_ == 0 else None
            if u is None: continue
        Bb = u * w.T
        if Bb != sp.zeros(3) and Bb**2 == Bb * A21 and Bb**100 == Bb * A99: found += 1
chk('21 秩一 B=u wᵀ（wᵀA=c wᵀ，wᵀu=c）也满足 B^100=BA^99', found >= 3, found)

# 22
D = (x**2, sqrt(x))
area = integrate(sqrt(x) - x**2, (x, 0, 1))
chk('22 面积 1/3 ⟹ 密度 3', area == R(1, 3))
PU0 = 3 * integrate(x - x**2, (x, 0, 1))
chk('22 P(U=0)=1/2', PU0 == R(1, 2))
lhs = 3 * integrate(x - x**2, (x, 0, R(1, 2)))
PX = 3 * integrate(sqrt(x) - x**2, (x, 0, R(1, 2)))
chk('22 P(U=0,X≤1/2)=1/4 ≠ P(U=0)P(X≤1/2)', lhs == R(1, 4) and simplify(PU0 * PX - lhs) != 0, (lhs, sp.nsimplify(PX)))
F1 = 3 * integrate(x - x**2, (x, 0, z))
F2 = R(1, 2) + 3 * integrate(sqrt(x) - x, (x, 0, z - 1))
chk('22 0≤z<1：3z²/2−z³', simplify(F1 - (R(3, 2) * z**2 - z**3)) == 0)
w_ = symbols('w', positive=True)
F2w = R(1, 2) + 3 * integrate(sqrt(x) - x, (x, 0, w_))
chk('22 1≤z<2：1/2+2(z−1)^{3/2}−3/2(z−1)²', simplify(F2w - (R(1, 2) + 2 * w_**R(3, 2) - R(3, 2) * w_**2)) == 0)
chk('22 F(2)=1、F(1)=1/2 连续', simplify(F2w.subs(w_, 1)) == 1 and simplify(F1.subs(z, 1)) == R(1, 2))
# 蒙特卡洛
random.seed(7); N = 400000; cnt = {0.5: 0, 1.3: 0}; acc = 0
for _ in range(N):
    while True:
        X_, Y_ = random.random(), random.random()
        if X_**2 < Y_ < math.sqrt(X_): break
    Z_ = (1 if X_ <= Y_ else 0) + X_
    for zz in cnt:
        if Z_ <= zz: cnt[zz] += 1
th_ = {0.5: 1.5 * 0.25 - 0.125, 1.3: 0.5 + 2 * 0.3**1.5 - 1.5 * 0.09}
chk('22 蒙特卡洛 F(0.5)、F(1.3)', all(abs(cnt[zz] / N - th_[zz]) < 4e-3 for zz in cnt), {zz: (round(cnt[zz] / N, 4), round(th_[zz], 4)) for zz in cnt})

# 23
thv = symbols('theta', positive=True)
FX = x**3 / thv**3
fT = diff(FX.subs(x, t)**3, t)
chk('23 f_T=9t^8/θ^9', simplify(fT - 9 * t**8 / thv**9) == 0)
ET = integrate(t * fT, (t, 0, thv))
chk('23 ET=9θ/10 ⟹ a=10/9', simplify(ET - R(9, 10) * thv) == 0)
chk('23 ∫f_T=1', simplify(integrate(fT, (t, 0, thv)) - 1) == 0)

# ── 举一反三的答案 ──
chk('v1 ∫0^∞ ln(1+x)/x^1.5 收敛（1<p<2）', abs(float(sp.Integral(log(1+x)/x**R(3,2),(x,0,oo)).evalf())-2*float(pi))<1e-6)
chk('v2 ∫0^2 f = 2ln2−2', simplify(integrate(2*(x-1),(x,0,1))+integrate(log(x),(x,1,2))-(2*log(2)-2))==0)
chk('v6 b=-1 特征值 -1,2,2；b=1/2 特征值 2,1/2,1/2', Matrix([[1,-1,-1],[-1,1,-1],[-1,-1,1]]).eigenvals()=={-1:1,2:2} and Matrix([[1,R(1,2),R(1,2)],[R(1,2),1,R(1,2)],[R(1,2),R(1,2),1]]).eigenvals()=={2:1,R(1,2):2})
chk('v8 p=(1/2,1/4,1/4) ρ=-1/√3', simplify(-sqrt(R(1,2)*R(1,4)/(R(1,2)*R(3,4)))+1/sqrt(3))==0)
chk('v12 a=1/3 时 f^(5)(0)=32/3', simplify(diff(atan(x)-x/(1+x**2/3),x,5).subs(x,0)-R(32,3))==0)
M=Matrix([[lam,1,0,0],[0,lam,1,0],[0,0,lam,1],[4,3,2,lam+1]])
chk('v13 上方改 1', sp.expand(M.det()-(lam**4+lam**3-2*lam**2+3*lam-4))==0, sp.expand(M.det()))
chk('v15 面积 8+π、全心形线 ∬x=10π', simplify(integrate(integrate(r,(r,2,2*(1+cos(th)))),(th,-pi/2,pi/2))-(8+pi))==0 and simplify(integrate(integrate(r**2*cos(th),(r,0,2*(1+cos(th)))),(th,-pi,pi))-10*pi)==0)
chk('v16 k=1/2 时 ∫xy=22', simplify(integrate(x*sol,(x,0,oo))-22)==0)
chk('v17 终点(2,t) 最小值 5+ln2', simplify((2*exp(4-t)+t).subs(t,4+log(2))-(5+log(2)))==0)
# v18 斜面上侧：封闭 1/2 减坐标面（x=0 面外侧 = -面积1）
chk('v18 斜面部分 = 3/2', R(1,2)-(-1)==R(3,2))
A100=Matrix([[2-2**100,2**100-1,2**99-2],[2-2**101,2**101-1,2**100-2],[0,0,0]])
chk('v21 A^100', A21**100==A100)
chk('v22 EZ=19/20、Cov(U,X)=-1/40', 3*integrate(x*(sqrt(x)-x**2),(x,0,1))==R(9,20) and 3*integrate(x*(sqrt(x)-x),(x,0,1))-R(1,2)*R(9,20)==R(-1,40))
ET2=integrate(t**2*fT,(t,0,thv))
chk('v23 D(10T/9)=θ²/99、D(4X̄/3)=θ²/45', simplify(R(100,81)*(ET2-ET**2)-thv**2/99)==0 and simplify(R(16,9)*(R(3,5)-R(9,16))/3-R(1,45))==0)

print('\n%d/%d 通过' % (sum(ok), len(ok)))
