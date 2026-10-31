from figs import fig, P, S, sin, cos, tan, exp, sqrt, log, atan, pi, circle3
import math


@fig('f01_exp_log')
def _():
    p = P((-3, 4.2), (-3, 4.2), 280, 260)
    p.line(-3, -3, 4.2, 4.2, 'ds')
    p.curve(exp, -3, 1.44)
    p.curve(log, 0.02, 4.1, 'cr')
    p.pt(0, 1, '1', dx=-11, dy=2).pt(1, 0, '1', dx=-2, dy=14)
    p.text(1.25, 3.5, 'y=eˣ', dx=-44, dy=0)
    p.text(3.1, log(3.1), 'y=ln x', dx=-12, dy=-8, cls='tx tr')
    return p()


@fig('f01_arctan')
def _():
    p = P((-7, 7), (-2.1, 2.1), 300, 150)
    p.dash(-7, pi / 2, 7, pi / 2).dash(-7, -pi / 2, 7, -pi / 2)
    p.curve(atan)
    p.text(-6.6, pi / 2, 'π/2', dy=-4).text(3.8, -pi / 2, '−π/2', dy=13)
    p.text(3.4, atan(3.4), 'y=arctan x', dy=16, dx=2)
    return p()


@fig('f02_disc')
def _():
    p = P((0, 12), (-1, 3.5), 320, 135, axes=False)
    # 可去
    p.arrow(0, 0, 3.5, 0)
    p.curve(lambda x: 0.8 + 0.5 * x, 0.2, 3)
    p.pt(1.7, 0.8 + 0.85, hollow=True)
    p.pt(1.7, 2.6)
    p.text(0.7, 0, '可去', dy=26)
    # 跳跃
    p.arrow(4.2, 0, 7.7, 0)
    p.curve(lambda x: 0.8 + .1 * (x - 4.4), 4.4, 5.9)
    p.curve(lambda x: 2.2 + .15 * (x - 5.9), 5.9, 7.4)
    p.pt(5.9, 0.95, hollow=True).pt(5.9, 2.2)
    p.text(5, 0, '跳跃', dy=26)
    # 无穷
    p.arrow(8.4, 0, 11.9, 0)
    p.curve(lambda x: 0.5 / abs(x - 10.1), 8.6, 10.0)
    p.curve(lambda x: 0.5 / abs(x - 10.1), 10.2, 11.7)
    p.dash(10.1, -0.6, 10.1, 3.4)
    p.text(9.4, 0, '无穷', dy=26)
    return p()


@fig('f02_ivt')
def _():
    f = lambda x: -1 + 0.9 * x - 0.35 * sin(2.2 * x)
    p = P((-.4, 4.4), (-1.9, 3.3), 280, 150)
    p.curve(f, 0.3, 4)
    a, b = 0.3, 4
    p.dash(a, 0, a, f(a)).dash(b, 0, b, f(b))
    p.text(a, 0, 'a', dx=-2, dy=-5).text(b, 0, 'b', dx=-2, dy=14)
    lo, hi = a, b
    for _i in range(40):
        m = (lo + hi) / 2
        if f(m) > 0:
            hi = m
        else:
            lo = m
    p.pt(lo, 0, 'ξ', dy=14, dx=-2, cls='r')
    return p()


@fig('f03_sinx')
def _():
    p = P((-.25, 1.5), (-.2, 1.65), 250, 225, axes=True)
    x = 0.85
    p.param(cos, sin, 0, pi / 2, 'cv')
    P_ = (cos(x), sin(x))
    T_ = (1, tan(x))
    p.line(0, 0, T_[0], T_[1])
    p.line(1, 0, T_[0], T_[1], 'lr')
    p.line(P_[0], 0, P_[0], P_[1], 'lb')
    p.pt(1, 0, 'A', dx=4, dy=14).pt(*P_, 'P', dx=-12, dy=-3).pt(*T_, 'T', dx=6, dy=2)
    p.text(.38, .12, 'x', dx=0, dy=0)
    p.text(P_[0], .3, 'sin x', dx=-32, dy=0, cls='tx tb')
    p.text(1, .7, 'tan x', dx=5, cls='tx tr')
    return p()


@fig('f04_tangent')
def _():
    f = lambda x: 0.28 * x * x + 0.4
    p = P((-.3, 4.4), (-.3, 5.4), 280, 180)
    p.curve(f, 0, 4.2)
    a, b = 1.3, 3.3
    k = 0.56 * a
    p.curve(lambda x: f(a) + k * (x - a), 0, 4.2, 'cr')
    p.curve(lambda x: f(a) + (f(b) - f(a)) / (b - a) * (x - a), 0.5, 4, 'cb')
    p.pt(a, f(a)).pt(b, f(b))
    p.dash(a, f(a), b, f(a)).dash(b, f(a), b, f(b))
    p.text((a + b) / 2, f(a), 'Δx', dy=13).text(b, (f(a) + f(b)) / 2, 'Δy', dx=4)
    p.text(3.75, f(a) + k * 2.45, '切线', dx=-2, dy=15, cls='tx tr').text(3.3, f(b), '割线', dx=-36, dy=-2, cls='tx tb')
    return p()


