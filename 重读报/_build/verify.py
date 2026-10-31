#!/usr/bin/env python3
"""独立复算：不读文稿，只把每道例题重新算一遍，再和文稿写下的最终答案比。分段运行：verify.py [起始期号] [终止期号]"""
import sys
from sympy import *
from sympy import Matrix as M
import mpmath as mp

x, y, z, t, r, n, u, v, a, b, c, k = symbols('x y z t r n u v a b c k', real=True)
th, ph, rho = symbols('theta phi rho', real=True)
OK, BAD = 0, []
lo = int(sys.argv[1]) if len(sys.argv) > 1 else 1
hi = int(sys.argv[2]) if len(sys.argv) > 2 else 99


def chk(tag, got, want, tol=1e-9):
    global OK
    try:
        d = abs(N(sympify(got) - sympify(want), 30))
        good = d < tol
    except Exception as e:
        good = False
        d = e
    if good:
        OK += 1
    else:
        BAD.append((tag, got, want, d))


def lim(e, var=x, to=0, d='+-'):
    if d == '+-':
        return limit(e, var, to, '+') if limit(e, var, to, '+') == limit(e, var, to, '-') else nan
    return limit(e, var, to, d)


def S(no):
    return lo <= no <= hi


pos = symbols('p', positive=True)
if S(1):
    e = (1 + 2 * exp(1 / x)) / (1 + exp(1 / x))
    chk('1.1+', limit(e, x, 0, '+'), 2)
    chk('1.1-', limit(e, x, 0, '-'), 1)
if S(2):
    chk('2.2', limit((x**2 - 4) / (x - 2), x, 2), 4)
    chk('2.3 x=1', limit((x**2 - 1) / (x**2 - x), x, 1), 2)
    chk('2.5 f0', (x**3 - 3 * x + 1).subs(x, 0), 1)
    chk('2.5 f1', (x**3 - 3 * x + 1).subs(x, 1), -1)
if S(3):
    chk('3.1', limit((sqrt(1 + x * sin(x)) - 1) / (x * atan(x)), x, 0), Rational(1, 2))
    chk('3.2', limit((tan(x) - sin(x)) / x**3, x, 0), Rational(1, 2))
    chk('3.3', limit(cos(x)**(1 / x**2), x, 0), exp(-Rational(1, 2)))
    chk('3.4', limit(sqrt(x**2 + x) - x, x, oo), Rational(1, 2))
    N_ = 200000
    chk('3.5', sum(1 / mp.sqrt(N_**2 + i) for i in range(1, N_ + 1)), 1, 1e-4)
    w = 1.0
    for _ in range(60):
        w = float(sqrt(2 + w))
    chk('3.6', w, 2, 1e-9)
if S(4):
    h = symbols('h')
    f = Function('f')
    chk('4.1', limit(x * sin(1 / x), x, 0), 0)
    fx = x**3 + 2 * x
    chk('4.3', limit((fx.subs(x, 1 + 2 * h) - fx.subs(x, 1 - h)) / h, h, 0), 3 * diff(fx, x).subs(x, 1))
if S(5):
    chk('5.1', simplify(diff(log(x + sqrt(1 + x**2)), x) - 1 / sqrt(1 + x**2)), 0)
    # 5.2 隐函数
    Y = Function('Y')
    F = exp(Y(x)) + x * Y(x) - E
    d1 = solve(diff(F, x), diff(Y(x), x))[0]
    d2 = diff(d1, x).subs(diff(Y(x), x), d1)
    chk('5.2 y1', d1.subs(Y(x), 1).subs(x, 0), -1 / E)
    chk('5.2 y2', d2.subs(Y(x), 1).subs(x, 0), 1 / E**2)
    X_, Y_ = log(1 + t**2), t - atan(t)
    dy = simplify(diff(Y_, t) / diff(X_, t))
    chk('5.3 dy', simplify(dy - t / 2), 0)
    chk('5.3 d2y', simplify(diff(dy, t) / diff(X_, t) - (1 + t**2) / (4 * t)), 0)
    chk('5.4', simplify(diff(x**sin(x), x) - x**sin(x) * (cos(x) * log(x) + sin(x) / x)), 0)
    for m in (1, 2, 3, 5):
        chk(f'5.5 n={m}', simplify(diff(x**2 * exp(x), x, m) - exp(x) * (x**2 + 2 * m * x + m * (m - 1))), 0)
