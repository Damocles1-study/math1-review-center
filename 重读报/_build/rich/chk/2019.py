# -*- coding: utf-8 -*-
"""2019 数学一 整卷答案独立复算（sympy / 数值 / 蒙特卡洛）。跑：python3 _build/rich/chk/2019.py"""
import random, math
import sympy as sp
from sympy import (symbols, sin, cos, tan, exp, log, sqrt, pi, oo, integrate, limit, series,
                   Matrix, diff, simplify, Rational, Function, dsolve, Eq, factorial, Sum, atan, cosh)
x, y, z, t, u, n, k = symbols('x y z t u n k', real=True)
ok = []
def chk(name, cond):
    ok.append((name, bool(cond)))
    print(('✓ ' if cond else '✗ ') + name)

# 1  x - tan x ~ -x^3/3
s1 = series(x - tan(x), x, 0, 6).removeO()
chk('1: x-tan x 首项 -x^3/3 ⟹ k=3 (C)', sp.expand(s1).coeff(x, 3) == Rational(-1, 3) and sp.expand(s1).coeff(x, 1) == 0)

# 2  f = x|x| (x<=0), x ln x (x>0)
rd = limit((x*log(x) - 0)/x, x, 0, '+')
chk('2: 右导数 = -oo ⟹ 不可导', rd == -oo)
fl = lambda v: v*abs(v) if v <= 0 else v*math.log(v)
chk('2: 0 两侧 f<0=f(0) ⟹ 极大值 (B)', all(fl(h) < 0 and fl(-h) < 0 for h in [1e-1, 1e-3, 1e-6, 0.5]))

# 3  反例 u_n = -1/n（单调增有界）
N = 200000
uA = sum((-1/m)/m for m in range(1, N))          # 收敛，但换 u_n=1-1/n 发散
uA2 = sum((1-1/m)/m for m in range(1, N))
chk('3A: u_n=1-1/n 时 Σu_n/n 部分和随 N 发散（> 11）', uA2 > 11)
# B: u_n=-1/n 时 (-1)^n/u_n = (-1)^{n+1} n，通项不趋 0
chk('3B: 通项 (-1)^n/u_n = (-1)^{n+1}n 不趋于 0', all(abs(abs((-1)**m/(-1/m)) - m) < 1e-6 for m in (10, 1000, N)))
# C: 1 - u_n/u_{n+1} = 1 - (n+1)/n = -1/n
cC = sum(1 - (-1/m)/(-1/(m+1)) for m in range(1, N))
chk('3C: u_n=-1/n 时 Σ(1-u_n/u_{n+1}) = -Σ1/n 发散', cC < -12)
# D 望远镜
uu = lambda m: 1 - 1/m
chk('3D: 部分和 = u_{N+1}^2-u_1^2 有界', abs(sum(uu(m+1)**2 - uu(m)**2 for m in range(1, 1000)) - (uu(1000)**2 - uu(1)**2)) < 1e-9)

# 4
Q = x/y**2
cands = {'A': y - x**2/y**3, 'B': 1/y - x**2/y**3, 'C': 1/x - 1/y, 'D': x - 1/y}
good = [kk for kk, P in cands.items() if simplify(diff(P, y) - diff(Q, x)) == 0]
chk('4: 满足 P_y=Q_x 的只有 C、D；C 在 x=0 无定义 ⟹ D', good == ['C', 'D'])

# 5  特征值 1,-2,-2
lam = symbols('lam')
roots = sp.solve(lam**2 + lam - 2, lam)
combos = [(a, b, c) for a in roots for b in roots for c in roots if a*b*c == 4]
chk('5: |A|=4 ⟹ 特征值 {1,-2,-2} ⟹ 一正两负 (C)', all(sorted(cb) == [-2, -2, 1] for cb in combos) and combos)

# 6  举一组具体三平面：x=0, y=0, x+y=1 （都平行于 z 轴，两两相交，交线平行）
Am = Matrix([[1, 0, 0], [0, 1, 0], [1, 1, 0]]); Ab = Am.row_join(Matrix([0, 0, 1]))
chk('6: 实例 r(A)=2, r(Ā)=3 (A)', Am.rank() == 2 and Ab.rank() == 3)

