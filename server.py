"""
Backend for “An Optimal Sample-Selection System”  (Flask)
"""
import json, random, time
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import main

# --- paths ---
BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
DB = BASE / "db"; DB.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=str(STATIC), static_url_path="")
CORS(app)

@app.get("/")
def index(): return send_from_directory(STATIC, "index.html")

# --- helpers ---
def _run_algo(p:dict)->dict:
    m,n,k,j,s = [int(p[x]) for x in ("m","n","k","j","s")]
    # 若提供具体 selected 列表，则直接用
    if isinstance(p.get("selected"), list) and p["selected"]:
        selected = sorted(int(x) for x in p["selected"])
        n = len(selected)  # 覆盖 n 值
    else:
        selected = sorted(random.sample(range(1, m+1), n))

    min_s  = int(p.get("min_s_covered",1))
    trials = int(p.get("max_trials",50))
    spr    = int(p.get("sample_per_round",200))

    groups = main.multi_round_greedy(selected,k,j,s,min_s,max_trials=trials,sample_per_round=spr)
    return {"m":m,"n":n,"k":k,"j":j,"s":s,"selected":selected,"groups":groups}

def _save_db_file(d:dict)->str:
    m,n,k,j,s = [d[t] for t in ("m","n","k","j","s")]
    patt = f"{m}-{n}-{k}-{j}-{s}-*-*.db"
    idx  = len(list(DB.glob(patt)))+1
    y    = len(d.get("groups",[]))
    fname= f"{m}-{n}-{k}-{j}-{s}-{idx}-{y}.db"
    with open(DB/fname,"w",encoding="utf-8") as f: json.dump(d,f)
    return fname

# --- API ---
@app.post("/api/optimize")
def api_opt():
    t0=time.time()
    res=_run_algo(request.json or {})
    res["runtime"]=round(time.time()-t0,3)
    return jsonify(res)

@app.post("/api/save-db")
def api_save():
    data=request.json
    if not isinstance(data,dict): return {"error":"bad data"},400
    fname=_save_db_file(data); return {"file":fname}

@app.get("/api/files")
def api_files(): return jsonify(sorted(f.name for f in DB.glob("*.db")))

@app.get("/api/file/<name>")
def api_load(name):
    fp=DB/name
    if not fp.exists(): return {"error":"not found"},404
    return jsonify(json.load(fp.open()))

@app.delete("/api/file/<name>")
def api_del(name):
    fp=DB/name
    if not fp.exists(): return {"error":"not found"},404
    fp.unlink(); return {"ok":True}

if __name__=="__main__":
    if not (STATIC/"index.html").exists():
        print("⚠  static/index.html missing")
    app.run(port=8000,debug=True)