if S(6):
    chk('6.3', limit((x - sin(x)) / x**3, x, 0), Rational(1, 6))
    chk('6.4', limit(x * log(x), x, 0, '+'), 0)
    chk('6.5', limit(1 / x**2 - 1 / (x * tan(x)), x, 0), Rational(1, 3))
if S(7):
    chk('7.1', limit((exp(x) * sin(x) - x - x**2) / x**3, x, 0), Rational(1, 3))
    s = series(x - (Rational(4, 3) - cos(x) / 3) * sin(x), x, 0, 7).removeO()
    chk('7.2 x', s.coeff(x, 1), 0)
    chk('7.2 x3', s.coeff(x, 3), 0)
    chk('7.2 x5', s.coeff(x, 5), Rational(1, 30))
    chk('7.3', diff(x**2 * exp(x), x, 5).subs(x, 0), 20)
if S(8):
    f = x**3 / (x - 1)**2
    chk('8.2 d1', simplify(diff(f, x) - x**2 * (x - 3) / (x - 1)**3), 0)
    chk('8.2 d2', simplify(diff(f, x, 2) - 6 * x / (x - 1)**4), 0)
    chk('8.2 min', f.subs(x, 3), Rational(27, 4))
    chk('8.2 a', limit(f / x, x, oo), 1)
    chk('8.2 b', limit(f - x, x, oo), 2)
    g = x * exp(1 / x)
    chk('8.1 a', limit(g / x, x, oo), 1)
    chk('8.1 b', limit(g - x, x, oo), 1)
    chk('8.3', (Abs(diff(x**2, x, 2)) / (1 + diff(x**2, x)**2)**Rational(3, 2)).subs(x, 0), 2)
if S(9):
    g = log(x) / x
    chk('9.3 max', g.subs(x, E), 1 / E)
    chk('9.3 lim', limit(g, x, oo), 0)
    chk('9.1', simplify(diff((1 + x) * log(1 + x) - atan(x), x) - log(1 + x) - x**2 / (1 + x**2)), 0)
if S(10):
    def anti(tag, F_, f_):
        chk(tag, simplify(diff(F_, x) - f_), 0)
    p_ = symbols('x', positive=True)
    chk('10.1a', simplify(diff(log(p_)**3 / 3, p_) - log(p_)**2 / p_), 0)
    anti('10.1b', atan((x + 1) / 2) / 2, 1 / (x**2 + 2 * x + 5))
    chk('10.2', simplify(diff(-sqrt(1 + p_**2) / p_, p_) - 1 / (p_**2 * sqrt(1 + p_**2))), 0)
    chk('10.3a', simplify(diff(p_**2 / 2 * log(p_) - p_**2 / 4, p_) - p_ * log(p_)), 0)
    anti('10.3b', x * atan(x) - log(1 + x**2) / 2, atan(x))
    anti('10.4', exp(x) * (sin(x) - cos(x)) / 2, exp(x) * sin(x))
    chk('10.5', simplify(diff(log(p_) - log(1 + p_**2) / 2, p_) - 1 / (p_ * (p_**2 + 1))), 0)
if S(11):
    chk('11.1', integrate(1 / (1 + x), (x, 0, 1)), log(2))
    chk('11.3', limit(integrate(sin(t), (t, 0, x**2)) / x**4, x, 0), Rational(1, 2))
    chk('11.5', integrate(x**3 + sqrt(1 - x**2), (x, -1, 1)), pi / 2)
    chk('11.6', integrate(x * sin(x), (x, 0, pi)), pi)
    chk('11.7', integrate(x * (1 - x), (x, 0, 1)) + integrate(x * (x - 1), (x, 1, 2)), 1)
    chk('11.8', integrate(sin(x)**4, (x, 0, pi / 2)), 3 * pi / 16)
