# 2018 数学一 · 精解答案独立复算（sympy + 数值 + 蒙特卡洛）
import sympy as sp, random, math
from sympy import pi, sqrt, exp, sin, cos, tan, log, atan, oo, Rational as R
x,y,z,t,u,k,a,lam=sp.symbols('x y z t u k a lam',real=True)
ok=lambda c,m: print(('✓ ' if c else '✗ ')+m) or (c or exit(1))

# 1 不可导的是 D：看单侧导数
fs={'A':lambda x:sp.Abs(x)*sin(x),'B':lambda x:sp.Abs(x)*sin(sp.sqrt(sp.Abs(x))),'C':lambda x:cos(sp.Abs(x)),'D':lambda x:cos(sp.sqrt(sp.Abs(x)))}
h=sp.symbols('h',positive=True)
bad=[n for n,f in fs.items() if sp.limit((f(h)-f(0))/h,h,0)!=sp.limit((f(-h)-f(0))/(-h),h,0)]
ok(bad==['D'],'#1 不可导只有 D，D 的左右导数 %s / %s'%(sp.limit((fs['D'](h)-1)/h,h,0),sp.limit((fs['D'](-h)-1)/(-h),h,0)))

# 2 切平面：切点 (x0,y0)，平面 z=2x0 x+2y0 y-(x0^2+y0^2)，过 (1,0,0),(0,1,0)
x0,y0=sp.symbols('x0 y0')
sol=sp.solve([2*x0-(x0**2+y0**2),2*y0-(x0**2+y0**2)],[x0,y0])
ok(sorted(sol)==[(0,0),(1,1)],'#2 切点 (0,0,0)、(1,1,2) ⟹ z=0 与 2x+2y−z=2，选 B')

# 3
n=sp.symbols('n',integer=True,nonnegative=True)
S=sum(((-1)**i*R(2*i+3,math.factorial(2*i+1))) for i in range(30))
ok(abs(float(S)-(math.cos(1)+2*math.sin(1)))<1e-14,'#3 和 = cos1+2sin1，选 B')

# 4
M=sp.integrate((1+x)**2/(1+x**2),(x,-pi/2,pi/2)); N=sp.integrate((1+x)*exp(-x),(x,-pi/2,pi/2))
K=sp.Integral(1+sp.sqrt(cos(x)),(x,-pi/2,pi/2)).evalf()
ok(sp.simplify(M-pi)==0 and float(N)<float(M)<float(K),'#4 M=π, N=%.4f, K=%.4f ⟹ K>M>N，选 C'%(float(N),float(K)))

# 5 相似：特征值都为 1，比 r(A−E)
T=sp.Matrix([[1,1,0],[0,1,1],[0,0,1]])
opts={'A':[[1,1,-1],[0,1,1],[0,0,1]],'B':[[1,0,-1],[0,1,1],[0,0,1]],'C':[[1,1,-1],[0,1,0],[0,0,1]],'D':[[1,0,-1],[0,1,0],[0,0,1]]}
I3=sp.eye(3)
rk={n:(sp.Matrix(m)-I3).rank() for n,m in opts.items()}
ok(rk=={'A':2,'B':1,'C':1,'D':1} and (T-I3).rank()==2,'#5 r(X−E)：目标 2，A2 B1 C1 D1 ⟹ 选 A；Jordan 形对照 %s'%(sp.Matrix(opts['A']).jordan_form()[1]==T.jordan_form()[1]))

# 6 随机矩阵检验 A 恒成立，B 有反例
random.seed(1)
cnt=0
for _ in range(300):
    A=sp.Matrix(3,3,lambda i,j:random.randint(-1,1)); B=sp.Matrix(3,3,lambda i,j:random.randint(-1,1))
    assert A.row_join(A*B).rank()==A.rank()
    if A.row_join(B*A).rank()!=A.rank(): cnt+=1
