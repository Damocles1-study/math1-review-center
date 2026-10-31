from figs import fig, P, S, sin, cos, tan, exp, sqrt, log, atan, pi, circle3
import math


@fig('f15_area')
def _():
    p = P((-.3, 5.2), (-.3, 3.2), 250, 150)
    a, b = (3, .7), (1.2, 2)
    p.poly([(0, 0), a, (a[0] + b[0], a[1] + b[1]), b])
    p.arrow(0, 0, a[0], a[1], 'lr').arrow(0, 0, b[0], b[1], 'lb')
    p.line(a[0], a[1], a[0] + b[0], a[1] + b[1], 'ds').line(b[0], b[1], a[0] + b[0], a[1] + b[1], 'ds')
    p.text(a[0], a[1], 'α', dx=2, dy=13, cls='tx tr').text(b[0], b[1], 'β', dx=-11, dy=-1, cls='tx tb')
    p.text(1.7, 1.25, '面积 = |det|', dx=-14)
    return p()


@fig('f18_dep')
def _():
    p = P((-.3, 5.2), (-.3, 3.3), 250, 150)
    a, b = (3, .5), (.8, 1.2)
    k1, k2 = .9, 1.3
    c = (k1 * a[0] + k2 * b[0], k1 * a[1] + k2 * b[1])
    p.arrow(0, 0, a[0], a[1]).arrow(0, 0, b[0], b[1])
    p.arrow(0, 0, c[0], c[1], 'lr')
    p.line(k1 * a[0], k1 * a[1], c[0], c[1], 'ds').line(k2 * b[0], k2 * b[1], c[0], c[1], 'ds')
    p.text(a[0], a[1], 'α₁', dx=3, dy=8).text(b[0], b[1], 'α₂', dx=-16, dy=2).text(c[0], c[1], 'α₃', dx=3, dy=-2, cls='tx tr')
    return p()


@fig('f19_eig')
def _():
    p = P((-3.3, 3.3), (-2.6, 2.6), 280, 215, xname='', yname='', o=False)
    T = lambda v: (2 * v[0] + v[1], v[0] + 2 * v[1])
    p.param(cos, sin, 0, 2 * pi, 'ds')
    p.param(lambda t: 2 * cos(t) + sin(t), lambda t: cos(t) + 2 * sin(t), 0, 2 * pi)
    r = 1 / sqrt(2)
    for v, cls in [((r, r), 'lr'), ((-r, r), 'lb')]:
        w = T(v)
        p.arrow(0, 0, w[0], w[1], cls)
    p.text(3 * r, 3 * r, '3ξ₁', dx=4, dy=2, cls='tx tr').text(-r, r, 'ξ₂', dx=-16, dy=-2, cls='tx tb')
    v = (1, 0)
    w = T(v)
    p.arrow(0, 0, 1, 0, 'ln').arrow(0, 0, w[0], w[1], 'ln')
    p.text(w[0], w[1], 'Av', dx=4, dy=2).text(1, 0, 'v', dx=1, dy=13)
    return p()


@fig('f21_conic')
def _():
    p = P((-1.7, 1.7), (-1.5, 1.5), 240, 210)
    a, b = sqrt(2 / 3), sqrt(2)
    r = 1 / sqrt(2)
    p.param(lambda t: a * cos(t) * r - b * sin(t) * r, lambda t: a * cos(t) * r + b * sin(t) * r, 0, 2 * pi)
    p.line(-1.3 * r, -1.3 * r, 1.3 * r, 1.3 * r, 'lr').line(-1.6 * r, 1.6 * r, 1.6 * r, -1.6 * r, 'lb')
    p.text(1.3 * r, 1.3 * r, 'u', dx=3, dy=-2, cls='tx tr').text(1.6 * r, -1.6 * r, 'v', dx=2, dy=8, cls='tx tb')
    return p()


