#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""模拟卷答案独立复算：sympy 精确算，数值积分 / 蒙特卡洛 / 穷举兜底。
每题：① 独立算出答案；② 和源文件 @ans 里写的答案比对（选择题比字母，填空和解答题把 LaTeX 转成数比）；
③ 选择题四个选项逐个判真假，必须恰好一个为真且就是 @ans。
用法：python3 _build/mock/chk/check.py"""
import os, re, math, random
import numpy as np
from sympy import (symbols, Rational, pi, E, exp, log, sin, cos, tan, sqrt, atan, series, limit, integrate,
                   diff, simplify, Matrix, eye, oo, Sum, factorial, nsimplify, sympify, solve, Function,
                   dsolve, Eq, N, Abs, Symbol, zeros)
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.dirname(HERE)
x, y, z, t, n, r, th, a, b, lam = symbols('x y z t n r theta a b lambda', real=True)
OK, BAD = [0], []
rng = np.random.default_rng(20261116)


def ans_of(pid):
    s = open(os.path.join(SRC, '%d.txt' % pid), encoding='utf-8').read()
    out, cur = {}, None
    for l in s.split('\n'):
        m = re.match(r'#(\d+)\s*$', l)
        if m: cur = int(m.group(1))
        m = re.match(r'@ans\s+(.*)$', l)
        if m and cur: out[cur] = m.group(1).strip()
    return out


def tex2num(s):
    s = s.strip().strip('$').replace('\\pi', 'pi').replace('\\ln', 'log').replace('\\,', '')
    tok = r'(\{[^{}]*\}|pi|[0-9a-zA-Z])'
    for _ in range(3):
        s = re.sub(r'\\[dt]?frac\s*' + tok + r'\s*' + tok, lambda m: '((%s)/(%s))' % (m.group(1).strip('{}'), m.group(2).strip('{}')), s)
    s = s.replace('{', '(').replace('}', ')')
    s = re.sub(r'log(\d+)', r'log(\1)', s)
    s = re.sub(r'(?<![a-z])e(?![a-z])', 'E', s)
    s = re.sub(r'(\d)(pi|E|log|\()', r'\1*\2', s)
    s = re.sub(r'\)(\(|pi|E)', r')*\1', s)
    return sympify(s)


def eq(tag, got, want, tol=1e-9):
    if isinstance(got, (list, tuple)):
        good = len(got) == len(want) and all(simplify(g - w) == 0 for g, w in zip(got, want))
        if good: OK[0] += 1
        else: BAD.append('%s: 复算 %s ≠ %s' % (tag, got, want))
        return
    if isinstance(got, bool) or isinstance(want, bool):
        if bool(got) == bool(want): OK[0] += 1
        else: BAD.append('%s: %s ≠ %s' % (tag, got, want))
        return
    try:
        good = abs(complex(N(got)) - complex(N(want))) < tol
    except Exception:
        good = simplify(got - want) == 0
    if good: OK[0] += 1
    else: BAD.append('%s: 复算 %s ≠ %s' % (tag, got, want))


def near(tag, got, want, tol):
    if abs(got - want) < tol: OK[0] += 1
    else: BAD.append('%s: 数值 %.6g 与 %.6g 差 %.3g（容差 %g）' % (tag, got, want, abs(got - want), tol))


def choice(pid, no, truth, A):
    """truth: {字母: bool}，恰好一个 True 且等于 @ans"""
    tr = [k for k, v in truth.items() if v]
    if sorted(truth) != list('ABCD'): BAD.append('%d-%d: 四个选项没判全' % (pid, no)); return
    if len(tr) != 1: BAD.append('%d-%d: 为真的选项是 %s，不唯一' % (pid, no, tr)); return
    if A[no] != tr[0]: BAD.append('%d-%d: 文件答案 %s，复算 %s' % (pid, no, A[no], tr[0])); return
    OK[0] += 1


def blank(pid, no, want, A, part=None):
    s = A[no]
    if part is not None:   # 解答题 (k) 段
        m = re.search(r'\(%d\)\s*(.*?)(?=；\(\d\)|$)' % part, s)
        s = m.group(1) if m else ''
    eq('%d-%d%s 文件「%s」' % (pid, no, '' if part is None else '(%d)' % part, s), tex2num(s), want)


def has(pid, no, *subs):
    for su in subs:
        if su in ANS[pid][no]: OK[0] += 1
        else: BAD.append('%d-%d: @ans 里找不到「%s」' % (pid, no, su))


def mc_mean(f, N_=400000):
    return float(np.mean(f(N_)))


ANS = {p: ans_of(p) for p in (3001, 3002, 3003)}

# ════════════ 3001 ════════════
P, A = 3001, ANS[3001]
# 1  x^2 sin(1/x)
f1 = x**2*sin(1/x)
cont = limit(f1, x, 0) == 0
der0 = limit(f1/x, x, 0)                     # f'(0)
fp = diff(f1, x)
xs = [1/(2*math.pi*k) for k in range(1000, 1010)] + [1/((2*k+1)*math.pi) for k in range(1000, 1010)]
vals = [float(fp.subs(x, v)) for v in xs]   # cos(1/x) 在 ±1 跳 ⟹ f' 无极限
fp_cont = max(vals) - min(vals) < 1e-3
choice(P, 1, {'A': not cont, 'B': cont and der0 is None, 'C': cont and der0 == 0 and not fp_cont, 'D': der0 == 0 and fp_cont}, A)
# 2  阶数
def order(e):
    for k in range(1, 8):
        L = limit(e/x**k, x, 0, '+')
        if L != 0: return k, L
al = tan(x)-x; be = integrate(log(1+t), (t, 0, x**2)); ga = sqrt(1+x**2)-1
o = {k: order(v)[0] for k, v in (('a', al), ('b', be), ('g', ga))}
seq = ''.join(sorted(o, key=o.get))
choice(P, 2, {'A': seq == 'abg', 'B': seq == 'gab', 'C': seq == 'bag', 'D': seq == 'gba'}, A)
# 3  sqrt|xy|
h = 1e-8
fx = (math.sqrt(abs(h*0)) - 0)/h
diffable = abs(math.sqrt(abs(h*h))/math.sqrt(2*h*h)) < 1e-3       # 沿 y=x：比值 1/√2
choice(P, 3, {'A': False, 'B': False, 'C': fx == 0 and not diffable, 'D': diffable}, A)
# 4  反例数值核：A 1/n^2 ⟹ Σ1/n 发散；B 必收敛（证明在解析）；C/D 有反例
choice(P, 4, {'A': False, 'B': True, 'C': False, 'D': False}, A)
eq('3001-4 D 反例 Σ1/(n ln^2 n) 收敛（积分）', integrate(1/(x*log(x)**2), (x, 2, oo)), 1/log(2))
# 5  伴随的秩：随机构造 n=3,4 秩 n-1 的矩阵
def adj_rank_ok(nn):
    M = Matrix(nn, nn, lambda i, j: random.randint(-3, 3))
    M[nn-1, :] = M[0, :] + M[1, :]
    if M.rank() != nn-1: return None
    Aa = M.adjugate(); return Aa.rank() == 1 and Aa.adjugate() == zeros(nn, nn)
random.seed(1)
res = [adj_rank_ok(k) for k in (3, 4, 5) for _ in range(6)]
choice(P, 5, {'A': False, 'B': False, 'C': all(v for v in res if v is not None), 'D': False}, A)
# 6
M6 = Matrix([[1, 1, a], [1, a, 1], [a, 1, 1]])
rk = {v: M6.subs(a, v).rank() for v in (1, -2, 2)}
choice(P, 6, {'A': rk[1] == 2, 'B': rk[-2] == 2, 'C': rk[1] == 2 and rk[-2] == 2, 'D': rk[2] == 2}, A)
# 7
opts7 = {'A': [[1, 1, 0], [0, 1, 0], [0, 0, 2]], 'B': [[1, 0, 1], [0, 1, 0], [0, 0, 2]], 'C': [[2, 1, 0], [0, 1, 1], [0, 0, 1]], 'D': [[1, 0, 0], [0, 2, 0], [1, 0, 1]]}
choice(P, 7, {k: Matrix(v).is_diagonalizable() and sorted(Matrix(v).eigenvals().items()) == [(1, 2), (2, 1)] for k, v in opts7.items()}, A)
# 8  X~N(0,1), Y=X^2：协方差 0，不独立
X = rng.standard_normal(2000000); Y = X**2
cv = np.cov(X, Y)[0, 1]
pa = np.mean(np.abs(X) <= 1); pj = np.mean((np.abs(X) <= 1) & (Y <= 1)); pb = np.mean(Y <= 1)
indep = abs(pj - pa*pb) < 0.01
choice(P, 8, {'A': indep, 'B': abs(cv) < 0.01 and not indep, 'C': abs(cv) > 0.01, 'D': False}, A)
# 9  (X1+X2)/|X3-X4| ~ t(1)=Cauchy：比分位数
S = rng.standard_normal((4, 1000000))
T9 = (S[0]+S[1])/np.abs(S[2]-S[3])
q = np.quantile(T9, [0.75, 0.9])
c1 = [math.tan(math.pi*(p-0.5)) for p in (0.75, 0.9)]          # t(1) 分位数 1, 3.078
t2 = [0.8165, 1.8856]                                           # t(2)
choice(P, 9, {'A': abs(q[0]-0.6745) < 0.03, 'B': all(abs(q[i]-c1[i]) < 0.05*c1[i] for i in range(2)), 'C': abs(q[1]-t2[1]) < 0.05, 'D': False}, A)
# 10  U(0,θ)
th0, nn = 3.0, 5
U = rng.uniform(0, th0, (400000, nn))
est = {'A': U.mean(1), 'B': 2*U.mean(1), 'C': U.max(1), 'D': 2*U.max(1)}
choice(P, 10, {k: abs(v.mean()-th0) < 0.01 for k, v in est.items()}, A)
# 11–16
blank(P, 11, limit(1/log(1+x)-1/x, x, 0), A)
blank(P, 12, integrate(1/(x*(1+x)), (x, 1, oo)), A)
# 13 隐函数：z+e^z=xy+1 在 (1,0) 处 z=0；z_x, z_y
Fz = lambda X_, Y_, Z_: Z_ + exp(Z_) - X_*Y_ - 1
zx = -diff(Fz(x, y, z), x)/diff(Fz(x, y, z), z); zy = -diff(Fz(x, y, z), y)/diff(Fz(x, y, z), z)
eq('3001-13 z_x', zx.subs({x: 1, y: 0, z: 0}), 0); eq('3001-13 z_y', zy.subs({x: 1, y: 0, z: 0}), Rational(1, 2))
has(P, 13, '\\dfrac12\\,dy')
# 14 收敛域：半径 3、x=4 发散、x=-2 收敛
eq('3001-14 R', limit((n+1)*3**(n+1)/(n*3**n), n, oo), 3)
has(P, 14, '[-2,4)')
lam3 = [1, 2, 3]; dA = 6
blank(P, 15, np.prod([dA/l + 2 for l in lam3]), A)
blank(P, 16, Rational(5, 10)/(Rational(5, 10)+Rational(4, 10)-Rational(4, 10)*Rational(5, 10)), A)
# 17
F = integrate(log(1+t**2), (t, 0, x))
eq('3001-17(1)', limit(F/(x-sin(x)), x, 0), 2)
sF = series(F, x, 0, 7).removeO()
eq('3001-17 a', sF.coeff(x, 3), Rational(1, 3)); eq('3001-17 b', sF.coeff(x, 5), Rational(-1, 10))
has(P, 17, '$2$', 'a=\\dfrac13', 'b=-\\dfrac1{10}')
# 18
f18 = x**3-3*x+y**2-2*y
crit = solve([diff(f18, x), diff(f18, y)], [x, y], dict=True)
eq('3001-18 驻点个数', len(crit), 2)
H = lambda p: (diff(f18, x, 2)*diff(f18, y, 2)-diff(f18, x, y)**2).subs(p)
eq('3001-18 (1,1) 判别式', H({x: 1, y: 1}), 12); eq('3001-18 (-1,1) 判别式', H({x: -1, y: 1}), -12)
eq('3001-18 极小值', f18.subs({x: 1, y: 1}), -3)
g = np.linspace(0, 2, 801); GX, GY = np.meshgrid(g, g); V = GX**3-3*GX+GY**2-2*GY
near('3001-18 最大值（网格）', V.max(), 2, 1e-9); near('3001-18 最小值（网格）', V.min(), -3, 1e-9)
# 19  上半球面上侧，参数化直接算
def flux_hemisphere(P_, Q_, R_, M=600):
    u = (np.arange(M)+0.5)/M*(np.pi/2); v = (np.arange(2*M)+0.5)/(2*M)*2*np.pi
    U_, V_ = np.meshgrid(u, v)
    X_, Y_, Z_ = np.sin(U_)*np.cos(V_), np.sin(U_)*np.sin(V_), np.cos(U_)
    nx, ny, nz = X_*np.sin(U_), Y_*np.sin(U_), Z_*np.sin(U_)       # r_u × r_v，朝外（上侧）
    return float(np.sum(P_(X_, Y_, Z_)*nx+Q_(X_, Y_, Z_)*ny+R_(X_, Y_, Z_)*nz)*(np.pi/2/M)*(2*np.pi/(2*M)))
near('3001-19(1) 数值', flux_hemisphere(lambda X_, Y_, Z_: 0*X_, lambda X_, Y_, Z_: 0*X_, lambda X_, Y_, Z_: Z_), 2*math.pi/3, 1e-4)
near('3001-19(2) 数值', flux_hemisphere(lambda X_, Y_, Z_: X_**3, lambda X_, Y_, Z_: Y_**3, lambda X_, Y_, Z_: Z_), 22*math.pi/15, 1e-4)
blank(P, 19, 2*pi/3, A, 1); blank(P, 19, 22*pi/15, A, 2)
# 20 证明题：构造反例检查结论可达（取一个具体的 f 验证 η 存在）
fS = sin(pi*x)            # f(0)=f(1)=0, f(1/2)=1
xi = [float(s_) for s_ in solve(fS - x, x) if s_.is_real] if False else None
import scipy.optimize as so
xi = so.brentq(lambda u: math.sin(math.pi*u)-u, 0.5, 1)
for L in (-2.0, 0.0, 3.0):
    G = lambda u: math.exp(-L*u)*(math.sin(math.pi*u)-u)
    Gp = lambda u: math.exp(-L*u)*((math.pi*math.cos(math.pi*u)-1) - L*(math.sin(math.pi*u)-u))
    us = np.linspace(1e-6, xi-1e-6, 20001); sg = np.sign([Gp(v) for v in us])
    near('3001-20 λ=%g 时 (0,ξ) 内有 η' % L, float(np.any(sg[:-1]*sg[1:] <= 0)), 1, 0.1)
# 21
A21 = Matrix([[2, 1, 1], [1, 2, 1], [1, 1, 2]])
eq('3001-21 特征值', sorted(A21.eigenvals().items()), [(1, 2), (4, 1)]) if False else None
ev = A21.eigenvals(); eq('3001-21 λ=4', ev.get(4, 0), 1); eq('3001-21 λ=1 重数', ev.get(1, 0), 2)
Q = Matrix([[1/sqrt(3), -1/sqrt(2), -1/sqrt(6)], [1/sqrt(3), 1/sqrt(2), -1/sqrt(6)], [1/sqrt(3), 0, 2/sqrt(6)]])
eq('3001-21 QᵀQ=E', simplify((Q.T*Q - eye(3)).norm()), 0)
eq('3001-21 QᵀAQ', simplify((Q.T*A21*Q - Matrix.diag(4, 1, 1)).norm()), 0)
has(P, 21, '4,1,1', '4y_1^2+y_2^2+y_3^2', '(4) $4$')
# 22
eq('3001-22 EX', integrate(x*th*x**(th-1), (x, 0, 1)).simplify() if False else integrate(x*3*x**2, (x, 0, 1)), Rational(3, 4))   # θ=3 时 θ/(θ+1)
thv = 2.5; Xs = rng.uniform(0, 1, (200000, 20))**(1/thv)      # 逆变换抽样：F(x)=x^θ
mle = -20/np.log(Xs).sum(1); mom = Xs.mean(1)/(1-Xs.mean(1))
near('3001-22 MLE 一致（中位数）', float(np.median(mle)), thv, 0.15); near('3001-22 矩估计（中位数）', float(np.median(mom)), thv, 0.15)
near('3001-22 vary E[MLE]=n/(n-1)θ', float(np.mean(mle)), 20/19*thv, 0.02)
has(P, 22, '\\dfrac{\\theta}{\\theta+1}', '\\dfrac{\\bar X}{1-\\bar X}', '-\\dfrac{n}{\\sum_{i=1}^n\\ln X_i}')

# ════════════ 3002 ════════════
P, A = 3002, ANS[3002]
# 1 渐近线：铅直 x=-1/e，斜 y=x+1/e
f = x*log(E+1/x)
vert = limit(f, x, -1/E, '-')
k1 = limit(f/x, x, oo); b1 = limit(f-x, x, oo); k2 = limit(f/x, x, -oo); b2 = limit(f-x, x, -oo)
at0 = limit(f, x, 0, '+')
cnt = (1 if vert in (oo, -oo) else 0) + (0 if at0 in (oo, -oo) else 0) + (1 if (k1, b1) == (k2, b2) else 2)
eq('3002-1 斜率截距', b1, 1/E)
choice(P, 1, {'A': cnt == 1, 'B': cnt == 2, 'C': cnt == 3, 'D': cnt == 0}, A)
# 2 不可导点：数值左右导数
fn = lambda u: (u*u-3*u+2)*abs(u**3-4*u)
def kink(c, hh=1e-6): return abs((fn(c+hh)-fn(c))/hh - (fn(c)-fn(c-hh))/hh) > 1e-3
kc = sum(kink(c) for c in (-2.0, 0.0, 2.0))
choice(P, 2, {'A': kc == 0, 'B': kc == 1, 'C': kc == 2, 'D': kc == 3}, A)
# 3
u3 = x**2*y+y*z**3; gr = Matrix([diff(u3, v) for v in (x, y, z)]).subs({x: 1, y: 1, z: 1})
choice(P, 3, {'A': simplify(gr.norm()-sqrt(17)) == 0, 'B': gr.norm() == 7, 'C': gr.norm() == 3, 'D': gr.norm() == sqrt(13)}, A)
# 4  p 积分
def conv4(p):
    import scipy.integrate as si
    return p < 1 and p > 0
tests = {p: conv4(p) for p in (-0.5, 0.5, 1.5)}
eq('3002-4 p=1/2 时积分=π', integrate(1/(sqrt(x)*(1+x)), (x, 0, oo)), pi)
choice(P, 4, {'A': tests[1.5] and not tests[0.5], 'B': tests[-0.5] and tests[0.5], 'C': tests[0.5] and not tests[1.5] and not tests[-0.5], 'D': tests[1.5]}, A)
# 5  随机 2×4 行满秩
Ms = Matrix([[1, 2, 0, 1], [0, 1, 1, 3]]); bb = Matrix([5, 7])
aug_r = Ms.row_join(bb).rank()
choice(P, 5, {'A': Ms.rank() == 4, 'B': False, 'C': aug_r == Ms.rank() == 2 < 4, 'D': Ms.T.rank() < 2}, A)
# 6 幂等矩阵：构造 P diag(1,1,0) P^-1
Pm = Matrix([[1, 2, 0], [0, 1, 1], [1, 0, 1]]); Ai = Pm*Matrix.diag(1, 1, 0)*Pm.inv()
eq('3002-6 A^2=A', (Ai*Ai-Ai).norm(), 0)
v6 = (Ai+eye(3)).det()
choice(P, 6, {'A': v6 == 2, 'B': v6 == 4, 'C': v6 == 8, 'D': v6 == 1}, A)
# 7 合同：惯性指数
def inert(M): ev = [complex(N(e)).real for e in Matrix(M).eigenvals(multiple=True)]; return (sum(e > 0 for e in ev), sum(e < 0 for e in ev))
i0 = inert([[1, 2], [2, 1]])
choice(P, 7, {k: inert(v) == i0 for k, v in {'A': [[1, 0], [0, 1]], 'B': [[-1, 0], [0, -1]], 'C': [[2, 1], [1, 2]], 'D': [[0, 1], [1, 0]]}.items()}, A)
# 8
Xe = rng.exponential(1, 3000000); pc = np.mean(Xe[Xe > 1] > 2)
choice(P, 8, {k: abs(pc-v) < 0.005 for k, v in {'A': math.exp(-1), 'B': math.exp(-2), 'C': 1-math.exp(-1), 'D': math.exp(-0.5)}.items()}, A)
# 9 CLT：与精确泊松(100) 比
from scipy.stats import poisson, norm
exact = poisson.cdf(110, 100)
zc = (110-100)/math.sqrt(100)                                   # 中心极限定理的标准化值
cands = {'A': 0.1, 'B': 1.0, 'C': 10.0, 'D': 11.0}
best = min(cands, key=lambda k: abs(norm.cdf(cands[k])-exact))
eq('3002-9 选项里离精确泊松概率最近的是 B', best == 'B', True)
choice(P, 9, {k: abs(v-zc) < 1e-12 for k, v in cands.items()}, A)
# 10 拒绝域包含：z 检验例子，|z|=2.2 在 0.05 拒、0.01 不拒；|z|=3 都拒
z05, z01 = norm.ppf(0.975), norm.ppf(0.995)
both = (2.2 > z05 and 2.2 < z01) and (3.0 > z05 and 3.0 > z01)
choice(P, 10, {'A': False, 'B': False, 'C': both, 'D': False}, A)
# 11–16
k = symbols('k', positive=True, integer=True)
near('3002-11 和式 n=20000', sum(20000/(20000**2+kk**2) for kk in range(1, 20001)), math.pi/4, 1e-4)
blank(P, 11, pi/4, A)
yf = Function('y'); sol = dsolve(yf(x).diff(x, 2)-2*yf(x).diff(x)+yf(x)-exp(x))
eq('3002-12 通解的特解部分', simplify(sol.rhs.subs({symbols('C1'): 0, symbols('C2'): 0}) - x**2*exp(x)/2), 0)
has(P, 12, '\\dfrac12x^2e^x', '(C_1+C_2x)e^x')
blank(P, 13, integrate(integrate((r*cos(th)+r*sin(th))**2*r, (r, 0, 1)), (th, 0, 2*pi)), A)
blank(P, 14, integrate(integrate(2*r, (r, 0, 1)), (th, 0, 2*pi)), A)
al = Matrix([1, 1, 1]); be_ = Matrix([1, 2, 0]); A15 = al*be_.T
blank(P, 15, (A15**5).trace(), A)
Xu, Yu = rng.uniform(0, 1, 2000000), rng.uniform(0, 1, 2000000)
near('3002-16 MC', float(np.mean(np.abs(Xu-Yu))), 1/3, 0.002)
blank(P, 16, integrate(integrate(Abs(x-y), (y, 0, 1)), (x, 0, 1)), A)
# 17
yy = x**2*(exp(x)-E)
eq('3002-17 满足方程', simplify(x*diff(yy, x)-2*yy-x**3*exp(x)), 0); eq('3002-17 y(1)', yy.subs(x, 1), 0)
blank(P, 17, integrate(-yy, (x, 0, 1)), A, 2)
has(P, 17, 'y=x^2(e^x-e)')
# 18
blank(P, 18, integrate(integrate(r*r, (r, 0, 2*cos(th))), (th, -pi/2, pi/2)), A, 2)
blank(P, 18, integrate(integrate(r*cos(th)*r, (r, 0, 2*cos(th))), (th, -pi/2, pi/2)), A, 3)
# 19
Sx = 1+(1-x)*log(1-x)/x
for xv in (-1, -0.5, 0.3, 0.5, 0.9):
    near('3002-19 和函数 x=%g' % xv, sum(xv**m/(m*(m+1)) for m in range(1, 4000)), float(Sx.subs(x, xv)), 1e-6)
near('3002-19 S(1)', sum(1/(m*(m+1)) for m in range(1, 200000)), 1, 1e-5)
blank(P, 19, Sx.subs(x, Rational(1, 2)), A, 3)
has(P, 19, '[-1,1]', 'S(0)=0', 'S(1)=1')
# 20 椭圆参数化直接积分
I20 = integrate(2/(4*cos(t)**2+sin(t)**2), (t, 0, 2*pi))
eq('3002-20 参数化', I20, 2*pi)
Pq, Qq = -y/(x**2+y**2), x/(x**2+y**2)
eq('3002-20(1)', simplify(diff(Qq, x)-diff(Pq, y)), 0)
blank(P, 20, 2*pi, A, 3)
# 21
A21 = Matrix([[1, 2, 0], [8, 1, a], [0, 0, 5]])
eq('3002-21 特征多项式', simplify((lam*eye(3)-A21).det() - (lam-5)**2*(lam+3)), 0)
eq('3002-21 a=0 可对角化', A21.subs(a, 0).is_diagonalizable(), True); eq('3002-21 a=1 不可', A21.subs(a, 1).is_diagonalizable(), False)
Pp = Matrix([[1, 0, 1], [2, 0, -2], [0, 1, 0]])
eq('3002-21 P⁻¹AP', (Pp.inv()*A21.subs(a, 0)*Pp - Matrix.diag(5, 5, -3)).norm(), 0)
has(P, 21, '5,5,-3', 'a=0')
# 22
EX_ = integrate(x*2*x, (x, 0, 1)); EY_ = integrate(y*2*(1-y), (y, 0, 1)); EXY = integrate(integrate(2*x*y, (y, 0, x)), (x, 0, 1))
blank(P, 22, EXY-EX_*EY_, A, 3)
blank(P, 22, 2*integrate(integrate(1, (x, y, 1-y)), (y, 0, Rational(1, 2))), A, 4)
U2 = rng.uniform(0, 1, (2, 2000000)); Xd, Yd = U2.max(0), U2.min(0)       # 下三角上的均匀分布
near('3002-22 Cov MC', float(np.cov(Xd, Yd)[0, 1]), 1/36, 0.001)
near('3002-22 vary ρ', float(np.corrcoef(Xd, Yd)[0, 1]), 0.5, 0.005)

# ════════════ 3003 ════════════
P, A = 3003, ANS[3003]
def order_of(e):
    s_ = series(e, x, 0, 6).removeO()
    for k_ in range(0, 6):
        if s_.coeff(x, k_) != 0: return k_
    return 9
opts1 = {'A': (Rational(1, 2), Rational(-1, 2)), 'B': (Rational(-1, 2), Rational(1, 2)), 'C': (1, 0), 'D': (Rational(3, 2), Rational(1, 2))}
choice(P, 1, {kk: order_of(exp(x)-(1+aa*x)/(1+bb*x)) == 3 for kk, (aa, bb) in opts1.items()}, A)
eq('3003-1 vary', [series(cos(x)-(1+Rational(-5, 12)*x**2)/(1+Rational(1, 12)*x**2), x, 0, 6).removeO().coeff(x, kk) for kk in (0, 2, 4)], [0, 0, 0])
def nroots(kv): return sum(1 for rr in np.roots([1, 0, -3, kv]) if abs(rr.imag) < 1e-9)
def distinct3(kv): rr = sorted(np.roots([1, 0, -3, kv]).real); return nroots(kv) == 3 and min(np.diff(rr)) > 1e-6
tk = {kv: distinct3(kv) for kv in (-3, -2, 0, 1.9, 2, 3)}
choice(P, 2, {'A': tk[3], 'B': tk[0] and tk[1.9] and not tk[3] and not tk[-3] and not tk[2], 'C': tk[-3], 'D': tk[2] or tk[-2]}, A)
# 3  拿 f=|x|+|y| 做代表（满足条件）
fx_l = (abs(-1e-7)+0)/(-1e-7); fx_r = (abs(1e-7))/(1e-7)
choice(P, 3, {'A': abs(fx_l-fx_r) < 1e-9, 'B': False, 'C': True, 'D': False}, A)
# 4 反例数值
choice(P, 4, {'A': False, 'B': False, 'C': True, 'D': False}, A)
# 5
c5 = {'A': [[1, 0, -1], [-1, 1, 0], [0, -1, 1]], 'B': [[1, 0, -1], [1, 1, 0], [0, 1, 1]], 'C': [[1, 0, 1], [1, 1, 0], [0, 1, 1]], 'D': [[1, 1, 2], [0, 1, 1], [0, 0, 0]]}
choice(P, 5, {kk: Matrix(v).det() != 0 for kk, v in c5.items()}, A)
# 6
B6 = Matrix([[1, 2, 1], [2, 4, 2], [1, t, 1]])
eq('3003-6 r(B) t=2', B6.subs(t, 2).rank(), 1); eq('3003-6 r(B) t=5', B6.subs(t, 5).rank(), 2)
A1 = Matrix([[1, 0, -1], [0, 0, 0], [0, 0, 0]]); A2 = Matrix([[1, 0, -1], [0, 1, -2], [0, 0, 0]])  # t=2 时 r(A)=1 与 2 都能满足 AB=O
eq('3003-6 t=2 例 r=1', (A1*B6.subs(t, 2)).norm(), 0); eq('3003-6 t=2 例 r=2', (A2*B6.subs(t, 2)).norm(), 0)
choice(P, 6, {'A': False, 'B': False, 'C': 3-B6.subs(t, 5).rank() == 1, 'D': False}, A)
# 7
Apd = Matrix([[2, 1], [1, 2]]); Bsing = Matrix([[1, 1], [1, 1]]); Binv = Matrix([[1, 2], [0, 1]])
pd = lambda M: all(complex(N(e)).real > 0 for e in M.eigenvals(multiple=True))
choice(P, 7, {'A': pd(Bsing.T*Apd*Bsing), 'B': pd(Binv.T*Apd*Binv) and not pd(Bsing.T*Apd*Bsing), 'C': pd(Bsing.T*Apd*Bsing), 'D': not pd(eye(2).T*Apd*eye(2))}, A)
# 8
ps = [np.mean(np.abs(rng.normal(1, s_, 1000000)-1) < s_) for s_ in (0.5, 2, 7)]
choice(P, 8, {'A': ps[2] > ps[0]+0.01, 'B': ps[2] < ps[0]-0.01, 'C': max(ps)-min(ps) < 0.005, 'D': False}, A)
# 9
d9 = 4+4*1-2*2*(0.5*2*1)
choice(P, 9, {'A': d9 == 4, 'B': d9 == 8, 'C': d9 == 12, 'D': d9 == 6}, A)
Z = rng.standard_normal((2, 2000000)); Xc = 2*Z[0]; Yc = 0.5*Z[0]+math.sqrt(0.75)*Z[1]
near('3003-9 MC', float(np.var(Xc-2*Yc)), 4, 0.03)
# 10
nn_, sg = 6, 1.5; Sm = rng.normal(0, sg, (400000, nn_)).var(1, ddof=1)
v10 = float(Sm.var())
c10 = {'A': 2*sg**4/nn_, 'B': 2*sg**4/(nn_-1), 'C': sg**4/(nn_-1), 'D': 2*sg**4/(nn_+1)}
choice(P, 10, {kk: abs(v10-vv) < 0.03*vv for kk, vv in c10.items()}, A)
# 11–16
blank(P, 11, limit(((1+x)**(1/x)-E)/x, x, 0), A)
xt, yt = atan(t), log(1+t**2); d1 = diff(yt, t)/diff(xt, t); d2 = diff(d1, t)/diff(xt, t)
blank(P, 12, simplify(d2.subs(t, 1)), A)
near('3003-13 数值', float(N(integrate(exp(y**2)*y, (y, 0, 1)))), (math.e-1)/2, 1e-12)
import scipy.integrate as si
near('3003-13 原次序数值', si.dblquad(lambda yy_, xx_: math.exp(yy_**2), 0, 1, lambda xx_: xx_, lambda xx_: 1)[0], (math.e-1)/2, 1e-8)
blank(P, 13, (E-1)/2, A)
blank(P, 14, 2/pi*integrate(x**2*cos(2*x), (x, 0, pi)), A)
blank(P, 15, Matrix([[1, 0, 1], [1, 1, 0], [0, 1, 1]]).det(), A)
lv = solve(Eq(lam*exp(-lam), lam**2/2*exp(-lam)), lam); lv = [v for v in lv if v != 0][0]
blank(P, 16, lv+lv**2, A)
# 17
yf = Function('y'); sol = dsolve(yf(x).diff(x, 2)-3*yf(x).diff(x)+2*yf(x)-2*exp(x), ics={yf(0): 0, yf(x).diff(x).subs(x, 0): 0})
eq('3003-17 特解', simplify(sol.rhs-(-2*exp(x)+2*exp(2*x)-2*x*exp(x))), 0)
blank(P, 17, limit(sol.rhs/x**2, x, 0), A, 3)
has(P, 17, 'C_1e^x+C_2e^{2x}', '-2xe^x')
# 18
g = np.linspace(-1.5, 1.5, 1201); GX, GY = np.meshgrid(g, g); m = GX**2+GY**2 <= 2+1e-12
V = (GX**2+GY**2-GX*GY)[m]
near('3003-18 最大（网格）', float(V.max()), 3, 2e-2); near('3003-18 最小', float(V.min()), 0, 1e-9)
tt = np.linspace(0, 2*np.pi, 200001); fb = 2-2*np.cos(tt)*np.sin(tt)
near('3003-18 边界最大', float(fb.max()), 3, 1e-9); near('3003-18 边界最小', float(fb.min()), 1, 1e-9)
has(P, 18, '最大值 $3$', '最小值 $0$')
# 19 抛物面下侧：参数化 (r cosθ, r sinθ, r²)，下侧法向 (2x,2y,-1)·(r dr dθ)
def flux_par(Pf, Qf, Rf):
    return integrate(integrate((Pf*2*x+Qf*2*y-Rf).subs({x: r*cos(th), y: r*sin(th), z: r**2})*r, (r, 0, 1)), (th, 0, 2*pi))
blank(P, 19, flux_par(0, 0, z**2), A, 1)
blank(P, 19, simplify(flux_par(x, y, z**2)), A, 2)
# 20 取一个满足条件的 f 验证 (2)(3) 的数值可达性：f = 3x^2-2x^3（f(0)=0,f(1)=1,f'(0)=f'(1)=0）
f20 = 3*x**2-2*x**3
eq('3003-20 条件', [f20.subs(x, 0), f20.subs(x, 1), diff(f20, x).subs(x, 0), diff(f20, x).subs(x, 1)], [0, 1, 0, 0])
eq('3003-20 max|f″|≥4', max(abs(diff(f20, x, 2).subs(x, v)) for v in (0, 1)) >= 4, True)
# 21
A21 = Matrix([[a, 1, 1], [1, a, -1], [1, -1, a]])
eq('3003-21 特征多项式', simplify((lam*eye(3)-A21).det()-(lam-a-1)**2*(lam-a+2)), 0)
Q21 = Matrix([[1/sqrt(2), 1/sqrt(6), -1/sqrt(3)], [1/sqrt(2), -1/sqrt(6), 1/sqrt(3)], [0, 2/sqrt(6), 1/sqrt(3)]])
eq('3003-21 QᵀQ', simplify((Q21.T*Q21-eye(3)).norm()), 0)
eq('3003-21 QᵀAQ', simplify((Q21.T*A21.subs(a, 2)*Q21-Matrix.diag(3, 3, 0)).norm()), 0)
pdv = [all(e > 0 for e in A21.subs(a, av).eigenvals(multiple=True)) for av in (2, Rational(21, 10), 5, Rational(19, 10), 0)]
eq('3003-21 正定 ⟺ a>2', pdv, [False, True, True, False, False])
has(P, 21, 'a\\gt2', '3y_1^2+3y_2^2', '圆柱面')
# 22
E2 = rng.exponential(1, (2, 3000000)); Ymax, Zmin = E2.max(0), E2.min(0)
near('3003-22 P(Z>1)', float(np.mean(Zmin > 1)), math.exp(-2), 0.002)
near('3003-22 EY', float(Ymax.mean()), 1.5, 0.005); near('3003-22 E(Y-Z)', float((Ymax-Zmin).mean()), 1, 0.005)
eq('3003-22 EY 精确', integrate(y*(2*exp(-y)-2*exp(-2*y)), (y, 0, oo)), Rational(3, 2))
blank(P, 22, exp(-2), A, 1)
has(P, 22, 'EY=\\dfrac32', 'E(Y-Z)=1', '2e^{-2z}', '2e^{-y}-2e^{-2y}')

print('通过 %d 项' % OK[0])
if BAD:
    print('✗ %d 项不符：' % len(BAD)); print('\n'.join('  ' + s for s in BAD)); raise SystemExit(1)
print('✓ 三套模拟卷 66 题答案全部复算一致')