# 7  随机抽概率空间验证 C ⟺ P(A)=P(B)
random.seed(7)
okc = True
for _ in range(2000):
    p = [random.random() for _ in range(4)]; s_ = sum(p); p = [v/s_ for v in p]   # AB, A~B, ~AB, ~A~B
    PA, PB = p[0]+p[1], p[0]+p[2]
    if (abs(p[1]-p[2]) < 1e-12) != (abs(PA-PB) < 1e-12): okc = False
chk('7: P(A B̄)=P(B Ā) ⟺ P(A)=P(B) (C)', okc)

# 8
Phi = lambda v: 0.5*(1+math.erf(v/math.sqrt(2)))
f8 = lambda mu, sg: 2*Phi(1/(math.sqrt(2)*sg)) - 1
random.seed(8)
def mc8(mu, sg, M=200000):
    c = 0
    for _ in range(M):
        if abs(random.gauss(mu, sg) - random.gauss(mu, sg)) < 1: c += 1
    return c/M
chk('8: 与 μ 无关、与 σ 有关 (A)', abs(mc8(0, 1) - f8(0, 1)) < 0.01 and abs(mc8(5, 1) - f8(5, 1)) < 0.01 and abs(f8(0, 1) - f8(0, 2)) > 0.1)

# 9
f = Function('f')
zz = f(sin(y) - sin(x)) + x*y
e9 = simplify(diff(zz, x)/cos(x) + diff(zz, y)/cos(y))
chk('9: = y/cos x + x/cos y', simplify(e9 - (y/cos(x) + x/cos(y))) == 0)

# 10
Y = sqrt(3*exp(x) - 2)
chk('10: y=√(3e^x-2) 满足方程与初值', simplify(2*Y*diff(Y, x) - Y**2 - 2) == 0 and Y.subs(x, 0) == 1)

# 11
xv = 2.7
sv = sum((-1)**m/math.factorial(2*m)*xv**m for m in range(40))
chk('11: S(x)=cos√x', abs(sv - math.cos(math.sqrt(xv))) < 1e-12)

# 12  上侧投影 D: x^2+y^2<=4，被积 = |y|
r, th = symbols('r th', positive=True)
I12 = integrate(integrate(r*abs(sin(th))*r, (r, 0, 2)), (th, 0, 2*pi))
chk('12: = 32/3', simplify(I12 - Rational(32, 3)) == 0)
# 数值直接算 ∬_D sqrt(4-x^2-4z^2) 其中 z=sqrt((4-x^2-y^2)/4)
import random as R; R.seed(12); M = 400000; acc = 0
for _ in range(M):
    a, b = R.uniform(-2, 2), R.uniform(-2, 2)
    if a*a + b*b <= 4:
        zz2 = (4 - a*a - b*b)/4; acc += math.sqrt(max(0.0, 4 - a*a - 4*zz2))
chk('12: 蒙特卡洛 ≈ 32/3', abs(acc/M*16 - 32/3) < 0.05)

# 13
a1, a2 = Matrix([1, 0, 2]), Matrix([0, 1, 1]); a3 = -a1 + 2*a2
A13 = a1.row_join(a2).row_join(a3)
ns = A13.nullspace()
chk('13: 基础解系 ∝ (1,-2,1)^T', len(ns) == 1 and simplify(ns[0]/ns[0][0] - Matrix([1, -2, 1])) == Matrix([0, 0, 0]))

# 14
EX = integrate(x*x/2, (x, 0, 2))
F = lambda v: v*v/4
chk('14: EX=4/3', EX == Rational(4, 3))
R.seed(14); M = 400000
c14 = sum(1 for _ in range(M) if F(2*math.sqrt(R.random())) > 4/3 - 1)/M   # X=2√U 的密度为 x/2
chk('14: P{F(X)>1/3}=2/3', abs(c14 - 2/3) < 0.005)