def _para(s, zmax=1.0, scale=1.6, hgt=1.7):
    # 旋转抛物面线框
    for z in [zmax, .55 * zmax, .2 * zmax]:
        r = sqrt(z / zmax) * scale
        s.path3(circle3((0, 0, z * hgt), r), 'ln' if z != zmax else 'cv')
    n = 40
    for sign in (1, -1):
        s.path3([(0, sign * scale * i / n, hgt * (i / n) ** 2) for i in range(n + 1)], 'cv')


@fig('f22_surf')
def _():
    a = S(lim=2.7, w=165, h=170)
    _para(a, scale=1.75, hgt=1.9)
    b = S(lim=2.7, w=165, h=170)
    h = 1.8
    b.path3(circle3((0, 0, h), 1.7), 'cv')
    b.path3(circle3((0, 0, h * .5), .85), 'ln')
    b.path3([(0, -1.7, h), (0, 0, 0), (0, 1.7, h)], 'cv')
    return '<div style="display:flex;gap:6px;justify-content:center">' + a().replace('<svg ', '<svg style="width:49%" ') + b().replace('<svg ', '<svg style="width:49%" ') + '</div>'


@fig('f24_lag')
def _():
    p = P((-3.6, 3.6), (-2.2, 2.2), 290, 180)
    p.param(lambda t: sqrt(8) * cos(t), lambda t: sqrt(2) * sin(t), 0, 2 * pi, 'cr')
    for c, cls in [(2, 'cv'), (.9, 'ds'), (3.4, 'ds')]:
        p.curve(lambda x: c / x, c / 2.2, 3.6, cls)
        p.curve(lambda x: c / x, -3.6, -c / 2.2, cls)
    p.pt(2, 1, 'xy=2', dx=7, dy=-4, cls='r')
    return p()


@fig('f25_xtype')
def _():
    p = P((-.15, 1.3), (-.15, 1.25), 220, 190)
    p.between(lambda x: x, lambda x: x * x, 0, 1)
    p.curve(lambda x: x, 0, 1.15).curve(lambda x: x * x, 0, 1.09)
    x = .55
    p.arrow(x, 0, x, x * 1.15, 'lr')
    p.pt(x, x * x, 'y=x²', dx=6, dy=11, cls='r').pt(x, x, 'y=x', dx=-27, dy=-3, cls='r')
    p.pt(1, 1, '(1,1)', dx=-34, dy=-3)
    p.text(x, 0, 'x', dx=-3, dy=14)
    return p()


@fig('f25_polar')
def _():
    p = P((-.3, 2.45), (-1.25, 1.25), 200, 195)
    p.param(lambda t: 1 + cos(t), sin, 0, 2 * pi)
    t = .6
    p.line(0, 0, 2 * cos(t) * cos(t), 2 * cos(t) * sin(t), 'lr')
    p.pt(2 * cos(t) ** 2, 2 * cos(t) * sin(t), 'r=2cos θ', dx=-40, dy=-7, cls='r')
    p.text(.42, .1, 'θ', dx=0, dy=-2)
    p.pt(1, 0, '1', dx=-3, dy=13).pt(2, 0, '2', dx=-11, dy=13)
    return p()


@fig('f26_para')
def _():
    s = S(lim=2.9, w=240, h=190)
    _para(s, scale=1.75, hgt=2.0)
    r = 1.75 * sqrt(.55)
    s.text3((0, 1.75, 2.0), 'z=1', dx=3, dy=-3)
    s.path3(circle3((0, 0, 1.1), r), 'cr')
    s.text3((0, r, 1.1), 'D_z', dx=4, dy=3, cls='tx tr')
    return s()


