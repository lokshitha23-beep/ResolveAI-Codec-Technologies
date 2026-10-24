from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from pathlib import Path
from datetime import datetime, timedelta, timezone
import sqlite3, re
ROOT=Path(__file__).resolve().parent; DB=ROOT/'resolveai.db'
app=FastAPI(title='ResolveAI Original',version='1.0.0'); app.mount('/static',StaticFiles(directory=ROOT/'static'),name='static')
def db():
 c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c
def init():
 with db() as c:
  c.execute("""CREATE TABLE IF NOT EXISTS tickets(id INTEGER PRIMARY KEY AUTOINCREMENT,subject TEXT NOT NULL,description TEXT NOT NULL,category TEXT NOT NULL,priority TEXT NOT NULL,status TEXT NOT NULL DEFAULT 'Open',customer TEXT NOT NULL,assignee TEXT NOT NULL DEFAULT 'Unassigned',created_at TEXT NOT NULL,due_at TEXT NOT NULL,notes TEXT NOT NULL DEFAULT '')""")
  if c.execute('SELECT COUNT(*) FROM tickets').fetchone()[0]==0:
   now=datetime.now(timezone.utc)
   sample=[('Cannot sign in','Password reset link does not work','Account Access','High','Open','Sam Taylor','Support A',2),('Invoice amount looks incorrect','My latest invoice contains a duplicate charge','Billing','Medium','In Progress','Priya Shah','Billing Team',24),('App crashes on export','Export fails when I download a report','Technical Issue','High','Open','Alex Chen','Support B',1)]
   for s,d,cat,p,st,cu,ass,hours in sample:c.execute('INSERT INTO tickets(subject,description,category,priority,status,customer,assignee,created_at,due_at) VALUES(?,?,?,?,?,?,?,?,?)',(s,d,cat,p,st,cu,ass,now.isoformat(),(now+timedelta(hours=hours)).isoformat()))
init()
class TicketIn(BaseModel): subject:str=Field(min_length=4,max_length=180); description:str=Field(min_length=8,max_length=5000); customer:str=Field(min_length=2,max_length=100); priority:str='Medium'
class UpdateIn(BaseModel): status:str|None=None; assignee:str|None=None; notes:str|None=None
STOP={'the','and','for','with','this','that','from','have','your','into','when','does','not','but','are','was','can','you','my','our','issue','help'}
def tokens(s):return {w for w in re.findall(r'[a-z0-9]+',s.lower()) if len(w)>2 and w not in STOP}
def similarity(a,b):
 x,y=tokens(a),tokens(b)
 return round(100*len(x&y)/len(x|y)) if x|y else 0
def classify(text):
 t=text.lower()
 rules={'Billing':['invoice','payment','charge','refund','billing','price'],'Account Access':['login','sign in','password','account','locked'],'Technical Issue':['crash','error','bug','slow','fail','export','broken']}
 scores={k:sum(w in t for w in words) for k,words in rules.items()}; best=max(scores,key=scores.get)
 if scores[best]==0:best='General Inquiry'
 priority='High' if any(w in t for w in ['urgent','critical','blocked','cannot access','down']) else ('Medium' if best!='General Inquiry' else 'Low')
 return best,priority

def allrows(sql,args=()):
 with db() as c:return [dict(x) for x in c.execute(sql,args).fetchall()]
def enrich(t):
 now=datetime.now(timezone.utc); due=datetime.fromisoformat(t['due_at']); seconds=int((due-now).total_seconds()); t['seconds_remaining']=seconds;t['sla_state']='Overdue' if seconds<0 and t['status'] not in ('Resolved','Closed') else ('Due soon' if seconds<3600 and t['status'] not in ('Resolved','Closed') else 'On track');return t
@app.get('/',response_class=HTMLResponse)
def home():return (ROOT/'static/index.html').read_text(encoding='utf-8')
@app.get('/api/tickets')
def tickets():return [enrich(t) for t in allrows('SELECT * FROM tickets ORDER BY id DESC')]
@app.post('/api/tickets')
def create(x:TicketIn):
 cat,guess=classify(x.subject+' '+x.description); priority=x.priority if x.priority in ('Low','Medium','High','Urgent') else guess
 now=datetime.now(timezone.utc); hours={'Low':72,'Medium':24,'High':4,'Urgent':1}[priority]
 with db() as c:cur=c.execute('INSERT INTO tickets(subject,description,category,priority,customer,created_at,due_at) VALUES(?,?,?,?,?,?,?)',(x.subject,x.description,cat,priority,x.customer,now.isoformat(),(now+timedelta(hours=hours)).isoformat())); tid=cur.lastrowid
 return {'id':tid,'category_suggestion':cat,'priority_suggestion':guess,'message':'Ticket created'}
@app.patch('/api/tickets/{tid}')
def update(tid:int,x:UpdateIn):
 changes={k:v for k,v in x.model_dump(exclude_none=True).items() if k in {'status','assignee','notes'}}
 if 'status' in changes and changes['status'] not in {'Open','In Progress','Waiting for Customer','Resolved','Closed'}:raise HTTPException(400,'Invalid status')
 if not changes:raise HTTPException(400,'No valid changes supplied')
 with db() as c:
  cur=c.execute('UPDATE tickets SET '+','.join(k+'=?' for k in changes)+' WHERE id=?',(*changes.values(),tid))
  if not cur.rowcount:raise HTTPException(404,'Ticket not found')
 return {'ok':True}
@app.get('/api/similar')
def similar(q:str):
 candidates=allrows('SELECT * FROM tickets'); scored=[]
 for t in candidates:
  score=similarity(q,t['subject']+' '+t['description'])
  if score>=15:scored.append({**enrich(t),'similarity':score})
 return sorted(scored,key=lambda x:x['similarity'],reverse=True)[:5]
@app.get('/api/summary')
def summary():
 ts=allrows('SELECT * FROM tickets'); active=[enrich(t) for t in ts if t['status'] not in ('Resolved','Closed')]
 return {'total':len(ts),'open':sum(t['status']=='Open' for t in ts),'active':len(active),'overdue':sum(t['sla_state']=='Overdue' for t in active),'high_priority':sum(t['priority'] in ('High','Urgent') and t['status'] not in ('Resolved','Closed') for t in ts)}
