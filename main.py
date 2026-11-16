#!/usr/bin/env python3
"""Tiny Chess runner with deterministic one-ply evaluation."""
import json,os,sys,urllib.request
V={'p':100,'n':320,'b':330,'r':500,'q':900,'k':20000}
class Client:
 def __init__(self):self.opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
 def open(self,req):return self.opener.open(req,timeout=10)
HTTP=Client()

def board(fen):
 b=[None]*64
 for y,row in enumerate(fen.split()[0].split('/')):
  x=0
  for c in row:
   if c.isdigit():x+=int(c)
   else:b[(7-y)*8+x]=c;x+=1
 return b

def square(s):return ord(s[0])-97+8*(ord(s[1])-49)
def value(b):
 n=0
 for s,p in enumerate(b):
  if p:
   f=s&7;r=s>>3
   if p.islower():r=7-r
   c=14-abs(2*f-7)-abs(2*r-7)
   v=V[p.lower()]+(r*5 if p.lower()=='p' else c*5 if p.lower() in 'nb' else 0)
   n+=v if p.isupper() else -v
 return n

def play(b,m,ep,white):
 a,z=square(m[:2]),square(m[2:4]);p=b[a];q=b[z];taken=q
 if p.lower()=='p' and a%8!=z%8 and not q and ep==m[2:4]:taken='p'
 b[a]=None
 if taken=='p' and p.lower()=='p' and a%8!=z%8 and not q:b[z-8 if white else z+8]=None
 b[z]=m[4].upper() if len(m)>4 and p.isupper() else m[4].lower() if len(m)>4 else p
 if p.lower()=='k' and abs(z-a)==2:
  x=a+(3 if z>a else -4);y=a+(1 if z>a else -1);b[y]=b[x];b[x]=None
 return taken

def attacked(b,t,bywhite):
 tf,tr=t&7,t>>3
 for s,p in enumerate(b):
  if not p or p.isupper()!=bywhite:continue
  f,r=tf-(s&7),tr-(s>>3);c=p.lower()
  if c=='p' and abs(f)==1 and r==(1 if bywhite else -1):return True
  if c=='n' and (abs(f),abs(r)) in ((1,2),(2,1)):return True
  if c=='k' and max(abs(f),abs(r))==1:return True
  if c in 'brq' and ((c in 'bq' and abs(f)==abs(r)) or (c in 'rq' and (not f or not r))):
   dx=(f>0)-(f<0);dy=(r>0)-(r<0);x=(s&7)+dx;y=(s>>3)+dy
   while (x,y)!=(tf,tr):
    if b[y*8+x]:break
    x+=dx;y+=dy
   else:return True
 return False

def choose(fen,legal):
 if not legal:raise ValueError('no legal moves')
 b=board(fen);parts=fen.split();white=parts[1]=='w';ep=parts[3]
 before=value(b)*(1 if white else -1)
 best=sorted(legal)[0];high=-10**9
 for m in sorted(legal):
  pos=b.copy();play(pos,m,ep,white);z=square(m[2:4])
  score=(value(pos)*(1 if white else -1))-before
  if pos[z] and pos[z].lower()!='k' and attacked(pos,z,not white):score-=V[pos[z].lower()]
  if score>high:best,high=m,score
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
  while g.get('status')=='your_move':g=post(url,'/move',{'game':g['game'],'move':choose(g['fen'],g['legal_moves'])})
  if g.get('status')!='over':raise RuntimeError('unexpected /move status')
if __name__=='__main__':run()