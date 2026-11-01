# -*- coding: utf-8 -*-
"""写笔记前读源材料（紧凑）。rd.py math 1 2 | cs 3 4 | po 马原_第2章 | en 2018_T1 [字数]"""
import glob,json,re,sys,os
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
R='/Users/zyx/Downloads/新威考研-资料/11408相关'
def strip(s):
    s=re.sub(r'<(script|style)\b.*?</\1>','',s,flags=re.S);s=re.sub(r'<svg\b.*?</svg>','[图]',s,flags=re.S)
    s=re.sub(r'</(p|div|li|tr|h\d|section|table|ul|details|summary)>','\n',s);s=re.sub(r'<br\s*/?>','\n',s);s=re.sub(r'<[^>]+>','',s)
    s=s.replace('&nbsp;',' ').replace('&lt;','<').replace('&gt;','>').replace('&amp;','&');s=re.sub(r'[ \t]+',' ',s);s=re.sub(r'\n\s*\n+','\n',s);return s.strip()
a=sys.argv[1]
def trim(t):
    # 代码块只留前 14 行，图表 DSL 只留前 160 字
    out=[];inc=0
    for l in t.split('\n'):
        if l.startswith(':::code'): inc=1;out.append(l);continue
        if inc:
            if l.strip()==':::': inc=0;out.append(l);continue
            inc+=1
            if inc<=15: out.append(l)
            continue
        if l.startswith('@ '): l=l[:170]
        if l.strip(): out.append(l)
    return '\n'.join(out)
if a=='math':
    p=R+'/数学一/复盘中心/重读报/_src/'
    Q=open(p+'shizhan.txt',encoding='utf8').read()
    for n in map(int,sys.argv[2:]):
        t=open(p+'%02d.txt'%n,encoding='utf8').read()
        t='\n'.join(l for l in t.split('\n') if not l.startswith('!fig') or True)
        print('=====期',n);print(t)
        for m in re.finditer(r':::q (\d+) \|(.*?)\n(.*?)\n:::',Q,re.S):
            if int(m.group(1))==n: print('[实战]',m.group(2).strip());print(m.group(3))
elif a=='cs':
    sys.path.insert(0,R+'/408/复盘中心/术式408/_build')
    import qbank
    B=qbank.load();p=R+'/408/复盘中心/术式408/_src/'
    cl=lambda x:re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',str(x)))
    for n in map(int,sys.argv[2:]):
        print('=====话',n);print(trim(open(p+'%02d.txt'%n,encoding='utf8').read()))
        f=p+'q/%02d.txt'%n
        if not os.path.exists(f):continue
        for l in open(f,encoding='utf8'):
            if l.startswith('@q '):
                k,_,c=l[3:].partition('|');k=k.strip();q=B[k]
                o=q.get('opts') or []
                print('[Q %s %s] %s | %s || 答 %s | 点评 %s'%(k,q.get('exam'),cl(q['stem'])[:170],' / '.join(cl(x)[:28] for x in o),q.get('ans',''),c.strip()[:110]))
            elif l.strip(): print(l.rstrip())
elif a=='po':
    f=R+'/政治/复盘中心/讲义/%s.html'%sys.argv[2]
    print(strip(open(f,encoding='utf8').read())[:int(sys.argv[3]) if len(sys.argv)>3 else 99999])
elif a=='pq':   # pq 科 章 [每隔k题取一题]
    p,ch=sys.argv[2],int(sys.argv[3]);k=int(sys.argv[4]) if len(sys.argv)>4 else 6
    s=open(R+'/政治/复盘中心/题库/data_%s.js'%p,encoding='utf8').read()
    qs=[x for x in json.loads(s.split('=',2)[2].rstrip().rstrip(';'))['qs'] if x['ch']==ch and x['t']!='e']
    for x in qs[::k]:
        print('[%s] %s | %s || %s || %s'%(x['id'],x['stem'].replace('\n',' ')[:130],' / '.join('ABCD'[i]+'.'+x['opts'][i][:26] for i in range(4)),x['ans'],(x.get('note') or x.get('jx') or x.get('db') or '')[:90]))