@fig('f04_diff')
def _():
    f = lambda x: 0.28 * x * x + 0.4
    p = P((-.3, 4.4), (-.3, 5.4), 280, 180)
    p.curve(f, 0, 4.2)
    a, b = 1.3, 3.5
    k = .56 * a
    p.curve(lambda x: f(a) + k * (x - a), 0.2, 4.2, 'cr')
    tan_y = f(a) + k * (b - a)
    p.pt(a, f(a)).pt(b, f(b)).pt(b, tan_y)
    p.dash(a, f(a), b, f(a))
    p.line(b - .04, f(a), b - .04, tan_y, 'lr')
    p.line(b + .04, f(a), b + .04, f(b), 'lb')
    p.text(b, (f(a) + tan_y) / 2, 'dy', dx=-17, cls='tx tr')
    p.text(b, (tan_y + f(b)) / 2, 'o(Δx)', dx=5, dy=3)
    p.text((a + b) / 2, f(a), 'Δx=dx', dy=13, dx=-16)
    return p()


@fig('f06_mvt')
def _():
    f = lambda x: -0.32 * (x - 2.2) ** 2 + 0.05 * (x - 1) ** 3 + 3
    p = P((-.3, 4.6), (-.3, 4.2), 280, 165)
    a, b = .5, 4.1
    p.curve(f, a, b)
    k = (f(b) - f(a)) / (b - a)
    p.line(a, f(a), b, f(b), 'lb')
    # 找 xi
    lo, hi = a, b
    d = lambda x: (f(x + 1e-5) - f(x - 1e-5)) / 2e-5 - k
    best = min((abs(d(a + (b - a) * i / 400)), a + (b - a) * i / 400) for i in range(1, 400))[1]
    p.curve(lambda x: f(best) + k * (x - best), .1, 4.4, 'cr')
    p.pt(a, f(a), 'A', dx=-12, dy=-2).pt(b, f(b), 'B', dx=4, dy=-3).pt(best, f(best), 'ξ', dx=-2, dy=-6, cls='r')
    p.dash(best, 0, best, f(best)).dash(a, 0, a, f(a)).dash(b, 0, b, f(b))
    p.text(a, 0, 'a', dx=-3, dy=14).text(b, 0, 'b', dx=-3, dy=14).text(best, 0, 'ξ', dx=-3, dy=14, cls='tx tr')
    return p()


@fig('f07_taylor')
def _():
    p = P((-4.6, 4.6), (-2.2, 2.2), 300, 165)
    p.curve(lambda x: x, -2.2, 2.2, 'ds')
    p.curve(lambda x: x - x ** 3 / 6, -3.5, 3.5, 'cb')
    p.curve(lambda x: x - x ** 3 / 6 + x ** 5 / 120, -4.3, 4.3, 'cr')
    p.curve(sin)
    p.text(1.75, 1.9, '1阶', dx=4, dy=2).text(3.1, -1.9, '3阶', dx=5, cls='tx tb').text(-4.3, -1.2, '5阶', dx=-1, dy=-6, cls='tx tr')
    return p()


@fig('f08_concave')
def _():
    f = lambda x: 0.12 * (x - 2) ** 3 + 2
    p = P((-.2, 4.3), (.6, 3.4), 280, 140, axes=False)
    p.curve(f, 0, 4)
    p.curve(lambda x: f(1) + .36 * (x - 1), 0.1, 1.9, 'lb')
    p.curve(lambda x: f(3) + .36 * (x - 3), 2.1, 3.9, 'lb')
    p.pt(2, 2, '拐点', dx=7, dy=12, cls='r')
    p.text(.45, f(.45), '∩ 上凸  f″<0', dx=5, dy=26)
    p.text(2.7, f(2.7), '∪ 下凸  f″>0', dx=-36, dy=-36)
    return p()


@fig('f08_graph')
def _():
    f = lambda x: x ** 3 / (x - 1) ** 2
    p = P((-6, 8), (-8, 16), 300, 240)
    p.curve(f, -6, .78)
    p.curve(f, 1.28, 8)
    p.dash(1, -8, 1, 16)
    p.curve(lambda x: x + 2, -6, 8, 'lb')
    p.pt(3, 27 / 4, '极小 (3, 27/4)', dx=-10, dy=18, cls='r').pt(0, 0, '拐点', dx=-30, dy=-6, cls='r')
    p.text(1, 15, 'x=1', dx=5, dy=5).text(6.3, 8.3, 'y=x+2', dx=-40, dy=9, cls='tx tb')
    return p()


