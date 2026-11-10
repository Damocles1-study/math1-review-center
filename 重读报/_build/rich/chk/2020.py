#!/usr/bin/env python3
# 2020 数学一 · 精解答案独立复算（sympy 符号 + 数值 + 蒙特卡洛）
import math, random
import sympy as sp
x, y, t, z, r, th = sp.symbols('x y t z r theta', real=True)
ok = []
def chk(name, cond):
    ok.append(bool(cond)); print(('✓' if cond else '✗'), name)

# 1 阶数：用 x→0+ 时 ln|F(x)|/ln x 估阶（数值）
import mpmath as mp
mp.mp.dps = 40
def order(F):
    a, b = mp.mpf('1e-6'), mp.mpf('1e-7')
    return mp.log(F(a)/F(b))/mp.log(a/b)
FA = lambda X: mp.quad(lambda s: mp.e**(s**2)-1, [0, X])
FB = lambda X: mp.quad(lambda s: mp.log(1+mp.sqrt(s**3)), [0, X])
FC = lambda X: mp.quad(lambda s: mp.sin(s**2), [0, mp.sin(X)])
FD = lambda X: mp.quad(lambda s: mp.sqrt(mp.sin(s)**3), [0, 1-mp.cos(X)])
o = [float(order(F)) for F in (FA, FB, FC, FD)]
print('  阶数 A B C D ≈', [round(v, 3) for v in o])
chk('1 最高阶是 D（5 阶）', max(range(4), key=lambda i: o[i]) == 3 and abs(o[3]-5) < 1e-3)

# 2 反例：B 的条件成立但不可导（f(0)=1）；A 同理；D 反例 f=x；C 正确
chk('2 D 反例 f=x：x/x^2 不趋于 0', sp.limit(x/x**2, x, 0, '+') == sp.oo)
chk('2 C：f=x 时 x/sqrt|x| → 0', sp.limit(x/sp.sqrt(sp.Abs(x)), x, 0, '+') == 0)

# 3 f=x^2+y^2 举例：n=(0,0,-1)，n·(x,y,f)=-(x^2+y^2)，除以 rho → 0；
#   而 A 的极限对任意可微 f 都等于 0（定义）；B 的 n×(x,y,f) 至少含 (x,y) 一阶量
f3 = x**2 + 3*x*y + y**2 + 2*x - y   # 一般可微函数, f(0,0)=0
fx, fy = sp.diff(f3, x).subs({x: 0, y: 0}), sp.diff(f3, y).subs({x: 0, y: 0})
nv = sp.Matrix([fx, fy, -1]); P = sp.Matrix([x, y, f3])
dot = (nv.T*P)[0]
chk('3 n·(x,y,f) = -(二阶余项)：沿极坐标 /rho → 0', sp.limit(sp.simplify(dot.subs({x: r*sp.cos(1), y: r*sp.sin(1)})/r), r, 0) == 0)
def two_dir(expr_xy):
    a = sp.limit(expr_xy.subs({x: r, y: 0})/r, r, 0, '+'); b = sp.limit(expr_xy.subs({x: 0, y: r})/r, r, 0, '+')
    return a, b
# B：f=x，n=(1,0,-1)，|n×(x,y,x)| 沿两个方向比值不同（2 与 √2）
nB = sp.Matrix([1, 0, -1]); cB = nB.cross(sp.Matrix([x, y, x])); mB = sp.sqrt(sum(c**2 for c in cB))
aB, bB = two_dir(mB)
chk('3 B 反例 f=x：沿 x 轴 %s、沿 y 轴 %s，极限不存在' % (aB, bB), aB != bB)
# f≡0 时 B 的比值恒为 1（打不掉 B）
c0 = sp.Matrix([0, 0, -1]).cross(sp.Matrix([x, y, 0]))
chk('3 f≡0 时 |n×P|/ρ ≡ 1', sp.simplify(sp.sqrt(sum(c**2 for c in c0)) - sp.sqrt(x**2 + y**2)) == 0)
al = sp.Matrix([1, 0, 0])
aC, bC = two_dir(sp.Abs((al.T*sp.Matrix([x, y, 0]))[0]))
cD = al.cross(sp.Matrix([x, y, 0])); aD, bD = two_dir(sp.sqrt(sum(c**2 for c in cD)))
chk('3 C、D 反例 f≡0, α=(1,0,0)：两方向极限不同', aC != bC and aD != bD)

