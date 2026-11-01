# -*- coding: utf-8 -*-
"""核对 408 笔记里写到的选项字母与题库答案是否一致；打印题库答案供人工比对。"""
import glob,os,re,sys
R='/Users/zyx/Downloads/新威考研-资料/11408相关'
sys.path.insert(0,R+'/408/复盘中心/术式408/_build')
import qbank
B=qbank.load();H=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cl=lambda x:re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',str(x)))
bad=0;n=0
for f in sorted(glob.glob(H+'/_src/d??_cs.txt')):
    s=open(f,encoding='utf8').read()
    for m in re.finditer(r':::q ((?:ds|co|os|net):[^ ]+) · (\d+)[^|]*\|\s*(\S+)\s*\|(.*?)\n(.*?)\n:::',s,re.S):
        k,y,mk,stem,b=m.groups();n+=1
        q=B.get(k)
        if not q: print('无此题',k,os.path.basename(f));bad+=1;continue
        a=q.get('ans','')
        if str(q.get('exam'))!=y: print('年份不符',k,y,q.get('exam'));bad+=1
        if a not in list('ABCD'): continue
        L=re.findall(r'(?<![A-Za-z0-9_])([A-D])(?=[，。；、）\s]|$)',b)
        if not L:
            if '-v' in sys.argv: print('未写字母',k,a,cl(q['opts']['ABCD'.index(a)])[:30])
            continue
        if a not in L or (mk=='✓' and L[-1]!=a) or (mk in('✗','△') and L[-1]!=a):
            print(os.path.basename(f),k,'题库',a,cl(q['opts']['ABCD'.index(a)])[:40],'| 笔记',L,'|',b[:60].replace('\n',' '));bad+=1
print('检查',n,'不符',bad)
# 政治
import json
Q={}
for p in ('my','sg','xg','sx','mz'):
    d=open(R+'/政治/复盘中心/题库/data_%s.js'%p,encoding='utf8').read()
    for x in json.loads(d.split('=',2)[2].rstrip().rstrip(';'))['qs']: Q[x['id']]=x
for f in sorted(glob.glob(H+'/_src/d??_po.txt')):
    s=open(f,encoding='utf8').read()
    for m in re.finditer(r':::q ((?:my|sg|xg|sx|mz)-[a-z]-\d+) \|\s*(\S+)\s*\|(.*?)\n(.*?)\n:::',s,re.S):
        k=m.group(1);b=m.group(4)
        if k not in Q: print('无',k);continue
        a=Q[k]['ans'];L=re.findall(r'(?<![A-Za-z])([A-D]+)(?=[，。；、）\s]|$)',b)
        opt=Q[k]['opts']['ABCD'.index(a[0])][:30] if a[0] in 'ABCD' else ''
        if not L or L[-1]!=a: print(os.path.basename(f),k,'题库',a,opt,'| 笔记',L,'|',m.group(3)[:30],'|',b[:40].replace('\n',' '))
