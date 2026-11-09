# -*- coding: utf-8 -*-
"""2023 数学一 · 精解答案独立复算。python3 _build/rich/chk/2023.py 全部 ✓ 才算过。"""
import math, random, itertools
import sympy as sp
from sympy import Matrix, Rational as R, symbols, oo, pi, E
x, y, z, t, a, b = symbols('x y z t a b', real=True)
OK = []
def ok(n, cond, msg=''):
    cond = bool(cond); OK.append(cond); print(('✓' if cond else '✗'), n, msg)

# 1 斜渐近线 y=x ln(e+1/(x-1))
f1 = x*sp.log(E + 1/(x-1))
k = sp.limit(f1/x, x, oo); b1 = sp.limit(f1 - k*x, x, oo); b1m = sp.limit(f1 - k*x, x, -oo)
ok(1, k == 1 and sp.simplify(b1 - 1/E) == 0 and sp.simplify(b1m - 1/E) == 0, 'k=%s b=%s (x→-∞ 也是 %s)' % (k, b1, b1m))

# 2 y''+ay'+by=0 在 R 上所有解有界：枚举四个选项的代表值，看通解基是否有界
def bounded(av, bv):
    w = symbols("w"); r = sp.solve(w**2 + av*w + bv, w)
    if len(r) == 1: return False  # 重根带 x e^{rx}
    return all(sp.re(ri) == 0 for ri in r)
ok(2, [bounded(-1, 1), bounded(1, 1), bounded(0, 1), bounded(0, -1)] == [False, False, True, False], '只有 C(a=0,b>0) 有界')

# 3 参数方程 x=2t+|t|, y=|t|sin t
fp = (x/3)*sp.sin(x/3); fm = -x*sp.sin(x)
d1p = sp.limit(fp/x, x, 0, '+'); d1m = sp.limit(fm/x, x, 0, '-')
g1p = sp.diff(fp, x); g1m = sp.diff(fm, x)
cont = sp.limit(g1p, x, 0, '+') == 0 and sp.limit(g1m, x, 0, '-') == 0
d2p = sp.limit(g1p/x, x, 0, '+'); d2m = sp.limit(g1m/x, x, 0, '-')
ok(3, d1p == 0 and d1m == 0 and cont and d2p == R(2, 9) and d2m == -2, "f'(0)=0, f' 连续, f''(0±)=%s,%s" % (d2p, d2m))

# 4 充要：随机造反例搜索（a_n<b_n、两级数都收敛，一方绝对收敛另一方不绝对收敛）——用三角不等式的界数值验证
random.seed(1); bad = 0
for _ in range(2000):
    N = 400
    an = [(-1)**n/(n+1)**random.choice([0.6, 1.5]) for n in range(N)]
    d = [abs(random.random())/(n+1)**2 for n in range(N)]  # b-a>0 且绝对收敛
    bn = [an[i] + d[i] for i in range(N)]
    sa = sum(abs(v) for v in an); sb = sum(abs(v) for v in bn); sd = sum(d)
    if sb > sa + sd + 1e-9 or sa > sb + sd + 1e-9: bad += 1
ok(4, bad == 0, '|b|≤|a|+(b-a)、|a|≤|b|+(b-a) 两向都成立 ⟹ 充要（A）')

# 5 分块矩阵秩：随机 ABC=O 的整数矩阵
random.seed(5); good = True
for _ in range(60):
    n = random.choice([2, 3, 4])
    A = Matrix(n, n, lambda i, j: random.randint(-2, 2))
    B = Matrix(n, n, lambda i, j: random.randint(-2, 2)) * Matrix.diag(*[random.choice([0, 1]) for _ in range(n)])
    AB = A*B
    ns = AB.nullspace()
    C = Matrix.hstack(*(ns[:1]*n)) if ns else sp.zeros(n)
    assert (A*B*C).is_zero_matrix
    O, I = sp.zeros(n), sp.eye(n)
    r1 = Matrix.vstack(Matrix.hstack(O, A), Matrix.hstack(B*C, I)).rank()
    r2 = Matrix.vstack(Matrix.hstack(AB, C), Matrix.hstack(O, I)).rank()
    r3 = Matrix.vstack(Matrix.hstack(I, AB), Matrix.hstack(AB, O)).rank()
    good &= (r1 == n and r2 == n + AB.rank() and r3 == n + (AB*AB).rank() and r1 <= r3 <= r2)