elif a=='en':
    f=glob.glob(R+'/英语一/阅读复盘/%s*.html'%sys.argv[2])[0];print(f.split('/')[-1])
    print(strip(open(f,encoding='utf8').read())[:int(sys.argv[3]) if len(sys.argv)>3 else 7000])
if a=='csb':
    # 精简模式：标题、术式块、陷阱、领域块、做题点评
    sys.path.insert(0,R+'/408/复盘中心/术式408/_build')
    import qbank
    B=qbank.load();p=R+'/408/复盘中心/术式408/_src/'
    cl=lambda x:re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',str(x)))
    for n in map(int,sys.argv[2:]):
        print('=====话',n);keep=0
        for l in open(p+'%02d.txt'%n,encoding='utf8'):
            l=l.rstrip()
            if l.startswith('== ') or l.startswith('=== '): print(l[:60]);continue
            if l.startswith(':::shu') or l.startswith(':::trap') or l.startswith(':::domain') or l.startswith(':::vow'): keep=1;print(l[:80]);continue
            if l.startswith(':::'): keep=0;continue
            if keep and l.strip(): print(l[:190])
            elif l.startswith('|') : print(l[:120])
        f=p+'q/%02d.txt'%n
        if not os.path.exists(f):continue
        for l in open(f,encoding='utf8'):
            if l.startswith('@q '):
                k,_,c=l[3:].partition('|');k=k.strip();q=B[k]
                o=q.get('opts') or [];ans=q.get('ans','')
                t=cl(o['ABCD'.index(ans)])[:26] if o and ans in list('ABCD') else ''
                print('[Q %s %s] %s → %s %s | %s'%(k,q.get('exam'),re.sub(r'^【[^】]*】','',cl(q['stem']))[:95],ans,t,c.strip()[:70]))
if a=='pob':
    CODE={'马原':'my','史纲':'sg','习概':'xg','思法':'sx','毛中特':'mz'}
    for name in sys.argv[2:]:
        s=open(R+'/政治/复盘中心/讲义/%s.html'%name,encoding='utf8').read()
        print('=====',name)
        heads=re.findall(r'<h2[^>]*>(.*?)</h2>',s,re.S)
        print('节:',' / '.join(re.sub(r'<[^>]+>','',h).strip()[:22] for h in heads))
        m=re.search(r'<table[^>]*onepage[^>]*>.*?</table>',s,re.S)
        if m: print('一页纸:',strip(m.group(0))[:1500])
        txt=strip(s)
        L=[l for l in txt.split('\n') if re.search(r'口诀|永远错|错——|」错|秒杀|必背|一句话',l)]
        for l in L[:12]: print('·',l[:150])
        # 比方（class 含 pic/ana/like）
        for b in re.findall(r'<div class="[^"]*(?:pic|ana|like|meta)[^"]*"[^>]*>(.*?)</div>',s,re.S)[:3]:
            print('比方:',strip(b)[:130])
        p=CODE[name.split('_')[0]];nums=re.findall(r'第?(\d+)',name.split('_',1)[1]) or ['0']
        ch=int(nums[0]) if '导论' not in name else 1
        d=open(R+'/政治/复盘中心/题库/data_%s.js'%p,encoding='utf8').read()
        qs=[x for x in json.loads(d.split('=',2)[2].rstrip().rstrip(';'))['qs'] if x['ch']==ch and x['t']!='e']
        k=max(1,len(qs)//4)
        for x in qs[k//2::k][:4]:
            print('[Q %s] %s | %s || %s'%(x['id'],x['stem'].replace('\n',' ')[-90:],' / '.join('ABCD'[i]+x['opts'][i][:18] for i in range(4)),x['ans']))