if S(12):
    chk('12.1', integrate(1 / (x * (1 + x**2)), (x, 1, oo)), log(2) / 2)
    chk('12.2', integrate(log(x) / sqrt(x), (x, 0, 1)), -4)
    chk('12.3', integrate((1 + cos(th))**2, (th, 0, pi)), 3 * pi / 2)
    chk('12.4a', pi * integrate(sin(x)**2, (x, 0, pi)), pi**2 / 2)
    chk('12.4b', 2 * pi * integrate(x * sin(x), (x, 0, pi)), 2 * pi**2)
    chk('12.5', integrate(2 * sin(t / 2), (t, 0, 2 * pi)), 8)
if S(13):
    Y = Function('y')
    chk('13.1', simplify((3 * exp(x**2)).diff(x) - 2 * x * 3 * exp(x**2)), 0)
    X = symbols('x', positive=True)
    C1 = symbols('C')
    yy = X * asin(C1 * X)
    chk('13.2', simplify(X * diff(yy, X) - yy - X * (C1 * X) / sqrt(1 - C1**2 * X**2)), 0)
    yy = (pi - 1 - cos(X)) / X
    chk('13.3 ode', simplify(diff(yy, X) + yy / X - sin(X) / X), 0)
    chk('13.3 iv', yy.subs(X, pi), 1)
    yy = X * (1 - log(X))
    chk('13.4 ode', simplify(yy - X * diff(yy, X) - X), 0)
    chk('13.4 iv', yy.subs(X, 1), 1)
if S(14):
    yy = 1 / (1 - x)
    chk('14.1', simplify(diff(yy, x, 2) - 2 * yy * diff(yy, x)), 0)
    C_1, C_2 = symbols('C_1 C_2')
    yy = C_1 * exp(x) + C_2 * exp(2 * x) - (x**2 / 2 + x) * exp(x)
    chk('14.2', simplify(diff(yy, x, 2) - 3 * diff(yy, x) + 2 * yy - x * exp(x)), 0)
    yy = C_1 * cos(x) + C_2 * sin(x) + x / 2 * sin(x)
    chk('14.3', simplify(diff(yy, x, 2) + yy - cos(x)), 0)
    yy = C_1 * x + C_2 * x**2
    chk('14.4', simplify(x**2 * diff(yy, x, 2) - 2 * x * diff(yy, x) + 2 * yy), 0)
if S(15):
    chk('15.1', factor(M([[a, b, b, b], [b, a, b, b], [b, b, a, b], [b, b, b, a]]).det()) - (a + 3 * b) * (a - b)**3, 0)
    D = M([[1, 2, 3], [4, 5, 6], [7, 8, 10]])
    chk('15.2', sum(D.cofactor(0, j) for j in range(3)), 1)
    chk('15.3', M([[1, 1, 1], [1, 2, 3], [1, 4, 9]]).det(), 2)
    chk('15.4', M([[1, 1, 1], [1, 2, 0], [1, 0, 3]]).det(), 1)
if S(16):
    A = M([[1, 1], [2, 2]])
    chk('16.1', (A**5 - 3**4 * A).norm(), 0)
    A = M([[1, 0, 1], [2, 1, 0], [0, 1, 1]])
    chk('16.4', (A.inv() - M([[1, 1, -1], [-2, 1, 2], [2, -1, 1]]) / 3).norm(), 0)
    A = M([[3, 1], [0, 3]])
    X_ = (A - 2 * eye(2)).inv() * A
    chk('16.5', (X_ - M([[3, -2], [0, 3]])).norm(), 0)
    chk('16.5b', (A * X_ - A - 2 * X_).norm(), 0)
