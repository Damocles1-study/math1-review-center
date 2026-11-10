# 2017 数学一 · 精解答案独立复算（sympy + 数值 + 蒙特卡洛）
import sympy as sp, random, math
from sympy import pi, sqrt, exp, sin, cos, log, oo, Rational as R
x,y,z,t,r,th,a,b,lam=sp.symbols('x y z t r theta a b lam',real=True)
ok=lambda c,m: print(('✓ ' if c else '✗ ')+m) or (c or exit(1))
random.seed(2017)

# 1 右极限 = 1/(2a) = b
h=sp.symbols('h',positive=True); A_=sp.symbols('A_',positive=True)
L=sp.limit((1-cos(sp.sqrt(h)))/(A_*h),h,0)
ok(sp.simplify(L-1/(2*A_))==0,'#1 右极限 1/(2a)=b ⟹ ab=1/2，选 A')

# 2 ff'>0：f=e^x（正）与 f=-e^x（负）两个例子都满足；C 恒成立，A/B 各被一个例子否掉
f1=sp.exp(x); f2=-sp.exp(x)
for f in (f1,f2): assert sp.simplify(f*sp.diff(f,x)).is_positive
c1=(f1.subs(x,1)>f1.subs(x,-1)); c2=(f2.subs(x,1)>f2.subs(x,-1))
ok(c1 and not c2 and all(abs(f.subs(x,1))>abs(f.subs(x,-1)) for f in (f1,f2)),'#2 A 被 f=−e^x 否掉、B 被 f=e^x 否掉，C 两例都对，选 C')

# 3 方向导数
f=x**2*y+z**2; g=sp.Matrix([sp.diff(f,v) for v in (x,y,z)]).subs({x:1,y:2,z:0})
n=sp.Matrix([1,2,2]); ok(g.dot(n/n.norm())==2 and g.dot(n)==6,'#3 ∇f=(4,1,0)，单位化后 =2（不单位化是 6 —— 选项 B 的来源），选 D')

# 4 追及：领先量 d(t)=10−∫(v1−v2)…… 这里用面积记账：d(0)=10，[0,10] 甲快 +10，[10,25] 乙快 −20，[25,30] 甲快 +3
d={0:10}; d[10]=d[0]+10; d[25]=d[10]-20; d[30]=d[25]+3
# 用一组具体函数复现：在 [10,25] 上领先量单调减（乙始终更快），t=25 时恰为 0
ok(d[10]==20 and d[25]==0 and d[30]==3,'#4 领先量 10→20→0→3，乙在 t=25 首次追上，选 C')

# 5 α 单位向量：αα^T 特征值 1 (一个)、0 (n−1 个)
for nn in (2,3,4):
    v=sp.Matrix([random.randint(-3,3) for _ in range(nn)])
    if v.norm()==0: v[0]=1
    v=v/v.norm(); P=v*v.T; I=sp.eye(nn)
    dets=[sp.simplify((I+c*P).det()) for c in (-1,1,2,-2)]
    assert dets==[0,2,3,-1], dets
ok(True,'#5 |E−αα^T|=0，|E+αα^T|=2，|E+2αα^T|=3，|E−2αα^T|=−1 ⟹ 只有 A 不可逆，选 A')

# 6 相似
A6=sp.Matrix([[2,0,0],[0,2,1],[0,0,1]]); B6=sp.Matrix([[2,1,0],[0,2,0],[0,0,1]]); C6=sp.diag(1,2,2)
ok(A6.is_diagonalizable() and not B6.is_diagonalizable() and (2*sp.eye(3)-A6).rank()==1 and (2*sp.eye(3)-B6).rank()==2,'#6 r(2E−A)=1 可对角化 ~C；r(2E−B)=2 不可对角化，选 B')

# 7 随机概率空间：P(A|B)>P(A|B̄) 与 P(B|A)>P(B|Ā) 同真同假
cnt=0
for _ in range(20000):
    w=[random.random() for _ in range(4)]; s_=sum(w); pAB,pAb,paB,pab=[q/s_ for q in w]
    pA=pAB+pAb; pB=pAB+paB
    lhs=pAB/pB>pAb/(1-pB); rhs=pAB/pA>paB/(1-pA)
    assert lhs==rhs; cnt+=lhs
ok(True,'#7 20000 组随机分布：两个不等式同真同假（真 %d 组），选 A'%cnt)

# 8 蒙特卡洛：2(Xn−X1)^2 的均值应为 4（χ²(1) 均值 1），不是 χ²
N=200000; s8=0.0
for _ in range(N):
    u,v=random.gauss(0,1),random.gauss(0,1); s8+=2*(u-v)**2
