"""按真实函数算出来的标准图（黑白 + 少量专色）。颜色全走 CSS 变量，夜读模式自动反相。"""
import math

FIG = {}


def fig(name):
    def deco(fn):
        FIG[name] = fn
        return fn
    return deco


class P:
    """二维坐标图"""

    def __init__(self, xlim, ylim, w=300, h=200, axes=True, xname='x', yname='y', o=True):
        self.xl, self.yl, self.w, self.h = xlim, ylim, w, h
        self.pad = 10
        self.el = []
        if axes:
            x0 = 0 if xlim[0] <= 0 <= xlim[1] else xlim[0]
            y0 = 0 if ylim[0] <= 0 <= ylim[1] else ylim[0]
            self.arrow(xlim[0], y0, xlim[1], y0)
            self.arrow(x0, ylim[0], x0, ylim[1])
            self.text(xlim[1], y0, xname, dx=-7, dy=14)
            self.text(x0, ylim[1], yname, dx=8, dy=8)
            if o and x0 == 0 and y0 == 0:
                self.text(0, 0, 'O', dx=-11, dy=13)

    def X(self, x):
        return self.pad + (x - self.xl[0]) / (self.xl[1] - self.xl[0]) * (self.w - 2 * self.pad)

    def Y(self, y):
        return self.h - self.pad - (y - self.yl[0]) / (self.yl[1] - self.yl[0]) * (self.h - 2 * self.pad)

    def arrow(self, a, b, c, d, cls='ax'):
        self.el.append(f'<line class="{cls}" x1="{self.X(a):.1f}" y1="{self.Y(b):.1f}" x2="{self.X(c):.1f}" y2="{self.Y(d):.1f}" marker-end="url(#arr)"/>')
        return self

    def line(self, a, b, c, d, cls='ln'):
        self.el.append(f'<line class="{cls}" x1="{self.X(a):.1f}" y1="{self.Y(b):.1f}" x2="{self.X(c):.1f}" y2="{self.Y(d):.1f}"/>')
        return self

    def dash(self, a, b, c, d):
        return self.line(a, b, c, d, 'ds')

    def path(self, pts, cls='cv', close=False):
        seg, cur = [], []
        for (x, y) in pts:
            if y is None or x is None or abs(y) > 1e6 or y != y or y < self.yl[0] - (self.yl[1] - self.yl[0]) or y > self.yl[1] + (self.yl[1] - self.yl[0]):
                if cur:
                    seg.append(cur)
                cur = []
            else:
                cur.append((x, y))
        if cur:
            seg.append(cur)
        for s in seg:
            d = 'M' + ' L'.join(f'{self.X(x):.1f} {self.Y(y):.1f}' for x, y in s) + (' Z' if close else '')
            self.el.append(f'<path class="{cls}" d="{d}"/>')
        return self

    def curve(self, f, a=None, b=None, cls='cv', n=240):
        a = self.xl[0] if a is None else a
        b = self.xl[1] if b is None else b
        pts = []
        for i in range(n + 1):
            x = a + (b - a) * i / n
            try:
                pts.append((x, f(x)))
            except (ValueError, ZeroDivisionError, OverflowError):
                pts.append((x, None))
        return self.path(pts, cls)

    def param(self, fx, fy, t0, t1, cls='cv', n=320):
        return self.path([(fx(t0 + (t1 - t0) * i / n), fy(t0 + (t1 - t0) * i / n)) for i in range(n + 1)], cls)

    def between(self, f, g, a, b, cls='fl', n=160):
        up = [(a + (b - a) * i / n, f(a + (b - a) * i / n)) for i in range(n + 1)]
        lo = [(a + (b - a) * i / n, g(a + (b - a) * i / n)) for i in range(n, -1, -1)]
        return self.path(up + lo, cls, close=True)

    def poly(self, pts, cls='fl'):
        return self.path(pts, cls, close=True)

    def pt(self, x, y, label=None, dx=6, dy=-5, hollow=False, cls=''):
        self.el.append(f'<circle class="{"ho" if hollow else "pt"} {cls}" cx="{self.X(x):.1f}" cy="{self.Y(y):.1f}" r="2.6"/>')
        if label:
            self.text(x, y, label, dx, dy)
        return self

    def text(self, x, y, s, dx=0, dy=0, cls='tx'):
        self.el.append(f'<text class="{cls}" x="{self.X(x)+dx:.1f}" y="{self.Y(y)+dy:.1f}">{s}</text>')
        return self

    def __call__(self):
        return (f'<svg viewBox="0 0 {self.w} {self.h}" role="img"><defs><marker id="arr" viewBox="0 0 8 8" refX="7" refY="4" '
                f'markerWidth="7" markerHeight="7" orient="auto"><path class="arrh" d="M0 .8L7 4L0 7.2z"/></marker></defs>'
                + ''.join(self.el) + '</svg>')


class S(P):
    """斜二测三维示意：(x,y,z) → 平面。x 轴朝左下，y 朝右，z 朝上"""

    def __init__(self, lim=3.2, w=300, h=220, names=('x', 'y', 'z')):
        super().__init__((-lim, lim), (-lim * h / w, lim * h / w), w, h, axes=False)
        self.lim = lim
        L = lim * 0.92
        self.arrow3((0, 0, 0), (L, 0, 0))
        self.arrow3((0, 0, 0), (0, L, 0))
        self.arrow3((0, 0, 0), (0, 0, L * 0.72))
        for v, n in zip([(L, 0, 0), (0, L, 0), (0, 0, L * .72)], names):
            a, b = self.pr(v)
            self.text(a, b, n, dx=4, dy=-3)
        self.text(0, 0, 'O', dx=-11, dy=12)

    @staticmethod
    def pr(v):
        x, y, z = v
        return (y - 0.42 * x, z - 0.42 * x)

    def arrow3(self, a, b, cls='ax'):
        A, B = self.pr(a), self.pr(b)
        return self.arrow(A[0], A[1], B[0], B[1], cls)

    def path3(self, pts, cls='cv', close=False):
        return self.path([self.pr(p) for p in pts], cls, close)

    def pt3(self, v, label=None, **k):
        a, b = self.pr(v)
        return self.pt(a, b, label, **k)

    def text3(self, v, s, **k):
        a, b = self.pr(v)
        return self.text(a, b, s, **k)


pi = math.pi
sin, cos, tan, exp, sqrt, log, atan = math.sin, math.cos, math.tan, math.exp, math.sqrt, math.log, math.atan


def circle3(c, r, plane='xy', n=120):
    out = []
    for i in range(n + 1):
        t = 2 * pi * i / n
        a, b = r * cos(t), r * sin(t)
        if plane == 'xy':
            out.append((c[0] + a, c[1] + b, c[2]))
        elif plane == 'yz':
            out.append((c[0], c[1] + a, c[2] + b))
        else:
            out.append((c[0] + a, c[1], c[2] + b))
    return out


import figs_a  # noqa: E402,F401
import figs_b  # noqa: E402,F401