A=sp.Matrix([[1,0],[0,0]]);B=sp.Matrix([[0,0],[1,0]])
ok(cnt>0 and A.row_join(B*A).rank()==2 and A.rank()==1,'#6 A 恒成立；B 反例 A=diag(1,0), B=[[0,0],[1,0]]（r(A,BA)=2≠1）；随机反例 %d 个'%cnt)

# 7 对称于 x=1
ok(abs((1-0.6)/2-0.2)<1e-12,'#7 P(X<0)=(1−0.6)/2=0.2，选 A')

# 8 拒绝域 z_{0.005}>z_{0.025}
from statistics import NormalDist
ok(NormalDist().inv_cdf(1-0.005)>NormalDist().inv_cdf(1-0.025),'#8 α=0.01 的临界值 %.3f > α=0.05 的 %.3f ⟹ 接受域更大，选 D'%(NormalDist().inv_cdf(.995),NormalDist().inv_cdf(.975)))

# 9
L=sp.limit(log((1-tan(x))/(1+tan(x)))/sin(k*x),x,0)
ks=sp.solve(sp.Eq(L,1),k)
ok(ks==[-2],'#9 指数极限 %s = 1 ⟹ k=-2'%L)

# 10 构造一个满足条件的 f：f(0)=0, f(1)=2, f'(1)=2ln2
c=sp.symbols('c0:4'); f=c[0]+c[1]*x+c[2]*x**2+c[3]*x**3
cs=sp.solve([f.subs(x,0),f.subs(x,1)-2,sp.diff(f,x).subs(x,1)-2*log(2),c[3]-7],c)
fv=f.subs(cs)
ok(sp.simplify(sp.integrate(x*sp.diff(fv,x,2),(x,0,1))-(2*log(2)-2))==0,'#10 ∫x f″ = 2ln2−2（与 f 的具体形状无关）')

# 11 rot
P,Q,Rr=x*y,-y*z,z*x
rot=sp.Matrix([sp.diff(Rr,y)-sp.diff(Q,z),sp.diff(P,z)-sp.diff(Rr,x),sp.diff(Q,x)-sp.diff(P,y)])
ok(list(rot.subs({x:1,y:1,z:0}))==[1,0,-1],'#11 rot F(1,1,0)=(1,0,−1)=i−k')

# 12 参数化大圆：e1=(1,-1,0)/√2, e2=(1,1,-2)/√6
e1=sp.Matrix([1,-1,0])/sqrt(2); e2=sp.Matrix([1,1,-2])/sqrt(6)
r=cos(t)*e1+sin(t)*e2
I12=sp.integrate(sp.simplify(r[0]*r[1]),(t,0,2*pi))  # |r'|=1
ok(sp.simplify(I12+pi/3)==0,'#12 ∮xy ds = %s'%sp.simplify(I12))

# 13 例：A=diag(1,-1)
A=sp.diag(1,-1); ok(A**2*sp.Matrix([1,1])==sp.Matrix([1,1]) and A.det()==-1,'#13 λ=±1 ⟹ |A|=−1')

# 14
cc=sp.symbols('cc',positive=True)
ok(sp.solve(sp.Eq((cc/2)/(R(1,4)+cc),R(1,4)),cc)==[R(1,4)],'#14 P(C)=1/4')
# 蒙特卡洛：构造 A,B,C 满足独立/互斥
random.seed(2);NN=400000;num=den=0
for _ in range(NN):
    A_=random.random()<.5; v=random.random(); B_=v<.5; C_=v>=.75   # B=[0,.5)、C=[.75,1) 互斥，与 A 独立
    if (A_ and B_) or C_:
        den+=1; num+= (A_ and C_)
ok(abs(num/den-.25)<.005,'#14 蒙特卡洛 P(AC|AB∪C)=%.4f'%(num/den))

# 15
F=R(1,2)*exp(2*x)*atan(sqrt(exp(x)-1))-R(1,6)*(exp(x)-1)**R(3,2)-R(1,2)*sqrt(exp(x)-1)
d=sp.diff(F,x)-exp(2*x)*atan(sqrt(exp(x)-1))
ok(all(abs(float(d.subs(x,v)))<1e-10 for v in [0.1,0.5,1.3,2.7]),'#15 求导验原函数')