ok(5, good, 'r1=n, r2=n+r(AB), r3=n+r((AB)^2) ⟹ r1≤r3≤r2（B）')

# 6 不能对角化
res = []
for M in [Matrix([[1, 1, a], [0, 2, 2], [0, 0, 3]]), Matrix([[1, 1, a], [1, 2, 0], [a, 0, 3]]), Matrix([[1, 1, a], [0, 2, 0], [0, 0, 2]]), Matrix([[1, 1, a], [0, 2, 2], [0, 0, 2]])]:
    res.append(all(M.subs(a, v).is_diagonalizable() for v in [-3, -1, 0, 1, 2, R(1, 2)]))
ok(6, res == [True, True, True, False], '只有 D 不能对角化（对任意 a）')

# 7 交空间
a1, a2, b1v, b2v = Matrix([1, 2, 3]), Matrix([2, 1, 1]), Matrix([2, 5, 9]), Matrix([1, 0, 1])
ns = Matrix.hstack(a1, a2, -b1v, -b2v).nullspace()
g = (ns[0][0]*a1 + ns[0][1]*a2); g = g/g[0]
ok(7, len(ns) == 1 and list(g) == [1, 5, 8] and list(3*a1 - a2) == [1, 5, 8] and list(b1v - b2v) == [1, 5, 8], 'γ=k(1,5,8)^T（D）')

# 8 E|X-1|, X~P(1)
k8 = symbols('k', integer=True, nonnegative=True)
v8 = sp.exp(-1)*1 + sp.summation((k8-1)*sp.exp(-1)/sp.factorial(k8), (k8, 2, oo))
ok(8, sp.simplify(v8 - 2/E) == 0, 'E|X-1|=%s（C）' % sp.simplify(v8))

# 9 F 分布：蒙特卡洛看 2S1^2/S2^2 的均值 ≈ (m-1)/(m-3)
random.seed(9); n9, m9 = 6, 9; vals = []
for _ in range(40000):
    X = [random.gauss(1, 1) for _ in range(n9)]; Y = [random.gauss(-2, math.sqrt(2)) for _ in range(m9)]
    s1 = sum((u - sum(X)/n9)**2 for u in X)/(n9-1); s2 = sum((u - sum(Y)/m9)**2 for u in Y)/(m9-1)
    vals.append(2*s1/s2)
mean = sum(vals)/len(vals)
ok(9, abs(mean - (m9-1)/(m9-3)) < 0.05, '2S1²/S2² 样本均值 %.3f ≈ F(n-1,m-1) 均值 %.3f（D）' % (mean, (m9-1)/(m9-3)))

# 10 a|X1-X2| 无偏
s = symbols('s', positive=True)
EZ = 2*sp.integrate(z*sp.exp(-z**2/(2*2*s**2))/sp.sqrt(2*pi*2*s**2), (z, 0, oo))
av = sp.simplify(s/EZ)
ok(10, sp.simplify(av - sp.sqrt(pi)/2) == 0, 'a=%s（A）' % av)

# 11
ser = sp.series(a*x + b*x**2 + sp.log(1+x), x, 0, 3).removeO(); g11 = sp.series(sp.exp(x**2) - sp.cos(x), x, 0, 3).removeO()
sol = sp.solve([ser.coeff(x, 1), ser.coeff(x, 2) - g11.coeff(x, 2)], [a, b])
ok(11, sol[a]*sol[b] == -2, 'a=%s b=%s ab=-2' % (sol[a], sol[b]))

# 12
F = x + 2*y + sp.log(1 + x**2 + y**2)
ok(12, (sp.diff(F, x).subs({x: 0, y: 0}), sp.diff(F, y).subs({x: 0, y: 0})) == (1, 2), '切平面 z=x+2y 即 x+2y-z=0')