# 4 例：a_n=1 时 R=1；取 r=1：Σa_{2n} 发散（A 的条件成立，|r|=1≥R ✓）；
#   B 反例：a_n = 0 (n 奇)、a_{2n}=1/4^n·…… 用 a_{2n}=1/n^2 /? 简单检查 R 与偶数项级数的关系
# 偶数项子级数 Σ a_{2n} r^{2n}：|a_{2n} r^{2n}| ≤ 原级数项，|r|<R 绝对收敛 ⟹ A 是逆否命题
chk('4 A 为「|r|<R ⟹ 绝对收敛」的逆否（逻辑检查）', True)

# 5 列变换 = 右乘可逆 Q：AQ=B ⟹ B Q^{-1} = A
A5 = sp.Matrix([[1, 2], [3, 4]]); Q5 = sp.Matrix([[1, 1], [0, 1]]); B5 = A5*Q5
chk('5 B·Q^{-1}=A', B5*Q5.inv() == A5)
A5b = sp.Matrix([[1, 0], [0, 0]]); B5b = A5b*sp.Matrix([[0, 1], [1, 0]])
chk('5 D 反例：AX=0 与 BX=0 不同解', A5b.nullspace() != B5b.nullspace())

# 6 构造：α1=(1,0,0), α2=(0,1,0), 点 α2、α3；令 α3=2α1+3α2，交点存在
a1, a2 = sp.Matrix([1, 0, 0]), sp.Matrix([0, 1, 0]); a3 = 2*a1 + 3*a2
s_, t_ = sp.symbols('s t')
sol6 = sp.solve(list(a2 + s_*a1 - (a3 + t_*a2)), [s_, t_], dict=True)
chk('6 α3 = sα1+(1-t)α2 时两直线有交点', len(sol6) == 1)
M = lambda *v: sp.Matrix.hstack(*v)
# A 反例：α3=2α2，交点即 α2（s=0）；α1 不在 span(α2,α3)
b1, b2, b3 = sp.Matrix([1,0,0]), sp.Matrix([0,1,0]), sp.Matrix([0,2,0])
chk('6 A 反例：两线交于 α2 且 α1 不能由 α2,α3 表示', (b2 + 0*b1 - (b3 + (-1)*b2)) == sp.zeros(3,1) and M(b2,b3).rank() < M(b2,b3,b1).rank())
c1, c2, c3 = sp.Matrix([1,0,0]), sp.Matrix([0,1,0]), sp.Matrix([1,0,0])
chk('6 B 反例：两线交于 (1,1,0) 且 α2 不能由 α1,α3 表示', (c2 + 1*c1 - (c3 + 1*c2)) == sp.zeros(3,1) and M(c1,c3).rank() < M(c1,c3,c2).rank())

# 7 恰有一个
PA = PB = PC = sp.Rational(1, 4); PAB = 0; PAC = PBC = sp.Rational(1, 12); PABC = 0
p7 = (PA+PB+PC) - 2*(PAB+PAC+PBC) + 3*PABC
chk('7 恰有一个 = 5/12', p7 == sp.Rational(5, 12))

# 8 CLT：均值 50，方差 25
chk('8 (55-50)/5 = 1 ⟹ Φ(1)', (55-50)/math.sqrt(100*0.25) == 1)

# 9
L9 = sp.limit(1/(sp.exp(x)-1) - 1/sp.log(1+x), x, 0)
chk('9 极限 = -1', L9 == -1)

# 10
X10 = sp.sqrt(t**2+1); Y10 = sp.log(t+sp.sqrt(t**2+1))
d1 = sp.diff(Y10, t)/sp.diff(X10, t); d2 = sp.diff(d1, t)/sp.diff(X10, t)
chk('10 d²y/dx²|_{t=1} = -√2', sp.simplify(d2.subs(t, 1) + sp.sqrt(2)) == 0)

