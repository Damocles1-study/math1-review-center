# -*- coding: utf-8 -*-
"""纸笔手绘风 SVG。线条有抖动、起笔收笔有出头、曲线只取几个关键点再连，刻意不追求程序式的精确。
用法：s=Sk(320,180,seed=3); s.axes(...); s.line(...); s.text(...); s.svg()"""
import math,random,re
INK={'k':'#2b2a28','p':'#55524c','r':'#b3362b','b':'#27508f','g':'#8a857a','y':'#d9a62e'}
def esc(t): return t.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
class Sk:
    def __init__(s,w,h,seed=None):
        s.w,s.h=w,h;s.o=[];s.R=random.Random(seed if seed is not None else w*1000+h)
    # 抖动 ---------------------------------------------------------
    def _noise(s,n,amp):
        a=[(s.R.uniform(.5,1.6),s.R.uniform(0,6.28)) for _ in range(3)]
        return [amp*sum(math.sin(f*i*.55+p) for f,p in a)/2 for i in range(n)]
    def _wob(s,pts,amp=.9,step=14):
        out=[]
        for (x0,y0),(x1,y1) in zip(pts,pts[1:]):
            d=math.hypot(x1-x0,y1-y0);n=max(1,int(d/step))
            for i in range(n): out.append((x0+(x1-x0)*i/n,y0+(y1-y0)*i/n))
        out.append(pts[-1]);nx=s._noise(len(out),amp);ny=s._noise(len(out),amp)
        return [(x+a,y+b) for (x,y),a,b in zip(out,nx,ny)]
    def _path(s,p):
        if len(p)<3: return 'M'+' L'.join('%.1f %.1f'%q for q in p)
        d='M%.1f %.1f'%p[0]
        for i in range(1,len(p)-1):
            mx,my=(p[i][0]+p[i+1][0])/2,(p[i][1]+p[i+1][1])/2
            d+=' Q%.1f %.1f %.1f %.1f'%(p[i][0],p[i][1],mx,my)
        return d+' L%.1f %.1f'%p[-1]
    def _st(s,d,c='k',w=1.25,op=.92,dash=None,fill='none'):
        x=' stroke-dasharray="%s"'%dash if dash else ''
        s.o.append('<path d="%s" fill="%s" stroke="%s" stroke-width="%.2f" stroke-linecap="round" stroke-linejoin="round" opacity="%.2f"%s/>'%(d,fill,INK.get(c,c),w,op,x))
    # 基本笔画 -------------------------------------------------------
    def poly(s,pts,c='k',w=1.25,amp=.9,dash=None,twice=False):
        s._st(s._path(s._wob(pts,amp)),c,w,dash=dash)
        if twice: s._st(s._path(s._wob(pts,amp*1.2)),c,w*.7,.45,dash=dash)
    def line(s,x0,y0,x1,y1,c='k',w=1.25,dash=None,over=True):
        d=math.hypot(x1-x0,y1-y0) or 1;e=s.R.uniform(.5,2.2) if over else 0
        ux,uy=(x1-x0)/d,(y1-y0)/d
        s.poly([(x0-ux*e,y0-uy*e),(x1+ux*e,y1+uy*e)],c,w,dash=dash,amp=min(1.0,.4+d/200))
    def arrow(s,x0,y0,x1,y1,c='k',w=1.25,dash=None,head=7):
        s.line(x0,y0,x1,y1,c,w,dash,over=False);a=math.atan2(y1-y0,x1-x0)
        for da in (2.65,-2.65):
            da+=s.R.uniform(-.1,.1)
            s.poly([(x1,y1),(x1+head*math.cos(a+da),y1+head*math.sin(a+da))],c,w,amp=.2)
    def bend(s,x0,y0,x1,y1,k=20,c='k',w=1.25,dash=None,arrow=True):
        """带弧度的引线"""
        mx,my=(x0+x1)/2,(y0+y1)/2;d=math.hypot(x1-x0,y1-y0) or 1
        cx,cy=mx-(y1-y0)/d*k,my+(x1-x0)/d*k
        pts=[((1-t)**2*x0+2*t*(1-t)*cx+t*t*x1,(1-t)**2*y0+2*t*(1-t)*cy+t*t*y1) for t in [i/10 for i in range(11)]]
        s.poly(pts,c,w,dash=dash,amp=.6)
        if arrow:
            a=math.atan2(y1-cy,x1-cx)
            for da in (2.65,-2.65): s.poly([(x1,y1),(x1+7*math.cos(a+da),y1+7*math.sin(a+da))],c,w,amp=.2)
    def curve(s,pts,c='k',w=1.35,amp=.7,dash=None):
        """过几个关键点的手画曲线（Catmull-Rom 插值后再抖）"""
        P=[pts[0]]+list(pts)+[pts[-1]];out=[]
        for i in range(1,len(P)-2):
            p0,p1,p2,p3=P[i-1],P[i],P[i+1],P[i+2]
            for j in range(6):
                t=j/6;t2=t*t;t3=t2*t
                out.append(tuple(.5*(2*p1[k]+(p2[k]-p0[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t2+(3*p1[k]-p0[k]-3*p2[k]+p3[k])*t3) for k in (0,1)))
        out.append(pts[-1])
        s._st(s._path(s._wob(out,amp,step=9)),c,w,dash=dash)
    def plot(s,f,x0,x1,X,Y,n=9,c='k',w=1.35,jit=.8,dash=None):
        """按函数取几个描点再徒手连，不是逐像素画；X、Y 把数学坐标映到纸上"""
        pts=[]
        for i in range(n+1):
            x=x0+(x1-x0)*i/n
            try:y=f(x)
            except Exception:continue
            pts.append((X(x)+s.R.uniform(-jit,jit)*.4,Y(y)+s.R.uniform(-jit,jit)))
        s.curve(pts,c,w,dash=dash)
    def axes(s,ox,oy,x0,x1,y0,y1,xl='x',yl='y',o=True,c='k'):
        """以 (ox,oy) 为原点，x0..x1、y0..y1 是纸上坐标范围"""
        s.arrow(x0,oy,x1,oy,c,1.1);s.arrow(ox,y0,ox,y1,c,1.1)
        if xl: s.text(x1-2,oy+15,xl,13,c,'middle')
        if yl: s.text(ox+11,y1+6,yl,13,c,'middle')
        if o: s.text(ox-9,oy+14,'O',12,c,'middle')
    def box(s,x,y,w,h,c='k',lw=1.2,dash=None,fill=None):
        if fill: s.o.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" opacity=".55"/>'%(x+1,y+1,w-2,h-2,fill))
        s.line(x,y,x+w,y,c,lw,dash);s.line(x+w,y,x+w,y+h,c,lw,dash);s.line(x+w,y+h,x,y+h,c,lw,dash);s.line(x,y+h,x,y,c,lw,dash)
    def circle(s,cx,cy,r,c='k',w=1.2,ry=None,dash=None,fill=None):
        ry=ry or r;a0=s.R.uniform(0,6.28);n=max(14,int(r*1.5));ov=.35
        pts=[(cx+r*math.cos(a0+(6.28+ov)*i/n)*(1+.012*i/n),cy+ry*math.sin(a0+(6.28+ov)*i/n)*(1+.012*i/n)) for i in range(n+1)]
        if fill: s.o.append('<ellipse cx="%.1f" cy="%.1f" rx="%.1f" ry="%.1f" fill="%s" opacity=".6"/>'%(cx,cy,r,ry,fill))
        s._st(s._path(s._wob(pts,.35,step=6)),c,w,dash=dash)
    def dot(s,x,y,r=2.2,c='k',hollow=False):
        if hollow: s.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="#fbf8f0" stroke="%s" stroke-width="1.1"/>'%(x,y,r+.8,INK.get(c,c)))
        else: s.o.append('<circle cx="%.1f" cy="%.1f" r="%.1f" fill="%s"/>'%(x+s.R.uniform(-.3,.3),y+s.R.uniform(-.3,.3),r,INK.get(c,c)))
    def hatch(s,poly,gap=7,c='p',w=.8,ang=-45):
        """给多边形打斜线阴影（铅笔排线，长短不齐）"""
        a=math.radians(ang);ca,sa=math.cos(a),math.sin(a)
        r=[(x*ca+y*sa,-x*sa+y*ca) for x,y in poly];v0=min(p[1] for p in r);v1=max(p[1] for p in r);v=v0+gap/2
        while v<v1:
            xs=[]
            for (x0,y0),(x1,y1) in zip(r,r[1:]+r[:1]):
                if (y0-v)*(y1-v)<0: xs.append(x0+(v-y0)/(y1-y0)*(x1-x0))
            xs.sort()
            for i in range(0,len(xs)-1,2):
                u0,u1=xs[i]+s.R.uniform(-1,1.5),xs[i+1]+s.R.uniform(-1.5,1)
                s.poly([(u0*ca-v*sa,u0*sa+v*ca),(u1*ca-v*sa,u1*sa+v*ca)],c,w,amp=.35)
            v+=gap+s.R.uniform(-.8,.8)
    def under(s,x,y,l,c='r',w=1.3): s.poly([(x,y),(x+l*.5,y+s.R.uniform(-1,1)),(x+l,y)],c,w,amp=.5)
    def text(s,x,y,t,size=13,c='k',anchor='start',rot=None,bold=False):
        """写字：x_{1}、x^{2} 转上下标；每条标注带一点点随手的倾斜"""
        r=s.R.uniform(-1.1,1.1) if rot is None else rot
        parts=re.split(r'(_\{[^}]*\}|\^\{[^}]*\})',t);out=''
        for p in parts:
            if p.startswith('_{'): out+='<tspan dy="3.5" font-size="%.1f">%s</tspan><tspan dy="-3.5">​</tspan>'%(size*.72,esc(p[2:-1]))
            elif p.startswith('^{'): out+='<tspan dy="-5" font-size="%.1f">%s</tspan><tspan dy="5">​</tspan>'%(size*.72,esc(p[2:-1]))
            else: out+=esc(p)
        s.o.append('<text x="%.1f" y="%.1f" font-size="%.1f" fill="%s" text-anchor="%s"%s transform="rotate(%.2f %.1f %.1f)">%s</text>'%(x,y,size,INK.get(c,c),anchor,' font-weight="600"' if bold else '',r,x,y,out))
    # 组合 ----------------------------------------------------------
    def node(s,x,y,t='',r=12,c='k',tc=None,size=12,fill=None):
        s.circle(x,y,r,c,fill=fill)
        if t!='': s.text(x,y+size*.36,t,size,tc or c,'middle',rot=0)
    def edge(s,x0,y0,x1,y1,r0=12,r1=12,c='k',arrow=False,w=1.2,dash=None):
        d=math.hypot(x1-x0,y1-y0) or 1;ux,uy=(x1-x0)/d,(y1-y0)/d
        a,b=(x0+ux*r0,y0+uy*r0),(x1-ux*r1,y1-uy*r1)
        (s.arrow if arrow else s.line)(a[0],a[1],b[0],b[1],c,w,dash)
    def tree(s,spec,x,y,dx=70,dy=42,r=12,size=12):
        """spec=('A',('B',None,('D',)),('C',)) 手画二叉树"""
        v=spec[0];s.node(x,y,str(v),r,size=size)
        if len(spec)>1 and spec[1]:
            s.edge(x,y,x-dx,y+dy,r,r);s.tree(spec[1],x-dx,y+dy,dx*.55,dy,r,size)
        if len(spec)>2 and spec[2]:
            s.edge(x,y,x+dx,y+dy,r,r);s.tree(spec[2],x+dx,y+dy,dx*.55,dy,r,size)
    def cells(s,x,y,rows,cw=34,ch=24,size=12,c='k',tc=None):
        """手画表格 rows=[[..],[..]]，cw 可为每列宽度的列表；元素前缀 ! 表示红笔"""
        n=len(rows[0]);cws=cw if isinstance(cw,(list,tuple)) else [cw]*n;W=sum(cws);H=ch*len(rows)
        for i in range(len(rows)+1): s.line(x,y+i*ch,x+W,y+i*ch,c,1.0)
        xx=x
        for w in [0]+list(cws):
            xx+=w;s.line(xx,y,xx,y+H,c,1.0)
        for i,r in enumerate(rows):
            xx=x
            for j,t in enumerate(r):
                t=str(t);col=tc or c
                if t.startswith('!'): t=t[1:];col='r'
                s.text(xx+cws[j]/2,y+i*ch+ch/2+size*.36,t,size,col,'middle',rot=0);xx+=cws[j]
    def chain(s,x,y,items,cw=40,ch=26,gap=20,size=12,arrow=True,c='k'):
        """一串小格子 + 箭头：链表、流程"""
        for i,t in enumerate(items):
            xx=x+i*(cw+gap);s.box(xx,y,cw,ch,c);s.text(xx+cw/2,y+ch/2+size*.36,str(t),size,c,'middle',rot=0)
            if arrow and i<len(items)-1: s.arrow(xx+cw+1,y+ch/2,xx+cw+gap-1,y+ch/2,c)
    def bar(s,x,y,w,h,frac,c='k',fillc='p',label=None):
        """手涂的进度条：框 + 排线"""
        s.box(x,y,w,h,c,1.0)
        if frac>0:
            xe=x+w*min(frac,1);xx=x+2
            while xx<xe-1:
                s.poly([(xx+s.R.uniform(-.6,.6),y+h-2),(xx+2+s.R.uniform(-.6,.6),y+2)],fillc,1.0,amp=.15);xx+=2.6+s.R.uniform(-.3,.5)
        if label: s.text(x+w+6,y+h-1,label,12,c,'start',rot=0)
    def svg(s,cls='sk',alt=''):
        return '<svg class="%s" viewBox="0 0 %d %d" width="%d" role="img" aria-label="%s" xmlns="http://www.w3.org/2000/svg">%s</svg>'%(cls,s.w,s.h,round(s.w*1.22),esc(alt).replace('"','&quot;'),''.join(s.o))