if S(17):
    a_ = symbols('a')
    chk('17.1', M([[1, 2, -1], [2, 5, 1], [1, 3, 2]]).rank(), 2)
    chk('17.2', (M([[1, 1, -1, -1], [2, 2, 1, 1]]) * M([-1, 1, 0, 0])).norm() + (M([[1, 1, -1, -1], [2, 2, 1, 1]]) * M([0, 0, -1, 1])).norm(), 0)
    A = M([[1, 1, a_], [1, a_, 1], [a_, 1, 1]])
    chk('17.3 det', expand(A.det() + (a_ + 2) * (a_ - 1)**2), 0)
    sol = M([-2, 1, 1]) / (a_ - 1)
    chk('17.3 uniq', simplify((A * sol - M([1, 1, -2])).norm()), 0)
    A1 = A.subs(a_, 1)
    chk('17.3 a=1', M.hstack(A1, M([1, 1, -2])).rank() - A1.rank(), 1)
    A2 = A.subs(a_, -2)
    chk('17.3 a=-2 p', (A2 * M([1, 0, 0]) - M([1, 1, -2])).norm(), 0)
    chk('17.3 a=-2 h', (A2 * M([1, 1, 1])).norm(), 0)
if S(18):
    chk('18.1', M([[1, 1, 1], [1, 2, 3], [1, 3, t]]).det() - (t - 5), 0)
    chk('18.2', M([[1, 0, 1], [1, 1, 0], [0, 1, 1]]).det(), 2)
    al = [M([1, 1, 1]), M([1, 2, 3]), M([2, 3, 4]), M([1, 0, -1])]
    chk('18.3 r', M.hstack(*al).rank(), 2)
    chk('18.3 a3', (al[2] - al[0] - al[1]).norm(), 0)
    chk('18.3 a4', (al[3] - 2 * al[0] + al[1]).norm(), 0)
    C = M([[1, 1], [0, 1]]).inv() * M([[1, 0], [2, 1]])
    chk('18.4', (C - M([[-1, -1], [2, 1]])).norm(), 0)
if S(19):
    A = M([[2, 0, 0], [1, 2, -1], [1, 0, 1]])
    lam = symbols('lambda')
    chk('19.1 char', expand(A.charpoly(lam).as_expr() - (lam - 2)**2 * (lam - 1)), 0)
    for v_, l in [(M([1, 0, 1]), 2), (M([0, 1, 0]), 2), (M([0, 1, 1]), 1)]:
        chk(f'19.1 v{l}', (A * v_ - l * v_).norm(), 0)
    chk('19.2a', 7 * 4 * 3, 84)
    A = M([[1, 1], [Rational(10, 3), Rational(4, 3)]])
    chk('19.3 det', A.det(), -2)
    chk('19.3 v', (A * M([1, 2]) - 3 * M([1, 2])).norm(), 0)
    chk('19.4', sorted(M([[1, 1, 1]] * 3).eigenvals().items())[0][1], 2)
if S(20):
    A = M([[2, 0, 0], [1, 2, -1], [1, 0, 1]])
    P = M([[1, 0, 0], [0, 1, 1], [1, 0, 1]])
    chk('20.2 inv', (P.inv() - M([[1, 0, 0], [1, 1, -1], [-1, 0, 1]])).norm(), 0)
    chk('20.2 diag', (P.inv() * A * P - diag(2, 2, 1)).norm(), 0)
    for m in (1, 2, 5):
        want = M([[2**m, 0, 0], [2**m - 1, 2**m, 1 - 2**m], [2**m - 1, 0, 1]])
        chk(f'20.2 A^{m}', (A**m - want).norm(), 0)
    A = M([[0, 1, 1], [1, 0, 1], [1, 1, 0]])
    Q = M([[1 / sqrt(3), -1 / sqrt(2), -1 / sqrt(6)], [1 / sqrt(3), 1 / sqrt(2), -1 / sqrt(6)], [1 / sqrt(3), 0, 2 / sqrt(6)]])
    chk('20.3 orth', simplify((Q.T * Q - eye(3)).norm()), 0)
    chk('20.3 diag', simplify((Q.T * A * Q - diag(2, -1, -1)).norm()), 0)
    B = M([[2, 1, 1], [1, 2, 1], [1, 1, 2]])
    chk('20.4 vals', sum(abs(l - w) for l, w in zip(sorted(B.eigenvals(multiple=True)), [1, 1, 4])), 0)
    chk('20.4 v', (B * M([1, 1, 1]) - 4 * M([1, 1, 1])).norm(), 0)