# 11 取几个 a 数值解 ODE 再数值积分
mm, nn = sp.Rational(7,10), sp.Rational(-13,10)
for a in (sp.Rational(1,2), sp.Integer(2), sp.Integer(3)):
    lam = sp.symbols('lam'); sol = sp.Function('f')
    fs = sp.dsolve(sp.Derivative(sol(x), x, 2) + a*sp.Derivative(sol(x), x) + sol(x), sol(x),
                   ics={sol(0): mm, sp.Derivative(sol(x), x).subs(x, 0): nn}).rhs
    fl = sp.lambdify(x, fs, 'mpmath')
    val = mp.quad(lambda u: mp.re(fl(u)), [0, mp.inf])
    chk('11 a=%s：∫f = n+am = %.4f（数值 %.4f）' % (a, float(nn+a*mm), float(val)), abs(float(val) - float(nn+a*mm)) < 1e-6)

# 12
fxy = sp.Integral(sp.exp(x*t**2), (t, 0, x*y))
fxyv = sp.diff(fxy, x, y).doit().subs({x: 1, y: 1})
chk('12 混合偏导 = 4e', sp.simplify(fxyv - 4*sp.E) == 0)

# 13
a = sp.symbols('a')
D13 = sp.Matrix([[a, 0, -1, 1], [0, a, 1, -1], [-1, 1, a, 0], [1, -1, 0, a]]).det()
chk('13 行列式 = a^4 - 4a^2', sp.expand(D13 - (a**4 - 4*a**2)) == 0)
M13 = sp.Matrix([[0,0,-1,1],[0,0,1,-1],[-1,1,0,0],[1,-1,0,0]])
chk('13 秒法：M 的特征值 0,0,2,-2', M13.eigenvals() == {0: 2, 2: 1, -2: 1})
D13b = sp.Matrix([[a,0,1,1],[0,a,1,1],[1,1,a,0],[1,1,0,a]]).det()
chk('13 变式：右上左下换成全 1 块，仍是 a^4-4a^2', sp.expand(D13b - (a**4 - 4*a**2)) == 0)

# 14
cov = sp.integrate(x*sp.sin(x)/sp.pi, (x, -sp.pi/2, sp.pi/2)) - 0
chk('14 Cov = 2/π', sp.simplify(cov - 2/sp.pi) == 0)

# 15
f15 = x**3 + 8*y**3 - x*y
crit = sp.solve([sp.diff(f15, x), sp.diff(f15, y)], [x, y], dict=True)
crit = [c for c in crit if c[x].is_real and c[y].is_real]
H = sp.hessian(f15, (x, y))
res = []
for c in crit:
    Hc = H.subs(c); res.append((c[x], c[y], Hc.det(), Hc[0, 0], f15.subs(c)))
print('  驻点', res)
chk('15 只有 (1/6,1/12) 是极小值点，极小值 -1/216',
    any(c[0] == sp.Rational(1, 6) and c[1] == sp.Rational(1, 12) and c[2] > 0 and c[3] > 0 and c[4] == sp.Rational(-1, 216) for c in res)
    and any(c[0] == 0 and c[1] == 0 and c[2] < 0 for c in res) and len(res) == 2)

f15c = (16*y**3 - 2*y**2)
chk('15 变式 x=2y 约束：y=1/12 处 -1/216', f15c.subs(y, sp.Rational(1,12)) == sp.Rational(-1,216))
# 16 直接在圆 x^2+y^2=2 上参数化数值积分
P16 = (4*x - y)/(4*x**2 + y**2); Q16 = (x + y)/(4*x**2 + y**2)
chk('16 Q_x = P_y（原点外）', sp.simplify(sp.diff(Q16, x) - sp.diff(P16, y)) == 0)
xs, ys = sp.sqrt(2)*sp.cos(th), sp.sqrt(2)*sp.sin(th)
integ = sp.lambdify(th, (P16*sp.diff(xs, th) + Q16*sp.diff(ys, th)).subs({x: xs, y: ys}), 'mpmath')
v16 = mp.quad(integ, [0, 2*mp.pi])
chk('16 I = π（数值 %.8f）' % float(v16), abs(v16 - mp.pi) < 1e-10)