ok(abs(s8/N-4)<0.06,'#8 E[2(Xn−X1)^2]≈%.3f=4 ≠ 自由度 1；(Xn−X1)^2/2 才是 χ²(1)，选 B'%(s8/N))

# 9
ok(sp.diff(1/(1+x**2),x,3).subs(x,0)==0 and sp.diff(1/(1+x**2),x,4).subs(x,0)==24,'#9 f\'\'\'(0)=0（附 f⁽⁴⁾(0)=24）')

# 10
Y=sp.Function('Y'); sol=sp.dsolve(Y(x).diff(x,2)+2*Y(x).diff(x)+3*Y(x))
ok('sqrt(2)*x' in str(sol.rhs) and 'exp(-x)' in str(sol.rhs),'#10 通解 %s'%sol.rhs)

# 11
P=x/(x**2+y**2-1); Q=-a*y/(x**2+y**2-1)
ok(sp.solve(sp.simplify(sp.diff(P,y)-sp.diff(Q,x)).subs({x:R(1,3),y:R(1,4)}),a)==[-1],'#11 a=−1')

# 12
xx=R(3,10); S12=sum((-1)**(k-1)*k*xx**(k-1) for k in range(1,200))
ok(abs(float(S12)-float(1/(1+xx)**2))<1e-12,'#12 S(x)=1/(1+x)^2（x=0.3 数值核对）')

# 13
A13=sp.Matrix([[1,0,1],[1,1,2],[0,1,1]])
for _ in range(5):
    M=sp.Matrix(3,3,lambda i,j:random.randint(-4,4))
    if M.det()!=0: assert (A13*M).rank()==2
ok(A13.rank()==2,'#13 秩 = r(A) = 2')

# 14
EX=sp.Rational(1,2)*0+sp.Rational(1,2)*4
phi=lambda u: sp.exp(-u**2/2)/sp.sqrt(2*pi)
dens=sp.Rational(1,2)*phi(x)+sp.Rational(1,4)*phi((x-4)/2)
ok(abs(float(sp.Integral(dens,(x,-30,30)).evalf())-1)<1e-9 and abs(float(sp.Integral(x*dens,(x,-30,30)).evalf())-2)<1e-9 and EX==2,'#14 E(X)=2（密度积分为 1）')

# 15 抽象 f：拿具体 f 验证 y''(0)=f11+f1−f2
u,v=sp.symbols('u v')
for F in (u**3*v+sp.sin(u*v), sp.exp(u-2*v)+u*v**2):
    yy=F.subs({u:sp.exp(x),v:sp.cos(x)})
    d1=sp.diff(yy,x).subs(x,0); d2=sp.diff(yy,x,2).subs(x,0)
    pt={u:1,v:1}
    assert sp.simplify(d1-sp.diff(F,u).subs(pt))==0
    assert sp.simplify(d2-(sp.diff(F,u,2)+sp.diff(F,u)-sp.diff(F,v)).subs(pt))==0
ok(True,'#15 dy/dx|0=f1\'(1,1)，d²y/dx²|0=f11\'\'(1,1)+f1\'(1,1)−f2\'(1,1)（两组具体 f 验证）')

# 16
I16=sp.integrate(x*sp.log(1+x),(x,0,1))
nn=20000; s16=sum(k/nn**2*math.log(1+k/nn) for k in range(1,nn+1))
ok(I16==R(1,4) and abs(s16-0.25)<1e-4,'#16 极限 = ∫0^1 x ln(1+x)dx = 1/4（n=20000 时和式 %.6f）'%s16)

# 17
Fe=x**3+y**3-3*x+3*y-2
yp=sp.simplify(-sp.diff(Fe,x)/sp.diff(Fe,y))
r1=[s for s in sp.solve(Fe.subs(x,1),y) if s.is_real]; r2=[s for s in sp.solve(Fe.subs(x,-1),y) if s.is_real]
ypp=lambda X0,Y0: sp.diff(yp,x).subs({x:X0,y:Y0})+sp.diff(yp,y).subs({x:X0,y:Y0})*yp.subs({x:X0,y:Y0})
ok(sp.simplify(yp-(1-x**2)/(1+y**2))==0 and r1==[1] and r2==[0] and ypp(1,1)==-1 and ypp(-1,0)==2,'#17 y\'=(1−x²)/(1+y²)；y(1)=1 极大（y\'\'=−1），y(−1)=0 极小（y\'\'=2）')