if S(21):
    x1, x2, x3 = symbols('x1 x2 x3')
    chk('21.2', expand(x1**2 + 2 * x1 * x2 + 2 * x2**2 + 4 * x2 * x3 + x3**2 - ((x1 + x2)**2 + (x2 + 2 * x3)**2 - 3 * x3**2)), 0)
    chk('21.3', sorted(M([[0, 1], [1, 0]]).eigenvals(multiple=True))[0], -1)
    A = M([[1, t, -1], [t, 1, 2], [-1, 2, 5]])
    chk('21.4', expand(A.det() + 5 * t**2 + 4 * t), 0)
if S(22):
    v1, v2 = M([-1, 1, 0]), M([-1, 0, 2])
    chk('22.1', (v1.cross(v2) - M([2, 2, 1])).norm(), 0)
    chk('22.2', (1 + Rational(3, 2)) + 3 + (-1 - Rational(3, 2)), 3)
if S(23):
    F1, F2 = Function('f')(u, v), None
    # 23.3 用具体 f 验证 z_xy 的通式
    f_ = u**3 * v + sin(u) * v**2
    U, V = x**2 - y**2, x * y
    z_ = f_.subs({u: U, v: V})
    fu, fv = diff(f_, u), diff(f_, v)
    fuu, fuv, fvv = diff(fu, u), diff(fu, v), diff(fv, v)
    sub = {u: U, v: V}
    want = (-4 * x * y * fuu + 2 * (x**2 - y**2) * fuv + x * y * fvv + fv).subs(sub)
    chk('23.3', simplify(diff(z_, x, y) - want), 0)
    # 23.4
    F = z**3 - 3 * x * y * z - 1
    zx, zy = -diff(F, x) / diff(F, z), -diff(F, y) / diff(F, z)
    chk('23.4 zx', zx.subs({x: 1, y: 0, z: 1}), 0)
    chk('23.4 zy', zy.subs({x: 1, y: 0, z: 1}), 1)
if S(24):
    f = x**3 + y**3 - 3 * x * y
    H = hessian(f, (x, y)).subs({x: 1, y: 1})
    chk('24.1 det', H.det(), 27)
    chk('24.1 val', f.subs({x: 1, y: 1}), -1)
    chk('24.1 sad', hessian(f, (x, y)).subs({x: 0, y: 0}).det(), -9)
    g = 8 - x**2 - 2 * x
    chk('24.3', g.subs(x, -1), 9)
    chk('24.3b', (x**2 + 2 * y**2 - 2 * x).subs({x: 1, y: 0}), -1)
    chk('24.4', (M([2, 2, 1]).dot(M([1, 2, 2]))) / 3, Rational(8, 3))
    vals = [(xx * yy) for xx, yy in [(2, 1), (-2, 1)]]
    chk('24.2', max(vals), 2)
    chk('24.5', 2 * 1 + 4 * 2 - 5, 5)
if S(25):
    chk('25.1', integrate(integrate(x * y, (y, x**2, x)), (x, 0, 1)), Rational(1, 24))
    chk('25.2', integrate(sin(y), (y, 0, 1)), 1 - cos(1))
    chk('25.3', integrate(integrate(r * r, (r, 0, 2 * cos(th))), (th, -pi / 2, pi / 2)), Rational(32, 9))
    chk('25.5', integrate(integrate(r**3 * sin(th)**2, (r, 0, 1)), (th, 0, 2 * pi)), pi / 4)
if S(26):
    chk('26.1', integrate(z * pi * z, (z, 0, 1)), pi / 3)
    chk('26.2', 2 * pi * integrate(r**3 * (1 - r**2), (r, 0, 1)), pi / 6)
    chk('26.3', 2 * pi * 2 * Rational(1, 5), 4 * pi / 5)
    I_ = 2 * pi * integrate(cos(ph) * sin(ph), (ph, 0, pi / 2)) * integrate(rho**3, (rho, 0, 1))
    chk('26.4', I_ / (2 * pi / 3), Rational(3, 8))
if S(27):
    chk('27.2', integrate(x * sqrt(1 + x**2), (x, 0, 1)), (2 * sqrt(2) - 1) / 3)
    chk('27.3', integrate(cos(t)**2 + cos(t) * sin(t), (t, 0, 2 * pi)), pi)
    chk('27.5', sqrt(2) * 2 * pi * Rational(1, 4), sqrt(2) * pi / 2)