@fig('f26_sph')
def _():
    s = S(lim=2.8, w=240, h=190)
    P_ = (1.2, 1.3, 1.5)
    s.arrow3((0, 0, 0), P_, 'lr')
    s.path3([P_, (P_[0], P_[1], 0), (0, 0, 0)], 'ds')
    s.pt3(P_, 'M', dx=5, dy=-3, cls='r')
    s.text3((.6, .65, .75), 'ρ', dx=7, dy=-1, cls='tx tr')
    # 角弧
    n = 20
    r = .75
    s.path3([(r * sin(i * .85 / n) * .68, r * sin(i * .85 / n) * .74, r * cos(i * .85 / n)) for i in range(n + 1)], 'lb')
    s.text3((.1, .1, .85), 'φ', dx=5, dy=-1, cls='tx tb')
    th = atan(1.3 / 1.2)
    s.path3([(.7 * cos(i * th / n), .7 * sin(i * th / n), 0) for i in range(n + 1)], 'lb')
    s.text3((.75, .35, 0), 'θ', dx=-4, dy=13, cls='tx tb')
    return s()


@fig('f27_ds')
def _():
    s = S(lim=2.6, w=240, h=165)
    a, b = .55, 1.0
    q = [(a, .3, 0), (a + 1, .3, 0), (a + 1, 1.5, 0), (a, 1.5, 0)]
    up = [(x, y, 1.75 - .55 * x + .3 * y) for x, y, z in q]
    s.path3(up, 'fl', close=True)
    s.path3(up + [up[0]], 'cv')
    s.path3(q, 'fr', close=True)
    s.path3(q + [q[0]], 'lr')
    for u, v in zip(up, q):
        s.path3([u, v], 'ds')
    c = up[2]
    s.text3(up[0], 'dS', dx=-1, dy=-7)
    s.text3(q[2], 'dσ', dx=4, dy=10, cls='tx tr')
    return s()


@fig('f28_green')
def _():
    p = P((-1.4, 1.4), (-1.15, 1.15), 230, 180, axes=False)
    R = lambda t: 1 + .18 * cos(3 * t)
    p.param(lambda t: 1.1 * R(t) * cos(t), lambda t: .9 * R(t) * sin(t), 0, 2 * pi, 'cr')
    inside = lambda x, y: (x / 1.1) ** 2 + (y / .9) ** 2 < (1 + .18 * cos(3 * math.atan2(y / .9, x / 1.1))) ** 2
    h = .36
    for i in range(-4, 4):
        for j in range(-3, 3):
            x, y = i * h + .05, j * h + .08
            cs = [(x, y), (x + h, y), (x + h, y + h), (x, y + h)]
            if all(inside(*c) for c in cs):
                d = .035
                c2 = [(x + d, y + d), (x + h - d, y + d), (x + h - d, y + h - d), (x + d, y + h - d)]
                for q_ in range(4):
                    p.arrow(*c2[q_], *c2[(q_ + 1) % 4], 'ln')
    p.text(.75, -.95, 'L', dx=8, cls='tx tr')
    return p()


@fig('f29_gauss')
def _():
    s = S(lim=2.8, w=240, h=190)
    _para(s, scale=1.75, hgt=2.0)
    s.path3(circle3((0, 0, 2.0), 1.75), 'fr', close=True)
    s.arrow3((0, 0, 2.0), (0, 0, 2.9), 'lr')
    s.text3((0, 0, 2.7), 'Σ₁ 上侧', dx=6, cls='tx tr')
    s.arrow3((0, 1.05, .72), (0, 1.5, .25), 'lb')
    s.text3((0, 1.45, .25), 'Σ 下侧', dx=6, dy=4, cls='tx tb')
    return s()


