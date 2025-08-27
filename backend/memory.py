import os, sqlite3, uuid, json, time
from typing import List, Dict, Any

DB_DIR = "data"
DB_PATH = os.path.join(DB_DIR, "chat.db")
os.makedirs(DB_DIR, exist_ok=True)

def _conn():
    return sqlite3.connect(DB_PATH)

def _init():
    with _conn() as con:
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS sessions(session_id TEXT,user_id TEXT,title TEXT,status TEXT,created_at REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS messages(session_id TEXT,role TEXT,content TEXT,ts REAL)")
        cur.execute("CREATE TABLE IF NOT EXISTS slots(session_id TEXT,key TEXT,value TEXT,PRIMARY KEY(session_id,key))")
        con.commit()
_init()

def create_session(user_id:str,title:str)->str:
    sid=str(uuid.uuid4())
    with _conn() as con:
        con.execute("INSERT INTO sessions VALUES(?,?,?,?,?)",(sid,user_id,title,"ongoing",time.time()))
        con.commit()
    return sid

def add_message(sid,role,content):
    with _conn() as con:
        con.execute("INSERT INTO messages VALUES(?,?,?,?)",(sid,role,content,time.time()))
        con.commit()

def get_history(sid):
    with _conn() as con:
        rows=con.execute("SELECT role,content FROM messages WHERE session_id=? ORDER BY ts",(sid,)).fetchall()
    return [{"role":r,"content":c} for r,c in rows]

def get_slots(sid)->Dict[str,Any]:
    with _conn() as con:
        rows=con.execute("SELECT key,value FROM slots WHERE session_id=?",(sid,)).fetchall()
    out={}
    for k,v in rows:
        try: out[k]=json.loads(v)
        except: out[k]=v
    return out

def update_slots(sid,new:Dict[str,Any]):
    if not new:return
    with _conn() as con:
        for k,v in new.items():
            val=json.dumps(v) if isinstance(v,(dict,list)) else str(v)
            con.execute("INSERT INTO slots VALUES(?,?,?) ON CONFLICT(session_id,key) DO UPDATE SET value=excluded.value",(sid,k,val))
        con.commit()