@fig('f09_lnx')
def _():
    g = lambda x: log(x) / x
    p = P((-.4, 12), (-.9, .75), 290, 150)
    p.curve(g, .55, 12)
    p.dash(-.4, 1 / math.e, 12, 1 / math.e).dash(math.e, 0, math.e, 1 / math.e)
    p.line(-.4, .2, 12, .2, 'lr')
    p.pt(math.e, 1 / math.e, 'y=1/e', dx=5, dy=-5).text(math.e, 0, 'e', dx=-3, dy=14)
    p.text(10.5, .2, 'y=k', dy=-4, cls='tx tr')
    return p()


@fig('f10_tri')
def _():
    p = P((-.3, 4.6), (-.3, 3.3), 220, 130, axes=False)
    p.line(0, 0, 4, 0).line(4, 0, 4, 2.6).line(0, 0, 4, 2.6, 'lr')
    p.line(3.75, 0, 3.75, .25).line(3.75, .25, 4, .25)
    p.text(2, 0, 'a', dy=14).text(4, 1.3, 'x', dx=5).text(2, 1.3, '√(a²+x²)', dx=-44, dy=-6, cls='tx tr').text(.55, .1, 't', dy=-2)
    return p()


@fig('f11_riemann')
def _():
    f = lambda x: .25 * x * x + .8
    p = P((-.3, 4.5), (-.3, 5.4), 270, 165)
    n = 8
    for i in range(n):
        a = .5 + 3.5 * i / n
        b = a + 3.5 / n
        m = (a + b) / 2
        p.poly([(a, 0), (a, f(m)), (b, f(m)), (b, 0)])
        p.line(a, 0, a, f(m)).line(b, 0, b, f(m)).line(a, f(m), b, f(m))
    p.curve(f, .2, 4.3, 'cr')
    p.text(.5, 0, 'a', dx=-3, dy=14).text(4, 0, 'b', dx=-3, dy=14)
    return p()


@fig('f12_polar')
def _():
    r = lambda t: 1 + cos(t)
    p = P((-.75, 2.35), (-1.6, 1.6), 240, 200, yname='', xname='极轴', o=False)
    p.param(lambda t: r(t) * cos(t), lambda t: r(t) * sin(t), 0, 2 * pi)
    t1, t2 = .75, .95
    n = 20
    pts = [(0, 0)] + [(r(t1 + (t2 - t1) * i / n) * cos(t1 + (t2 - t1) * i / n), r(t1 + (t2 - t1) * i / n) * sin(t1 + (t2 - t1) * i / n)) for i in range(n + 1)]
    p.poly(pts, 'fr')
    p.line(0, 0, pts[1][0], pts[1][1], 'lr').line(0, 0, pts[-1][0], pts[-1][1], 'lr')
    p.text(pts[-1][0], pts[-1][1], 'r(θ)', dx=4, dy=-3, cls='tx tr')
    p.text(0, 0, 'O', dx=-11, dy=13)
    return p()


@fig('f12_shell')
def _():
    p = P((-.35, 8.1), (-1.45, 1.75), 330, 150)
    # 左：圆片
    p.curve(sin, 0, pi)
    p.curve(lambda x: -sin(x), 0, pi, 'ds')
    x = 1.25
    h = sin(x)
    p.line(x, -h, x, h, 'lr').line(x + .28, -sin(x + .28), x + .28, sin(x + .28), 'lr')
    p.param(lambda t: x + .1 * cos(t), lambda t: h * sin(t), 0, 2 * pi, 'lr')
    p.param(lambda t: x + .28 + .1 * cos(t), lambda t: sin(x + .28) * sin(t), 0, 2 * pi, 'lr')
    p.text(x, .3, 'y', dx=-11, dy=0, cls='tx tr')
    p.arrow(-.3, 0, 3.6, 0)
    p.text(1.0, -1.4, '绕 x 轴：圆片 πy²dx', dx=-26, dy=0)
    # 右：柱壳
    ox = 6.0
    p.arrow(ox, -.5, ox, 1.7)
    p.arrow(ox - 2.0, 0, ox + 2.05, 0)
    g = lambda u: .95 * sin(u * pi / 1.9)
    p.curve(lambda t: g(t - ox), ox, ox + 1.9)
    u = 1.0
    h2 = g(u)
    for sx in (1, -1):
        p.line(ox + sx * u, 0, ox + sx * u, h2, 'lr')
    p.param(lambda t: ox + u * cos(t), lambda t: .13 * sin(t), 0, 2 * pi, 'lr')
    p.param(lambda t: ox + u * cos(t), lambda t: h2 + .13 * sin(t), 0, 2 * pi, 'lr')
    p.text(ox + u, h2, 'y', dx=3, dy=-6, cls='tx tr')
    p.text(ox + u, 0, 'x', dx=-3, dy=14, cls='tx tr')
    p.text(ox - .35, -1.4, '绕 y 轴：柱壳 2πxy dx', dx=-40, dy=0)
    return p()