# 15
y15 = x*exp(-x**2/2)
chk('15: y=x e^{-x^2/2} 满足方程与初值', simplify(diff(y15, x) + x*y15 - exp(-x**2/2)) == 0 and y15.subs(x, 0) == 0)
y2 = simplify(diff(y15, x, 2))
chk('15: y\'\' = x(x^2-3)e^{-x^2/2}', simplify(y2 - x*(x**2 - 3)*exp(-x**2/2)) == 0)
chk('15: 拐点纵坐标 ±√3 e^{-3/2}', simplify(y15.subs(x, sqrt(3)) - sqrt(3)*exp(Rational(-3, 2))) == 0)

# 16
a, b = symbols('a b', real=True)
g = Matrix([6*a, 8*b])
sol = sp.solve([6*a*(-4) - 8*b*(-3), 36*a**2 + 64*b**2 - 100], [a, b], dict=True)
sol = [s_ for s_ in sol if (6*s_[a])*(-3) + (8*s_[b])*(-4) > 0]
chk('16: a=b=-1', sol == [{a: -1, b: -1}])
S16 = integrate(integrate(sqrt(1 + 4*r**2)*r, (r, 0, sqrt(2))), (th, 0, 2*pi))
chk('16: 面积 13π/3', simplify(S16 - 13*pi/3) == 0)

# 17
I0 = integrate(exp(-x)*sin(x), (x, 0, pi))
chk('17: ∫_0^π e^{-x}sin x = (1+e^{-π})/2', simplify(I0 - (1 + exp(-pi))/2) == 0)
ans17 = (1 + exp(-pi))/(2*(1 - exp(-pi)))
import scipy.integrate as si
num17, _ = si.quad(lambda v: math.exp(-v)*abs(math.sin(v)), 0, 60, limit=500)
chk('17: 面积 = (1+e^{-π})/(2(1-e^{-π})) = %.6f' % float(ans17), abs(num17 - float(ans17)) < 1e-7)
chk('17: 等价写法 ½·coth(π/2)', abs(float(ans17) - 0.5/math.tanh(math.pi/2)) < 1e-12)

# 18
an = lambda m: si.quad(lambda v: v**m*math.sqrt(1 - v*v), 0, 1)[0]
chk('18: 递推 a_n=(n-1)/(n+2) a_{n-2}（n=2..12）', all(abs(an(m) - (m - 1)/(m + 2)*an(m - 2)) < 1e-9 for m in range(2, 13)))
chk('18: 单调递减', all(an(m + 1) < an(m) for m in range(0, 15)))
chk('18: a_n/a_{n-1} → 1（n=400 时 >0.99）', an(400)/an(399) > 0.99)
chk('18: a_0=π/4, a_1=1/3', abs(an(0) - math.pi/4) < 1e-9 and abs(an(1) - 1/3) < 1e-9)

# 19  截面：圆心 (0,z) 半径 1-z
V = integrate(pi*(1 - z)**2, (z, 0, 1))
My = integrate(z*pi*(1 - z)**2, (z, 0, 1))   # ∭ y dV（截面圆心 y=z）
Mz = integrate(z*pi*(1 - z)**2, (z, 0, 1))
chk('19: V=π/3, ȳ=z̄=1/4', V == pi/3 and simplify(My/V) == Rational(1, 4) and simplify(Mz/V) == Rational(1, 4))
R.seed(19); M = 400000; cnt = sy = sz = 0
for _ in range(M):
    px, py, pz = R.uniform(-1, 1), R.uniform(-1, 2), R.uniform(0, 1)
    if px*px + (py - pz)**2 <= (1 - pz)**2:
        cnt += 1; sy += py; sz += pz
chk('19: 蒙特卡洛 体积≈π/3、形心≈(0,1/4,1/4)', abs(cnt/M*6 - math.pi/3) < 0.01 and abs(sy/cnt - .25) < .01 and abs(sz/cnt - .25) < .01)