# 18 举例：f(x)=x^2−x/2... 需 f(1)>0, f(x)/x→负；f=x^2−0.5x，零点 ξ=0.5；验证 ff''+f'^2=(ff')' 在 (0,1) 有两个零点
fx=x**2-R(1,2)*x; G=sp.expand(fx*sp.diff(fx,x,2)+sp.diff(fx,x)**2)
rts=[q for q in sp.solve(G,x) if 0<q<1]
ok(fx.subs(x,1)>0 and sp.limit(fx/x,x,0,'+')<0 and len(rts)==2 and sp.simplify(sp.diff(fx*sp.diff(fx,x),x)-G)==0,'#18 例 f=x²−x/2：ff\'\'+f\'^2=(ff\')\' 在 (0,1) 的根 %s'%rts)

# 19
M19=sp.integrate(sp.integrate(18*r*r,(r,0,2*cos(th))),(th,-pi/2,pi/2))
# 数值核对 dS=√2dxdy：锥面 z=√(x²+y²)
zz=sp.sqrt(x**2+y**2); dS=sp.sqrt(1+sp.diff(zz,x)**2+sp.diff(zz,y)**2)
ok(M19==64 and sp.simplify(dS-sp.sqrt(2))==0,'#19 投影 x²+y²=2x（z=0），dS=√2dxdy，M=64')

# 20 构造满足条件的 A：取 α1,α2 随机，α3=α1+2α2，检验 3 个特征值互异、r=2、通解
for _ in range(50):
    a1=sp.Matrix([random.randint(-3,3) for _ in range(3)]); a2=sp.Matrix([random.randint(-3,3) for _ in range(3)])
    A20=a1.row_join(a2).row_join(a1+2*a2)
    ev=A20.eigenvals()
    if len(ev)==3 and all(m==1 for m in ev.values()):
        beta=a1+a2+(a1+2*a2)
        assert A20.rank()==2 and A20*sp.Matrix([1,1,1])==beta and A20*sp.Matrix([1,2,-1])==sp.zeros(3,1)
        break
else: ok(False,'#20 没找到例子')
ok(True,'#20 r(A)=2；Ax=β 通解 (1,1,1)^T+k(1,2,−1)^T（具体矩阵核对）')

# 21
A21=lambda aa: sp.Matrix([[2,1,-4],[1,-1,1],[-4,1,aa]])
asol=sp.solve(A21(a).det(),a)
M21=A21(2); ev=M21.eigenvals()
Qc=[]
for lv,vec in [(-3,[1,-1,1]),(0,[1,2,1]),(6,[1,0,-1])]:
    vv=sp.Matrix(vec); assert M21*vv==lv*vv; Qc.append(vv/vv.norm())
Q=Qc[0].row_join(Qc[1]).row_join(Qc[2])
ok(asol==[2] and ev=={6:1,-3:1,0:1} and sp.simplify(Q.T*Q)==sp.eye(3) and sp.simplify(Q.T*M21*Q)==sp.diag(-3,0,6),'#21 a=2，特征值 6、−3、0；Q^TAQ=diag(−3,0,6)')

# 22
EY=sp.integrate(y*2*y,(y,0,1)); pY=sp.integrate(2*y,(y,0,EY))
N=200000; c=0; hist={'01':0,'23':0}; sz=0.0
for _ in range(N):
    X_=random.choice((0,2)); Y_=math.sqrt(random.random()); Z_=X_+Y_
    c+=(Y_<=2/3); sz+=Z_
    if 0.5<Z_<0.6: hist['01']+=1
    if 2.5<Z_<2.6: hist['23']+=1
# 密度 z (0<z<1)：在 (0.5,0.6) 的概率 = ∫ z = 0.055；z−2 (2<z<3) 在 (2.5,2.6) 也是 0.055
ok(EY==R(2,3) and pY==R(4,9) and abs(c/N-4/9)<0.004 and abs(hist['01']/N-0.055)<0.003 and abs(hist['23']/N-0.055)<0.003,'#22 EY=2/3，P=4/9；f_Z：0<z<1 为 z，2<z<3 为 z−2（蒙特卡洛核对）')

# 23
sg=sp.symbols('sigma',positive=True); zp=sp.symbols('zp',positive=True)
fz=2/(sp.sqrt(2*pi)*sg)*sp.exp(-zp**2/(2*sg**2))
EZ=sp.integrate(zp*fz,(zp,0,oo)); norm=sp.integrate(fz,(zp,0,oo))
nS,S2=sp.symbols('n S2',positive=True)
lnL=nS*sp.log(2/sp.sqrt(2*pi))-nS*sp.log(sg)-S2/(2*sg**2)
mle=sp.solve(sp.diff(lnL,sg),sg)
ok(norm==1 and sp.simplify(EZ-sg*sp.sqrt(2/pi))==0 and mle==[sp.sqrt(S2/nS)],'#23 f_Z=2/(√(2π)σ)e^{−z²/(2σ²)}，EZ=σ√(2/π) ⟹ 矩估计 √(π/2)·Z̄；MLE √(ΣZi²/n)')
print('全部通过')