if S(28):
    chk('28.1', integrate(x * x**2 + (x**2 - x) * 2 * x, (x, 0, 1)), Rational(1, 12))
    chk('28.2', integrate((1 - 2 * x) * (sqrt(x) - x**2), (x, 0, 1)), Rational(1, 30))
    # 28.3 直接数值积分复核：A(2,0)→O 上半圆，x=1+cos s, y=sin s, s 0→π
    P_ = lambda s: mp.e**(1 + mp.cos(s)) * mp.sin(mp.sin(s)) - 2 * mp.sin(s)
    Q_ = lambda s: mp.e**(1 + mp.cos(s)) * mp.cos(mp.sin(s)) - 2
    val = mp.quad(lambda s: P_(s) * (-mp.sin(s)) + Q_(s) * mp.cos(s), [0, mp.pi])
    chk('28.3', val, mp.pi, 1e-9)
    # 28.4 椭圆绕原点数值复核
    val = mp.quad(lambda s: (-(mp.sin(s) * 2) * (-3 * mp.sin(s)) + 3 * mp.cos(s) * 2 * mp.cos(s)) / ((3 * mp.cos(s))**2 + (2 * mp.sin(s))**2), [0, 2 * mp.pi])
    chk('28.4', val, 2 * mp.pi, 1e-9)
    chk('28.5', (x**2 * y + x * y**2).subs({x: 1, y: 2}), 6)
    chk('28.5b', diff(x**2 * y + x * y**2, x) - (2 * x * y + y**2), 0)
if S(29):
    chk('29.1', 2 * pi * integrate(sqrt(1 - r**2) * r, (r, 0, 1)), 2 * pi / 3)
    chk('29.2', 3 * 2 * pi * 2 * Rational(1, 5), 12 * pi / 5)
    chk('29.3', 3 * integrate(pi * z, (z, 0, 1)) - pi, pi / 2)
    # 29.4 直接参数化交线复核
    e1 = [1 / mp.sqrt(2), -1 / mp.sqrt(2), 0]
    e2 = [1 / mp.sqrt(6), 1 / mp.sqrt(6), -2 / mp.sqrt(6)]
    def pos(s):
        return [e1[i] * mp.cos(s) + e2[i] * mp.sin(s) for i in range(3)]
    def vel(s):
        return [-e1[i] * mp.sin(s) + e2[i] * mp.cos(s) for i in range(3)]
    val = mp.quad(lambda s: pos(s)[1] * vel(s)[0] + pos(s)[2] * vel(s)[1] + pos(s)[0] * vel(s)[2], [0, 2 * mp.pi])
    # e1×e2 的 z 分量决定走向：要求从 z 轴正向看逆时针
    nz = e1[0] * e2[1] - e1[1] * e2[0]
    if nz < 0:
        val = -val
    chk('29.4', val, -mp.sqrt(3) * mp.pi, 1e-9)
if S(30):
    chk('30.1', summation(1 / (n * (n + 1)), (n, 1, oo)), 1)
    chk('30.2c', summation(n / 2**n, (n, 1, oo)), 2)
if S(31):
    chk('31.2', series(1 / (x**2 - 3 * x + 2), x, 0, 5).removeO().coeff(x, 3), 1 - Rational(1, 16))
    chk('31.3', diff(log((1 + x) / (1 - x)) / 2, x).subs(x, Rational(1, 3)), 1 / (1 - Rational(1, 9)))
    chk('31.3b', sum(0.5**(2 * m - 1) / (2 * m - 1) for m in range(1, 60)), log(3) / 2, 1e-12)
    chk('31.4', summation(n / 2**n, (n, 1, oo)), 2)
    for m in (1, 2, 3):
        chk(f'31.5 b{m}', integrate(x * sin(m * x), (x, 0, pi)) * 2 / pi, 2 * (-1)**(m + 1) / Integer(m))
