#!/usr/bin/env python3
"""Tiny Chess runner: deterministic move picker plus the official env protocol."""
import json,os,sys,urllib.request
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':20000}
HTTP=urllib.request.build_opener(urllib.request.ProxyHandler({}))

def board(fen):
 b=[None]*64
 for y,row in enumerate(fen.split()[0].split('/')):
  x=0
  for c in row:
   if c.isdigit():x+=int(c)
   else:b[(7-y)*8+x]=c;x+=1
 return b

def sq(s):return ord(s[0])-97+8*(ord(s[1])-49)

def pst(p,s):
 f=s&7;r=s>>3
 if p.islower():r=7-r
 c=14-abs(2*f-7)-abs(2*r-7)
 return (r*4+c if p.lower()=='p' else c*4 if p.lower()=='n' else c*2 if p.lower()=='b' else r*2 if p.lower()=='r' else c if p.lower()=='q' else 0)

def attacks(b,t,w):
 n=0;tf,tr=t&7,t>>3
 for s,p in enumerate(b):
  if not p or s==t or p.isupper()!=w:continue
  f,r=tf-(s&7),tr-(s>>3);c=p.lower()
  if c=='p':n+=abs(f)==1 and r==(1 if w else -1)
  elif c=='n':n+=(abs(f),abs(r)) in ((1,2),(2,1))
  elif c=='k':n+=max(abs(f),abs(r))==1
  elif (c=='b' and abs(f)==abs(r)) or (c=='r' and (not f or not r)) or (c=='q' and (not f or not r or abs(f)==abs(r))):
   a=(f>0)-(f<0);d=(r>0)-(r<0);x=(s&7)+a;y=(s>>3)+d
   while (x,y)!=(tf,tr):
    if b[y*8+x]:break
    x+=a;y+=d
   else:n+=1
 return n

def choose(fen,legal):
 if not legal:raise ValueError('no legal moves')
 b=board(fen);parts=fen.split();white=parts[1]=='w';ep=parts[3] if len(parts)>3 else '-'
 best=None;high=-10**9
 for m in sorted(legal):
  if len(m) not in (4,5):continue
  a,z=sq(m[:2]),sq(m[2:4]);p=b[a]
  if not p:continue
  q=b[z];cap=V[q.lower()] if q else 0
  if p.lower()=='p' and (a&7)!=(z&7) and not q and ep==m[2:4]:cap=100
  promo=V[m[4]]-100 if len(m)==5 and m[4] in V else 0
  pp=(m[4].upper() if p.isupper() else m[4]) if len(m)==5 else p
  c=b.copy();c[a]=None;c[z]=pp
  if cap==100 and p.lower()=='p' and (a&7)!=(z&7) and ep==m[2:4]:c[z-8 if white else z+8]=None
  castle=p.lower()=='k' and abs(z-a)==2
  if castle:
   rs=a+(3 if z>a else -4);rd=a+(1 if z>a else -1);c[rd]=c[rs];c[rs]=None
  score=cap+promo+pst(pp,z)-pst(p,a)+(40 if castle else 0)
  if pp.lower()!='k':
   e=attacks(c,z,not white);f=attacks(c,z,white)
   if e>f:score-=V[pp.lower()]*(e-f)//e
  if score>high:best,high=m,score
 if best is None:raise ValueError('no usable legal moves')
 return best

def post(url,path,body):
 req=urllib.request.Request(url+path,data=json.dumps(body).encode(),headers={'content-type':'application/json'})
 with HTTP.open(req) as res:return json.load(res)

def run():
 url=os.environ.get('MAKEFUN_ENV_URL','').rstrip('/')
 if not url:sys.exit('MAKEFUN_ENV_URL is not set')
 while True:
  g=post(url,'/game',{})
  if g.get('status')=='done':return
  if g.get('status')!='your_move':raise RuntimeError('unexpected /game status')
  while g.get('status')=='your_move':
   g=post(url,'/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
  if g.get('status')!='over':raise RuntimeError('unexpected /move status')

if __name__=='__main__':run()