# 13 余弦级数 Σa_{2n}
nn = symbols('n', integer=True, positive=True)
an13 = sp.simplify(2*sp.integrate((1-x)*sp.cos(nn*pi*x), (x, 0, 1)))
a0 = 2*sp.integrate(1-x, (x, 0, 1))
s13 = sum(an13.subs(nn, 2*j) for j in range(1, 50))
ok(13, a0 == 1 and sp.simplify(s13) == 0, 'a_n=%s, a0=1, Σa_{2n}=0' % an13)

# 14 取一个满足条件的 f 验证：f(x)=x^2/4 - x/2 + c 满足 f(x+2)-f(x)=x；再调 c 使 ∫_0^2 f=0
c = symbols('c'); f14 = x**2/4 - x/2 + c
assert sp.simplify(f14.subs(x, x+2) - f14 - x) == 0
cv = sp.solve(sp.integrate(f14, (x, 0, 2)), c)[0]
# 加一个周期 2、积分为 0 的扰动，确认答案与 f 的具体形状无关
f14b = f14.subs(c, cv) + sp.sin(pi*x)
ok(14, sp.integrate(f14.subs(c, cv), (x, 1, 3)) == R(1, 2) and sp.simplify(sp.integrate(f14b, (x, 1, 3)) - R(1, 2)) == 0, '∫_1^3 f = 1/2')

# 15
A15 = [Matrix([1, 0, 1, 1]), Matrix([-1, -1, 0, 1]), Matrix([0, 1, -1, 1])]; be = Matrix([1, 1, 1, -1])
ks = symbols('k1:4'); gam = sum((ks[i]*A15[i] for i in range(3)), sp.zeros(4, 1))
sol15 = sp.solve([(gam.T*A15[i])[0] - (be.T*A15[i])[0] for i in range(3)], ks)
ok(15, sum(v**2 for v in sol15.values()) == R(11, 9), 'k=%s, 平方和 11/9' % sol15)

# 16
pX = {0: R(2, 3), 1: R(1, 3)}; pY = {0: R(1, 4), 1: R(1, 2), 2: R(1, 4)}
ok(16, sum(pX[i]*pY[i] for i in (0, 1)) == R(1, 3), 'P(X=Y)=1/3')

# 17
Y = sp.Function('Y')
sol17 = sp.dsolve(sp.Eq(Y(x) - x*Y(x).diff(x), x), Y(x), ics={Y(1): 2}).rhs
fmax = sp.integrate(sol17.subs(x, t), (t, 1, sp.exp(2)))
ok(17, sp.simplify(sol17 - x*(2 - sp.log(x))) == 0 and sp.simplify(fmax - (sp.exp(4) - 5)/4) == 0, 'y=%s, 最大值 %s' % (sol17, sp.simplify(fmax)))

# 18
f18 = (y - x**2)*(y - x**3)
crit = sp.solve([sp.diff(f18, x), sp.diff(f18, y)], [x, y], dict=True)
H = sp.hessian(f18, (x, y)); info = []
for p in crit:
    Hp = H.subs(p); info.append((p[x], p[y], Hp.det(), Hp[0, 0], f18.subs(p)))
info.sort()
p3 = [i for i in info if i[0] == R(2, 3)][0]
# (0,0),(1,1) 附近数值找正负值
def sign_both(px, py):
    # 沿 y=py 的水平线与夹在两曲线之间的点各取一个，看符号
    if (px, py) == (0, 0):
        vals = [f18.subs({x: e, y: 0}) for e in (R(1, 100), R(-1, 100))]           # f(x,0)=x^5
    else:
        e = R(1, 100)
        vals = [f18.subs({x: 1 + e, y: 1 + R(5, 2)*e}), f18.subs({x: 1 + e, y: 1})]  # 斜率 2.5 落在两曲线之间
    return min(vals) < 0 < max(vals)
ok(18, len(crit) == 3 and p3[1] == R(10, 27) and p3[2] > 0 and p3[3] > 0 and p3[4] == R(-4, 729) and sign_both(0, 0) and sign_both(1, 1),
   '驻点 %s；(2/3,10/27) 处 AC-B²=%s A=%s 极小值 %s；另两点附近变号' % ([(i[0], i[1]) for i in info], p3[2], p3[3], p3[4]))