if S(32):
    chk('32.1', 1 - Rational(2, 3)**2, Rational(5, 9))
    p_ = 0.5 * 0.01 + 0.3 * 0.02 + 0.2 * 0.05
    chk('32.2a', p_, 0.021, 1e-12)
    chk('32.2b', 0.2 * 0.05 / p_, Rational(10, 21), 1e-12)
    chk('32.3', Rational(3, 5) * Rational(1, 2) + Rational(2, 5) * Rational(3, 4), Rational(3, 5))
    chk('32.5', 1 - 0.2 * 0.3 * 0.5, 0.97, 1e-12)
if S(33):
    chk('33.1', integrate(x / 2, (x, 1, 2)), Rational(3, 4))
    chk('33.3', 2 * (erf(1 / sqrt(2)) / 2 + Rational(1, 2)) - 1, 0.6826894921, 1e-6)
    y_ = symbols('y', positive=True)
    chk('33.5', integrate(Rational(1, 2), (x, -sqrt(y_), sqrt(y_))) - sqrt(y_), 0)
if S(34):
    f = 6 * x
    chk('34.2 c', integrate(integrate(x, (x, 0, y)), (y, 0, 1)), Rational(1, 6))
    chk('34.2 fx', simplify(integrate(f, (y, x, 1)) - 6 * x * (1 - x)), 0)
    chk('34.2 fy', simplify(integrate(f, (x, 0, y)) - 3 * y**2), 0)
    chk('34.2 P', integrate(integrate(f, (y, x, 1 - x)), (x, 0, Rational(1, 2))), Rational(1, 4))
    Z = symbols('z', positive=True)
    chk('34.3', simplify(integrate(exp(-x) * exp(-(Z - x)), (x, 0, Z)) - Z * exp(-Z)), 0)
if S(35):
    chk('35.1', 2 + 4, 6)
    chk('35.2a', integrate(2 * x**2, (x, 0, 1)), Rational(2, 3))
    chk('35.2b', integrate(2 * x**3, (x, 0, 1)) - Rational(4, 9), Rational(1, 18))
    chk('35.2c', integrate(2 * x * exp(x), (x, 0, 1)), 2)
    chk('35.3', integrate(x**3 / 2, (x, -1, 1)), 0)
    chk('35.4', 4 + 36 - 12, 28)
    fx, fy = 6 * x * (1 - x), 3 * y**2
    EX, EX2 = integrate(x * fx, (x, 0, 1)), integrate(x**2 * fx, (x, 0, 1))
    EY, EY2 = integrate(y * fy, (y, 0, 1)), integrate(y**2 * fy, (y, 0, 1))
    EXY = integrate(integrate(6 * x**2 * y, (y, x, 1)), (x, 0, 1))
    cov = EXY - EX * EY
    chk('35.5 cov', cov, Rational(1, 40))
    chk('35.5 rho', cov / sqrt((EX2 - EX**2) * (EY2 - EY**2)), sqrt(3) / 3)
if S(36):
    n_ = symbols('n', positive=True)
    chk('36.3', Rational(1, 2) * (1 + erf(1 / sqrt(2))), 0.8413447461, 1e-6)
    sig = symbols('s', positive=True)
    chk('36.5', simplify(2 * (n_ - 1) * sig**4 / (n_ - 1)**2 - 2 * sig**4 / (n_ - 1)), 0)
if S(37):
    th_ = symbols('theta', positive=True)
    chk('37.1 EX', integrate((th_ + 1) * x**(th_ + 1), (x, 0, 1)), (th_ + 1) / (th_ + 2))
    Xb = symbols('Xb')
    chk('37.1 m', simplify(solve(Eq((th_ + 1) / (th_ + 2), Xb), th_)[0] - (2 * Xb - 1) / (1 - Xb)), 0)
    Phi = lambda v_: (1 + mp.erf(v_ / mp.sqrt(2))) / 2
    chk('37.3', 4 / mp.sqrt(16) * 1.96, 1.96, 1e-9)
    chk('37.4', Phi(-0.04) - Phi(-3.96), 0.484, 1e-3)
    chk('37.4a', 2 * (1 - Phi(1.96)), 0.05, 1e-3)
print(f'通过 {OK} 项，失败 {len(BAD)} 项')
for b_ in BAD:
    print('  ✗', b_)
sys.exit(1 if BAD else 0)