# 20
aa, bb, cc = symbols('aa bb cc')
A1, A2 = Matrix([1, 2, 1]), Matrix([1, 3, 2]); A3 = Matrix([1, aa, 3]); B = Matrix([1, 1, 1])
s20 = sp.solve(list(bb*A1 + cc*A2 + A3 - B), [aa, bb, cc], dict=True)
chk('20: a=3,b=2,c=-2', s20 == [{aa: 3, bb: 2, cc: -2}])
A3v = A3.subs(aa, 3)
Mnew = A2.row_join(A3v).row_join(B); Mold = A1.row_join(A2).row_join(A3v)
chk('20: α2,α3,β 线性无关', Mnew.det() != 0)
P20 = Mnew.inv()*Mold
chk('20: 过渡矩阵 P=[[1,1,0],[-1/2,0,1],[1/2,0,0]]', P20 == Matrix([[1, 1, 0], [Rational(-1, 2), 0, 1], [Rational(1, 2), 0, 0]]))
chk('20: 校验 (α1,α2,α3)=(α2,α3,β)P', Mnew*P20 == Mold)

# 21
X_, Y_ = symbols('X_ Y_')
A21 = Matrix([[-2, -2, 1], [2, X_, -2], [0, 0, -2]]); B21 = Matrix([[2, 1, 0], [0, -1, 0], [0, 0, Y_]])
s21 = sp.solve([A21.trace() - B21.trace(), A21.det() - B21.det()], [X_, Y_], dict=True)
chk('21: x=3,y=-2', s21 == [{X_: 3, Y_: -2}])
A21 = A21.subs(X_, 3); B21 = B21.subs(Y_, -2)
chk('21: 特征多项式相同、都可对角化', A21.charpoly() == B21.charpoly() and A21.is_diagonalizable() and B21.is_diagonalizable())
Pbook = Matrix([[-1, -1, -1], [2, 1, 2], [0, 0, 4]])
chk('21: 书答 P 满足 P^{-1}AP=B', Pbook.det() != 0 and Pbook.inv()*A21*Pbook == B21)
P1 = Matrix([[-1, -2, -1], [2, 1, 2], [4, 0, 0]]); P2 = Matrix([[0, -1, 1], [0, 3, 0], [1, 0, 0]])
chk('21: P1^{-1}AP1 = P2^{-1}BP2 = diag(-2,-1,2)', P1.inv()*A21*P1 == sp.diag(-2, -1, 2) and P2.inv()*B21*P2 == sp.diag(-2, -1, 2))
chk('21: P1 P2^{-1} = 书答 P', P1*P2.inv() == Pbook)
# 我在精解里用的另一组：P1 列取 (1,-2,-4),(2,-1,0),(1,-2,0) 即全部取负
P1b = -P1
chk('21: 特征向量整体取负也行：P = -书答 P', (P1b*P2.inv()).inv()*A21*(P1b*P2.inv()) == B21)

# 22
pp = symbols('pp', positive=True)
EX22, EX2, EY = 1, 2, (1 - pp) - pp
cov = EX2*EY - EX22*EX22*EY
chk('22: Cov(X,Z)=1-2p ⟹ p=1/2', simplify(cov - (1 - 2*pp)) == 0 and sp.solve(cov, pp) == [Rational(1, 2)])
R.seed(22); M = 300000; pv = 0.3
zs = [R.expovariate(1)*(-1 if R.random() < pv else 1) for _ in range(M)]
# 检查密度：P(Z<-1) = p e^{-1}，P(Z>2) = (1-p)e^{-2}
chk('22: f_Z: P(Z<-1)=p e^{-1}, P(Z>2)=(1-p)e^{-2}', abs(sum(1 for v in zs if v < -1)/M - pv*math.exp(-1)) < .004 and abs(sum(1 for v in zs if v > 2)/M - (1 - pv)*math.exp(-2)) < .004)
# 不独立：P(X<=1, Z<=-1) = 0 ≠ P(X<=1)P(Z<=-1)
PX1 = 1 - math.exp(-1); PZm1 = pv*math.exp(-1)
chk('22: P(X≤1,Z≤-1)=0 而 P(X≤1)P(Z≤-1)>0 ⟹ 不独立', PX1*PZm1 > 0)