@fig('f30_flow')
def _():
    w, h = 320, 200
    def box(x, y, bw, t, cls=''):
        return (f'<rect x="{x}" y="{y}" width="{bw}" height="24" fill="none" stroke="var(--ink)" stroke-width=".9"/>'
                f'<text x="{x+bw/2}" y="{y+16}" text-anchor="middle" style="font-style:normal;font-size:11px;font-family:var(--sans)" {cls}>{t}</text>')
    def ln(a, b, c, d):
        return f'<line class="ln" x1="{a}" y1="{b}" x2="{c}" y2="{d}" marker-end="url(#arr2)"/>'
    def lab(x, y, t):
        return f'<text x="{x}" y="{y}" style="font-style:normal;font-size:10px;font-family:var(--sans)">{t}</text>'
    e = ['<defs><marker id="arr2" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" orient="auto"><path class="arrh" d="M0 .8L7 4L0 7.2z"/></marker></defs>']
    e += [box(95, 4, 130, 'uₙ → 0 吗？'), ln(95, 16, 45, 16), box(4, 4, 42, '发散'), lab(60, 12, '否')]
    e += [ln(160, 28, 160, 50), lab(165, 42, '是'), box(95, 50, 130, '正项级数？')]
    e += [ln(130, 74, 80, 98), lab(90, 84, '是'), ln(190, 74, 240, 98), lab(222, 84, '否')]
    e += [box(4, 98, 155, '等价后比较 / 比值 / 根值'), box(170, 98, 146, '先取绝对值判断')]
    e += [ln(243, 122, 243, 148), lab(248, 138, '发散')]
    e += [box(170, 148, 146, '交错？用莱布尼茨'), lab(178, 190, '收敛 ⟹ 条件收敛')]
    return f'<svg viewBox="0 0 {w} {h}" role="img">' + ''.join(e) + '</svg>'


@fig('f31_abel')
def _():
    p = P((-3.3, 3.3), (-.6, .6), 300, 70, axes=False)
    p.line(-3.2, 0, -1.8, 0, 'ds').line(1.8, 0, 3.2, 0, 'ds')
    p.line(-1.8, 0, 1.8, 0, 'cr')
    p.pt(-1.8, 0, '−R', dx=-8, dy=-7, hollow=True).pt(1.8, 0, 'R', dx=-3, dy=-7, hollow=True).pt(0, 0, '0', dx=-3, dy=-7)
    p.text(-.9, 0, '绝对收敛', dy=15, dx=-8).text(2.2, 0, '发散', dy=15).text(-2.9, 0, '发散', dy=15)
    return p()


@fig('f31_fourier')
def _():
    p = P((-3.9, 3.9), (-3.9, 3.9), 280, 200)
    F = lambda x, N: sum(2 * (-1) ** (n + 1) / n * sin(n * x) for n in range(1, N + 1))
    p.curve(lambda x: F(x, 1), -3.8, 3.8, 'ds')
    p.curve(lambda x: F(x, 3), -3.8, 3.8, 'cb')
    p.curve(lambda x: F(x, 8), -3.8, 3.8, 'cr')
    p.line(-pi, -pi, pi, pi, 'cv')
    p.pt(pi, 0, 'π', dx=2, dy=14, hollow=True).pt(-pi, 0, '−π', dx=-13, dy=14, hollow=True)
    return p()


@fig('f32_geo')
def _():
    p = P((-.12, 1.2), (-.12, 1.2), 200, 190)
    k = 1 / 3
    p.poly([(0, 0), (k, 0), (1, 1 - k), (1, 1), (1 - k, 1), (0, k)], 'fr')
    p.path([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)], 'ln')
    p.line(0, k, 1 - k, 1, 'lr').line(k, 0, 1, 1 - k, 'lr')
    p.text(1, 0, '1', dx=-3, dy=13).text(0, 1, '1', dx=-10, dy=4).text(k, 0, '1/3', dx=-8, dy=13).text(0, k, '1/3', dx=-22, dy=4)
    return p()