# 16
X_,Y_,Z_=sp.symbols('X Y Z',positive=True)
area=X_**2/(4*pi)+Y_**2/16+sqrt(3)*Z_**2/36
sl=sp.solve([sp.diff(area,X_)+lam,sp.diff(area,Y_)+lam,sp.diff(area,Z_)+lam,X_+Y_+Z_-2],[X_,Y_,Z_,lam],dict=True)[0]
mn=sp.simplify(area.subs(sl))
bd=[1/(4+3*sqrt(3)),1/(pi+3*sqrt(3)),1/(pi+4)]
ok(sp.simplify(mn-1/(pi+4+3*sqrt(3)))==0 and all(float(mn)<float(b) for b in bd),'#16 最小值 1/(π+4+3√3)=%.5f，三个边界最小 %.5f'%(float(mn),min(float(b) for b in bd)))
# 数值随机搜索
random.seed(3);best=9
for _ in range(200000):
    p=random.random();q=random.random()
    if p+q>1: continue
    xx,yy=2*p,2*q;zz=2-xx-yy
    best=min(best,xx**2/(4*math.pi)+yy**2/16+math.sqrt(3)*zz**2/36)
ok(best>=float(mn)-1e-9 and best-float(mn)<1e-4,'#16 随机搜索最小 %.6f'%best)

# 17 数值：散度体积分 + 补面
rho,th=sp.symbols('rho th',positive=True)
# 半椭球 x>=0, x^2+3y^2+3z^2<=1；y=rho cos/√3 ...
# ∭(1+3y^2+3z^2)dV，换元 y=v/√3,z=w/√3, dV=dx dv dw/3，区域 x^2+v^2+w^2<=1, x>=0
r_,ph,te=sp.symbols('r ph te',positive=True)
integrand=(1+(r_*sin(ph)*cos(te))**2+(r_*sin(ph)*sin(te))**2)*r_**2*sin(ph)/3  # x=r cos ph
I17=sp.integrate(integrand,(r_,0,1),(ph,0,pi/2),(te,0,2*pi))
ok(sp.simplify(I17-14*pi/45)==0,'#17 I=%s（补面 x=0 上三项皆 0）'%sp.simplify(I17))

# 18 (I)
yy=sp.Function('y')
g=sp.dsolve(sp.Derivative(yy(x),x)+yy(x)-x).rhs
ok(sp.simplify(g-(x-1)-sp.Symbol('C1')*exp(-x))==0,'#18(I) y=x−1+Ce^{−x}')
# (II) 数值例：f=cos(2πx/T)+1, T=1.7
T_=1.7; fT=lambda s:math.cos(2*math.pi*s/T_)+1
import numpy as np
def Iexp(a,b,m=4000):
    s=np.linspace(a,b,m+1); v=np.exp(s)*(np.cos(2*np.pi*s/T_)+1); return float(((v[1:]+v[:-1])/2*np.diff(s)).sum())
C0=Iexp(0,T_)/(math.e**T_-1)
ysol=lambda X:math.exp(-X)*(C0+Iexp(0,X))
ok(abs(ysol(0.37+T_)-ysol(0.37))<1e-6 and abs(ysol(2.9+T_)-ysol(2.9))<1e-6,'#18(II) C=∫₀ᵀeᵗf/(eᵀ−1) 时 y 以 T 为周期（数值）')

# 19
xs=[3.0]
for _ in range(30): xs.append(math.log(math.expm1(xs[-1])/xs[-1]))
ok(all(b<a for a,b in zip(xs,xs[1:])) and xs[-1]<1e-6 and all(v>0 for v in xs),'#19 x_n 单调降、恒正，x_30=%.2e → 0'%xs[-1])
ok(all((math.exp(v)-1)<v*math.exp(v) for v in [0.01,0.5,2,5]),'#19 e^x−1<xe^x (x>0)')