# 23
s_, mu = symbols('s_ mu', positive=True)
A23 = symbols('A23', positive=True)
I23 = integrate(A23/s_*exp(-(x - mu)**2/(2*s_**2)), (x, mu, oo))
chk('23: A=√(2/π)', simplify(sp.solve(I23 - 1, A23)[0] - sqrt(2/pi)) == 0)
# MLE：对 θ=σ^2 求导
th2 = symbols('th2', positive=True); nn = symbols('nn', positive=True); SS = symbols('SS', positive=True)
lnL = -nn/2*log(th2) - SS/(2*th2)
chk('23: σ²的 MLE = (1/n)Σ(X_i-μ)²', sp.solve(diff(lnL, th2), th2) == [SS/nn])
R.seed(23); data = [3 + abs(R.gauss(0, 1.7)) for _ in range(200000)]
est = sum((d - 3)**2 for d in data)/len(data)
chk('23: 模拟样本估计 ≈ σ²=2.89', abs(est - 2.89) < 0.05)

# ── 变式与校验数值 ──
chk('20变式: P(1,1,1)^T=(2,1/2,1/2)，且 2α2+½α3+½β=(3,8,6)', P20*Matrix([1,1,1])==Matrix([2,Rational(1,2),Rational(1,2)]) and 2*A2+A3v/2+B/2==Matrix([3,8,6]))
chk('20注: 反向过渡矩阵 Q=P^{-1}', P20.inv()==Matrix([[0,0,2],[1,0,-2],[0,1,1]]) and P20.det()==Rational(1,2))
chk('20变式: |α1,α2,α3|=4-a', sp.simplify(Matrix([[1,1,1],[2,3,aa],[1,2,3]]).det()-(4-aa))==0)
chk('21: AP=PB=[[-2,0,2],[4,1,-4],[0,0,-8]]', A21*Pbook==Matrix([[-2,0,2],[4,1,-4],[0,0,-8]])==Pbook*B21)
chk('21: P2^{-1}', P2.inv()==Matrix([[0,0,1],[0,Rational(1,3),0],[1,Rational(1,3),0]]))
chk('17变式: e^{-2x} 时 J=(1+e^{-2π})/5', simplify(integrate(exp(-2*x)*sin(x),(x,0,pi))-(1+exp(-2*pi))/5)==0)
chk('16变式: z≥1 面积 π(5√5−1)/6；体积 2π', simplify(integrate(integrate(sqrt(1+4*r**2)*r,(r,0,1)),(th,0,2*pi))-pi*(5*sqrt(5)-1)/6)==0 and integrate(integrate((2-r**2)*r,(r,0,sqrt(2))),(th,0,2*pi))==2*pi)
chk('19变式: 转动惯量 2π/15', simplify(integrate(pi/2*(1-z)**4+z**2*pi*(1-z)**2,(z,0,1))-2*pi/15)==0)
chk('18变式: a_4=π/32', abs(an(4)-math.pi/32)<1e-10)
chk('23变式: E(X-μ)²=σ², E(X-μ)=σ√(2/π)', simplify(integrate((x-mu)**2*sqrt(2/pi)/s_*exp(-(x-mu)**2/(2*s_**2)),(x,mu,oo))-s_**2)==0 and simplify(integrate((x-mu)*sqrt(2/pi)/s_*exp(-(x-mu)**2/(2*s_**2)),(x,mu,oo))-s_*sqrt(2/pi))==0)
chk('13变式: A*x=0 的解空间维数 2', A13.adjugate().rank()==1)
chk('12变式: 下侧 ∬z dxdy = -8π/3', simplify(-integrate(integrate(sqrt(4-r**2)/2*r,(r,0,2)),(th,0,2*pi))+8*pi/3)==0)

bad = [nm for nm, c in ok if not c]
print('\n共 %d 项，失败 %d 项' % (len(ok), len(bad)))
if bad: raise SystemExit(1)