@fig('f32_tree')
def _():
    w, h = 300, 150
    e = []
    def ln(a, b, c, d, t=None, red=False):
        cl = 'lr' if red else 'ln'
        e.append(f'<line class="{cl}" x1="{a}" y1="{b}" x2="{c}" y2="{d}"/>')
        if t:
            e.append(f'<text x="{(a+c)/2-6}" y="{(b+d)/2-3}" style="font-size:10.5px">{t}</text>')
    def tx(x, y, t):
        e.append(f'<text x="{x}" y="{y}">{t}</text>')
    pts = [(25, 75)]
    ys = [25, 75, 125]
    for i, y in enumerate(ys):
        ln(25, 75, 115, y, f'P(A{"₁₂₃"[i]})', i == 2)
        tx(118, y + 4, f'A{"₁₂₃"[i]}')
        ln(135, y, 225, y - 12 if True else y, f'P(B|A{"₁₂₃"[i]})', i == 2)
        ln(135, y, 225, y + 12)
        tx(229, y - 8, 'B')
        tx(229, y + 16, 'B̄')
    return f'<svg viewBox="0 0 {w} {h}" role="img">' + ''.join(e) + '</svg>'


@fig('f33_pdf')
def _():
    f = lambda x: .5 * x
    p = P((-.4, 2.8), (-.12, 1.2), 240, 130)
    p.between(f, lambda x: 0, 1, 2, 'fr')
    p.line(-.4, 0, 0, 0, 'cv').curve(f, 0, 2).line(2, 1, 2, 0, 'ds').line(2, 0, 2.7, 0, 'cv')
    p.text(1, 0, '1', dx=-3, dy=13).text(2, 0, '2', dx=-3, dy=13)
    p.text(1.4, .3, 'P', dx=-3, dy=3, cls='tx tr').text(1.25, .62, 'f(x)', dx=-30, dy=-2)
    return p()


@fig('f33_normal')
def _():
    phi = lambda x, s=1: exp(-x * x / (2 * s * s)) / (sqrt(2 * pi) * s)
    p = P((-4.4, 4.4), (-.05, .47), 300, 130, yname='', xname='x', o=False)
    p.between(phi, lambda x: 0, -1, 1, 'fr')
    p.curve(phi, -4.3, 4.3)
    p.curve(lambda x: phi(x, 1.8), -4.3, 4.3, 'ds')
    p.line(0, 0, 0, phi(0), 'ds')
    p.text(0, 0, 'μ', dx=-3, dy=13).text(-1, 0, 'μ−σ', dx=-14, dy=13).text(1, 0, 'μ+σ', dx=-10, dy=13)
    return p()


@fig('f34_region')
def _():
    p = P((-.15, 1.25), (-.15, 1.2), 210, 180)
    p.poly([(0, 0), (1, 1), (0, 1)], 'fl')
    p.poly([(0, 0), (.5, .5), (0, 1)], 'fr')
    p.line(0, 0, 1, 1).line(0, 1, 1, 1).line(0, 1, 1, 0, 'lr')
    p.text(.74, .74, 'y=x', dx=7, dy=7).text(.72, .28, 'x+y=1', dx=4, dy=-2, cls='tx tr')
    p.text(0, 1, '1', dx=-10, dy=4).text(1, 0, '1', dx=-3, dy=14)
    return p()


@fig('f36_clt')
def _():
    p = P((-3.3, 3.3), (-.04, .62), 280, 130, yname='', o=False)
    p.path([(-3.3, 0), (-1, 0), (-1, .5), (1, .5), (1, 0), (3.3, 0)], 'ds')
    p.path([(-3.3, 0), (-2, 0), (0, .5), (2, 0), (3.3, 0)], 'cb')
    def f4(x):
        y = (x + 4) / 2
        def F(t):
            return (t ** 3) / 6 if t > 0 else 0
        v = sum((-1) ** k * math.comb(4, k) * F(y - k) for k in range(5))
        return v / 2
    p.curve(f4, -3.3, 3.3, 'cr')
    p.text(1, .5, 'n=1', dx=2, dy=-2).text(.9, .28, 'n=2', dx=7, cls='tx tb').text(-1.2, .28, 'n=4', dx=-34, cls='tx tr')
    return p()