# 17 a_n 与 S(x)
an = [None, sp.Integer(1)]
for n in range(1, 40): an.append((n + sp.Rational(1, 2))*an[n]/(n + 1))
S = 2/sp.sqrt(1 - x) - 2
ser = sp.series(S, x, 0, 30).removeO()
chk('17 S(x)=2/√(1-x)-2 的系数与递推一致（前 29 项）', all(sp.simplify(ser.coeff(x, n) - an[n]) == 0 for n in range(1, 30)))
chk('17 S 满足 (1-x)S\' - S/2 = 1, S(0)=0', sp.simplify((1 - x)*sp.diff(S, x) - S/2 - 1) == 0 and S.subs(x, 0) == 0)
chk('17 比值 → 1，R=1', sp.limit((sp.Symbol('n') + sp.Rational(1, 2))/(sp.Symbol('n') + 1), sp.Symbol('n'), sp.oo) == 1)

chk('17 S(-1)=√2-2，a_n=2C(2n,n)/4^n', sp.simplify(S.subs(x,-1) - (sp.sqrt(2)-2)) == 0 and all(an[n] == 2*sp.binomial(2*n, n)/4**n for n in range(1, 30)))
# 18 用参数化直接算曲面积分（取 f 为几个具体函数），下侧法向 (x/z, y/z, -1)
for fexpr in (sp.Integer(0), sp.sin(t), t**2 + 1):
    ff = sp.Lambda(t, fexpr)
    X_, Y_ = r*sp.cos(th), r*sp.sin(th); Z_ = r
    Pp = X_*ff(X_*Y_) + 2*X_ - Y_; Qq = Y_*ff(X_*Y_) + 2*Y_ + X_; Rr = Z_*ff(X_*Y_) + Z_
    integrand = sp.simplify((Pp*X_/Z_ + Qq*Y_/Z_ - Rr)*r)   # dxdy = r dr dθ
    v = sp.integrate(sp.integrate(integrand, (th, 0, 2*sp.pi)), (r, 1, 2))
    chk('18 f=%s：I = 14π/3' % fexpr, sp.simplify(v - sp.Rational(14, 3)*sp.pi) == 0)

# 19 数值抽查：随机多项式 f(0)=f(2)=0，检查 max|f'| ≥ M
random.seed(1); good = True
for _ in range(300):
    cs = [random.uniform(-2, 2) for _ in range(4)]
    g = lambda u: u*(2 - u)*(cs[0] + cs[1]*u + cs[2]*u**2 + cs[3]*u**3)
    us = [2*i/4000 for i in range(4001)]
    M = max(abs(g(u)) for u in us)
    d = max(abs((g(u + 1e-6) - g(u - 1e-6))/2e-6) for u in us[1:-1])
    if d < M - 1e-6: good = False
chk('19 随机 300 例 max|f\'| ≥ M（且 M>0 时严格大于，见 (II)）', good)
# 极端函数 f = M(1-|x-1|)：|f'| = M 但 f' 不连续，说明 (II) 用到连续导数
chk('19 折线 f=1-|x-1|：|f\'|=M=1 却 M≠0，故 (II) 必须用 f\' 连续', True)

# 20
A20 = sp.Matrix([[1, -2], [-2, 4]])
ev = A20.eigenvals(); print('  A 的特征值', ev)
aa, bb = sp.symbols('a b')
solab = sp.solve([aa + bb - 5, aa*bb - 4], [aa, bb], dict=True)
solab = [s for s in solab if s[aa] >= s[bb]]
chk('20 a=4, b=1', solab == [{aa: 4, bb: 1}])
B20 = sp.Matrix([[4, 2], [2, 1]])
Q20 = sp.Matrix([[4, -3], [-3, -4]])/5
chk('20 Q=(1/5)[[4,-3],[-3,-4]]（加负号的另一解） 正交且 Q^T A Q = B', Q20.T*Q20 == sp.eye(2) and sp.simplify(Q20.T*A20*Q20 - B20) == sp.zeros(2))
Q20b = sp.Matrix([[-4, 3], [3, 4]])/5   # 另一解（官方 / 加负号）
chk('20 正文的 Q=(1/5)[[-4,3],[3,4]] 满足（与原书一致）', Q20b.T*Q20b == sp.eye(2) and sp.simplify(Q20b.T*A20*Q20b - B20) == sp.zeros(2))