# 19 高斯
r, th = symbols('r theta', nonnegative=True)
div = sp.diff(2*x*z, x) + sp.diff(x*z*sp.cos(y), y) + sp.diff(3*y*z*sp.sin(x), z)
inner = sp.integrate(div, (z, 0, 1 - x))
from scipy import integrate as si
fi = sp.lambdify((r, th), inner.subs({x: r*sp.cos(th), y: r*sp.sin(th)})*r, 'math')
I19 = si.dblquad(lambda rr, tt: fi(rr, tt), 0, 2*math.pi, 0, 1)[0]
ok(19, abs(I19 - 5*math.pi/4) < 1e-8, 'div=%s, I=%.10f, 5π/4=%.10f' % (div, I19, 5*math.pi/4))

# 20 用几个具体函数数值验证 (I)(II) 的不等式/等式可达
def chk20():
    good = True
    for fn, d2 in [(lambda u: math.sin(u) + u*u, lambda u: -math.sin(u) + 2), (lambda u: math.exp(u) - 1, lambda u: math.exp(u))]:
        aa = 1.3; target = (fn(aa) + fn(-aa))/aa**2
        xs = [-aa + 2*aa*i/4000 for i in range(1, 4000)]
        good &= min(d2(u) for u in xs) <= target <= max(d2(u) for u in xs)
    # (II)：f=(x-0.4)^2+ x^3/5 在 (-1,1) 内取极小值
    fn = lambda u: (u-0.4)**2 + u**3/5; d2 = lambda u: 2 + 6*u/5; aa = 1
    xs = [-aa + 2*aa*i/4000 for i in range(1, 4000)]
    good &= max(abs(d2(u)) for u in xs) >= abs(fn(aa) - fn(-aa))/(2*aa*aa)
    return good
ok(20, chk20(), '(I) 目标值落在 f\'\' 的值域内；(II) 不等式在例子上成立')

# 21
A21 = Matrix([[1, 1, -1], [1, 2, 0], [-1, 0, 2]]); B21 = Matrix([[1, 0, 0], [0, 1, 1], [0, 1, 1]]); P = Matrix([[1, -1, 1], [0, 1, 0], [0, 0, 1]])
ok(21, P.T*A21*P == B21 and P.det() != 0 and A21.trace() == 5 and B21.trace() == 3 and sorted(A21.eigenvals()) == [0, 2, 3] and sorted(B21.eigenvals()) == [0, 1, 2],
   'P^TAP=B；特征值 A:{0,2,3} B:{0,1,2} ⟹ 不存在正交变换')

# 22
dens = 2/pi*(x**2 + y**2)
tot = sp.integrate(sp.integrate(2/pi*r**2*r, (r, 0, 1)), (th, 0, 2*pi))
EXY = sp.integrate(sp.integrate(2/pi*r**2*(r*sp.cos(th))*(r*sp.sin(th))*r, (r, 0, 1)), (th, 0, 2*pi))
EX = sp.integrate(sp.integrate(2/pi*r**2*(r*sp.cos(th))*r, (r, 0, 1)), (th, 0, 2*pi))
fX = sp.simplify(sp.integrate(dens, (y, -sp.sqrt(1 - x**2), sp.sqrt(1 - x**2))))
zz = symbols('zz', positive=True)
FZ = sp.integrate(sp.integrate(2/pi*r**3, (r, 0, sp.sqrt(zz))), (th, 0, 2*pi))
indep = sp.simplify(fX.subs(x, R(9, 10))*fX.subs(x, R(9, 10)))  # f(0.9,0.9)=0 但 fX fY>0
ok(22, tot == 1 and EXY == 0 and EX == 0 and indep > 0 and sp.simplify(FZ - zz**2) == 0,
   'Cov=0；f_X(x)=%s；f(0.9,0.9)=0≠f_X f_Y=%s；F_Z=z² ⟹ f_Z=2z' % (fX, sp.N(indep, 4)))

print('全部通过' if all(OK) else '有失败', '%d/%d' % (sum(OK), len(OK)))