# 20
x1,x2,x3=sp.symbols('x1 x2 x3')
Mx=sp.Matrix([[1,-1,1],[0,1,1],[1,0,a]])
ok(sp.factor(Mx.det())==a-2,'#20 系数行列式 = a−2')
M2=Mx.subs(a,2); ns=M2.nullspace()[0]; ns=ns/ns[2]
ok(list(ns)==[-2,-1,1],'#20 a=2 解 k(−2,−1,1)')
fq=(x1-x2+x3)**2+(x2+x3)**2+(x1+2*x3)**2
Aq=sp.hessian(fq,(x1,x2,x3))/2
ev=Aq.eigenvals()
ok(sorted([float(e) for e in Aq.eigenvals(multiple=True)])[0]==0 and all(float(e)>=-1e-12 for e in Aq.eigenvals(multiple=True)) and Aq.rank()==2,'#20 a=2 时矩阵 %s 特征值 %s，秩 2 正惯性 2 ⟹ y1²+y2²'%(Aq.tolist(),[sp.nsimplify(e) for e in Aq.eigenvals(multiple=True)]))

# 21
A=sp.Matrix([[1,2,a],[1,3,0],[2,7,-a]]); B=sp.Matrix([[1,a,2],[0,1,1],[-1,1,1]])
ok(sp.expand(A.det())==0 and sp.expand(B.det())==2-a,'#21 |A|≡0，|B|=2−a ⟹ a=2')
A2,B2=A.subs(a,2),B.subs(a,2)
k1,k2,k3=sp.symbols('k1 k2 k3')
Pm=sp.Matrix([[3-6*k1,4-6*k2,4-6*k3],[-1+2*k1,-1+2*k2,-1+2*k3],[k1,k2,k3]])
ok(sp.simplify(A2*Pm-B2)==sp.zeros(3) and sp.factor(Pm.det())==k3-k2,'#21 AP=B 恒成立，|P|=%s'%sp.factor(Pm.det()))

# 22
# Cov(X,Z)=E(X^2 Y)-EX E(XY)=EY=λ；蒙特卡洛 λ=1.3
random.seed(5);L_=1.3;NN=300000;sxz=sx=sz=0;cnt0=0;cnt2=0
def pois(l):
    k_=0;p_=math.exp(-l);s_=p_;uu=random.random()
    while uu>s_: k_+=1;p_*=l/k_;s_+=p_
    return k_
for _ in range(NN):
    X=random.choice([1,-1]);Y=pois(L_);Z=X*Y
    sxz+=X*Z;sx+=X;sz+=Z;cnt0+=(Z==0);cnt2+=(Z==-2)
cov=sxz/NN-(sx/NN)*(sz/NN)
ok(abs(cov-L_)<0.03,'#22 Cov 蒙特卡洛 %.3f ≈ λ=%.1f'%(cov,L_))
ok(abs(cnt0/NN-math.exp(-L_))<0.005 and abs(cnt2/NN-0.5*L_**2/2*math.exp(-L_))<0.004,'#22 P(Z=0)=e^{−λ}、P(Z=−2)=½·λ²e^{−λ}/2 ✓')

# 23
s=sp.symbols('sigma',positive=True)
fd=exp(-sp.Abs(x)/s)/(2*s)
E1=2*sp.integrate(x*exp(-x/s)/(2*s),(x,0,oo)); E2=2*sp.integrate(x**2*exp(-x/s)/(2*s),(x,0,oo))
ok(sp.simplify(E1-s)==0 and sp.simplify(E2-2*s**2)==0,'#23 E|X|=σ，EX²=2σ² ⟹ E σ̂=σ，D σ̂=σ²/n')
xs_=sp.symbols('x1:6',real=True)
# 似然对 σ 求导零点
Ls=sum(-log(2*s)-sp.Abs(v)/s for v in xs_)
ok(sp.simplify(sp.solve(sp.diff(Ls,s),s)[0]-sum(sp.Abs(v) for v in xs_)/5)==0,'#23 MLE σ̂ = Σ|Xi|/n')
print('全部通过')