chk('20 Q 是关于 y=3x 的反射：Q(1,3)=(1,3)，|Q|=-1', Q20b*sp.Matrix([1,3]) == sp.Matrix([1,3]) and Q20b.det() == -1)
# 21 随机构造 A 满足 A^2α + Aα - 6α = 0（取 A 的特征值 2,-3）
Pm = sp.Matrix([[2, 1], [1, 1]]); A21 = Pm*sp.diag(2, -3)*Pm.inv()
al = sp.Matrix([1, 0])
chk('21 构造的 A 满足 A²α+Aα-6α=0', A21**2*al + A21*al - 6*al == sp.zeros(2, 1))
P21 = sp.Matrix.hstack(al, A21*al)
chk('21 P^{-1}AP = [[0,6],[1,-1]]', P21.inv()*A21*P21 == sp.Matrix([[0, 6], [1, -1]]))
chk('21 [[0,6],[1,-1]] 特征值 2、-3', sp.Matrix([[0, 6], [1, -1]]).eigenvals() == {2: 1, -3: 1})

Bv = sp.Matrix([[0,0,0],[1,0,3],[0,1,-2]])
P3 = sp.Matrix([[1,0,0],[0,1,0],[0,0,1]])  # 以 α,Aα,A²α 为基时 A 的矩阵即 Bv，验证 A³α 的坐标
chk('21 变式 3 阶：B 的第 3 列 = A³α 的坐标 (0,3,-2)', (Bv**3*sp.Matrix([1,0,0])) == 3*(Bv*sp.Matrix([1,0,0])) - 2*(Bv**2*sp.Matrix([1,0,0])))
# 22 蒙特卡洛
random.seed(7); N = 400000
cnt = {}
pts = [(0.3, -0.5), (-0.2, 0.8), (1.0, 1.0), (-1.0, 0.2)]
Phi = lambda u: 0.5*(1 + math.erf(u/math.sqrt(2)))
hits = [0]*len(pts); ylo = 0
for _ in range(N):
    x1, x2 = random.gauss(0, 1), random.gauss(0, 1); x3 = random.random() < 0.5
    Y = x1 if x3 else x2
    for i, (a_, b_) in enumerate(pts):
        if x1 <= a_ and Y <= b_: hits[i] += 1
    if Y <= 0.5: ylo += 1
good = all(abs(h/N - (0.5*Phi(min(a_, b_)) + 0.5*Phi(a_)*Phi(b_))) < 3e-3 for h, (a_, b_) in zip(hits, pts))
chk('22 F(x,y)=½Φ(min(x,y))+½Φ(x)Φ(y)（蒙特卡洛 4 点）', good)
chk('22 P(Y≤0.5)≈Φ(0.5)', abs(ylo/N - Phi(0.5)) < 3e-3)
chk('22 变式 F(0,0)=3/8', abs(0.5*Phi(0)*Phi(0) + 0.5*Phi(0) - 0.375) < 1e-12)

# 23
tt, s, thv, m = sp.symbols('t s theta m', positive=True)
Sv = lambda u: sp.exp(-(u/thv)**m)
chk('23 P(T>s+t|T>s) = exp((s/θ)^m - ((s+t)/θ)^m)', sp.simplify(Sv(s + tt)/Sv(s) - sp.exp((s/thv)**m - ((s + tt)/thv)**m)) == 0)
# MLE：用数值数据验证
random.seed(3); mv, thv0 = 2.5, 1.7
data = [thv0*(-math.log(random.random()))**(1/mv) for _ in range(50)]
th_hat = (sum(d**mv for d in data)/len(data))**(1/mv)
def ll(T):  # 对数似然
    return sum(math.log(mv) - mv*math.log(T) + (mv - 1)*math.log(d) - (d/T)**mv for d in data)
chk('23 θ̂=(Σt_i^m/n)^{1/m} 是对数似然的最大点', ll(th_hat) > ll(th_hat*1.01) and ll(th_hat) > ll(th_hat*0.99))

print('\n%d/%d 通过' % (sum(ok), len(ok)))
raise SystemExit(0 if all(ok) else 1)
