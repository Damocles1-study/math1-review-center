#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""在线真题套卷：从本机真题 PDF 裁出每题题面和解析，输出 assets/exam/。
exam_cuts.json：paper=每题在试卷页上的 [页,上,下]（170dpi 像素），sol.st=每题解析起点 [页,千分位]，ans=选择题答案。"""
import io,json,os,sys
import numpy as np
import fitz
from PIL import Image
sys.path.insert(0,os.path.dirname(__file__))
from exam_map import MAP,scores
fitz.TOOLS.mupdf_display_errors(False)
HERE=os.path.dirname(os.path.abspath(__file__));ROOT=os.path.join(HERE,'..')
Z=os.path.join(ROOT,'..','..')
J=json.load(open(os.path.join(HERE,'exam_cuts.json')))
OUT=os.path.join(ROOT,'assets','exam')
def counts(y): return (8,6) if y<=2020 else (10,6)
def page(doc,i,dpi=170):
    p=doc[i].get_pixmap(dpi=dpi,colorspace=fitz.csGRAY)
    return Image.frombytes('L',(p.width,p.height),p.samples)
def clean(im,lim):
    a=np.array(im).astype(np.int16)
    lo=95
    a=np.where(a>=lim,255,np.clip((a-lo)*255/(lim-lo),0,255)).astype(np.uint8)
    return Image.fromarray(a)
def save(im,path):
    im.save(path,'WEBP',quality=62,method=6)
    return os.path.getsize(path)
tot=0
for y in sorted(MAP):
    d=os.path.join(OUT,'img',str(y));os.makedirs(d,exist_ok=True)
    qp=fitz.open(os.path.join(Z,'真题复盘中心易识别版','按年份',str(y),'%d_数学一_真题_图像保真版.pdf'%y))
    sf=os.path.join(Z,'真题','%d数学一解析.pdf'%y if y<=2019 else '%d数一真题解析.pdf'%y if y<=2025 else '2026考研数学（一）答案解析.pdf')
    sp=fitz.open(sf)
    n1,n2=counts(y);sc=scores(y);Q=[]
    B=J['paper'][str(y)];S=J['sol'][str(y)];N=len(B)
    assert N==len(sc),y
    pc={}
    def pq(i):
        if i not in pc: pc[i]=clean(page(qp,i),172)
        return pc[i]
    ps={}
    def psol(i):
        if i not in ps: ps[i]=clean(page(sp,i),205)
        return ps[i]
    TOP=.068 if y==2026 else .035; BOT=.925 if y==2026 else .955
    for k in range(N):
        pg,t,b=B[k];im=pq(pg);W=im.width
        c=im.crop((int(W*.075),max(0,t-6),int(W*.95),b+7))
        tot+=save(c,os.path.join(d,'q%02d.webp'%(k+1)))
        a=S['st'][str(k+1)];e=S['st'].get(str(k+2)) or S['end']
        sl=[]
        for p in range(a[0],e[0]+1):
            if p>=len(sp): break
            pi=psol(p);H=pi.height
            y0=a[1]/1000-.012 if p==a[0] else TOP
            y1=e[1]/1000-.012 if p==e[0] else BOT
            y0=max(y0,TOP);y1=min(y1,BOT)
            if y1-y0<.006: continue
            sl.append(pi.crop((int(pi.width*.03),int(H*y0),int(pi.width*.975),int(H*y1))))
        Wm=max(s.width for s in sl);Hm=sum(s.height for s in sl)
        o=Image.new('L',(Wm,Hm),255);h=0
        for s in sl: o.paste(s,(0,h));h+=s.height
        tot+=save(o,os.path.join(d,'s%02d.webp'%(k+1)))
        ty='choice' if k<n1 else 'blank' if k<n1+n2 else 'essay'
        it={'no':k+1,'type':ty,'score':sc[k],'img':'assets/exam/img/%d/q%02d.webp'%(y,k+1),'solImg':['assets/exam/img/%d/s%02d.webp'%(y,k+1)],
            'back':{'href':'q%02d.html'%MAP[y][k],'text':'这题归在第 %d 期，回去看 →'%MAP[y][k]}}
        if ty=='choice': it['ans']=J['ans'][str(y)][str(k+1)]
        Q.append(it)
    P={'year':y,'q':Q,'secName':{'choice':'一、选择题（每题 %d 分）'%sc[0],'blank':'二、填空题（每题 %d 分）'%sc[n1],'essay':'三、解答题'}}
    open(os.path.join(OUT,'y%d.js'%y),'w',encoding='utf-8').write('(window.EXAM_PAPERS=window.EXAM_PAPERS||{})[%d]=%s;\n'%(y,json.dumps(P,ensure_ascii=False,separators=(',',':'))))
    print(y,round(tot/1e6,1),'MB',flush=True)
