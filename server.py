"""
Backend for “An Optimal Sample‑Selection System” (Flask)

2025‑05‑03 update #2
───────────────────
* 新算法文件已改名为 **main.py**；后端直接 `import main as solver`。
* 继续支持 `time_limit` 参数与自适应尝试次数／采样率，无其他行为改动。
"""
from __future__ import annotations

import json, random, time, importlib
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS


# ---------------------------------------------------------------------------
# Import solver (main.py) and允许在 debug 模式下自动热重载
# ---------------------------------------------------------------------------
import main as solver  # noqa: E402  — 本目录下的 main.py
importlib.reload(solver)

# ---------------------------------------------------------------------------
# 目录设置
# ---------------------------------------------------------------------------
BASE   = Path(__file__).resolve().parent
STATIC = BASE / "static"
DB     = BASE / "db"; DB.mkdir(exist_ok=True)

app = Flask(__name__, static_folder=str(STATIC), static_url_path="")
CORS(app)

@app.get("/")
def index():
    return send_from_directory(STATIC, "index.html")

# ---------------------------------------------------------------------------
# 核心算法调用包装
# ---------------------------------------------------------------------------

def _run_algo(p: dict) -> dict:
    """解析前端参数，调用 solver.multi_round_greedy_with_prune 并返回结果字典"""

    # 基础整数参数 -----------------------------------------------------------
    m, n, k, j, s = [int(p[x]) for x in ("m", "n", "k", "j", "s")]

    # 选择样本列表 -----------------------------------------------------------
    if isinstance(p.get("selected"), list) and p["selected"]:
        selected = sorted(int(x) for x in p["selected"])
        n = len(selected)                               # 覆盖 n 值
    else:
        selected = sorted(random.sample(range(1, m + 1), n))

    # 其他可选参数 -----------------------------------------------------------
    min_s       = int(p.get("min_s_covered", 1))
    time_limit  = float(p.get("time_limit", 55.0))   # 终止上限（秒）

    # 尝试次数与采样率：若前端留空/0，则根据 n & time_limit 自适应
    trials_raw = int(p.get("max_trials", 0) or 0)
    spr_raw    = int(p.get("sample_per_round", 0) or 0)

    if trials_raw <= 0 or spr_raw <= 0:
        # 若 solver 没有该辅助函数，则退回默认值
        if hasattr(solver, "get_adaptive_effort_levels"):
            levels = solver.get_adaptive_effort_levels(n, k, time_limit)
            best   = levels[-1] if levels else {"max_trials": 50, "sample_per_round": 200}
            if trials_raw <= 0:
                trials_raw = best["max_trials"]
            if spr_raw <= 0:
                spr_raw    = best["sample_per_round"]
        else:
            trials_raw = trials_raw or 50
            spr_raw    = spr_raw or 200

    # ---------------- 调用求解器 ----------------
    groups = solver.multi_round_greedy_with_prune(
        selected, k, j, s, min_s,
        max_trials=trials_raw,
        sample_per_round=spr_raw,
        prune_active=True,
    )

    return {
        "m": m, "n": n, "k": k, "j": j, "s": s,
        "selected": selected,
        "groups": groups,
        "time_limit": time_limit,
        "max_trials": trials_raw,
        "sample_per_round": spr_raw,
    }

# ---------------------------------------------------------------------------
# 数据库文件操作
# ---------------------------------------------------------------------------

def _save_db_file(d: dict) -> str:
    m, n, k, j, s = [d[t] for t in ("m", "n", "k", "j", "s")]
    patt = f"{m}-{n}-{k}-{j}-{s}-*-*.db"
    idx  = len(list(DB.glob(patt))) + 1
    y    = len(d.get("groups", []))
    fname = f"{m}-{n}-{k}-{j}-{s}-{idx}-{y}.db"
    with open(DB / fname, "w", encoding="utf-8") as f:
        json.dump(d, f)
    return fname

# ---------------------------------------------------------------------------
# REST API
# ---------------------------------------------------------------------------

@app.post("/api/optimize")
def api_opt():
    t0 = time.time()
    res = _run_algo(request.json or {})
    res["runtime"] = round(time.time() - t0, 3)
    return jsonify(res)

@app.post("/api/save-db")
def api_save():
    data = request.json
    if not isinstance(data, dict):
        return {"error": "bad data"}, 400
    fname = _save_db_file(data)
    return {"file": fname}

@app.get("/api/files")
def api_files():
    return jsonify(sorted(f.name for f in DB.glob("*.db")))

@app.get("/api/file/<name>")
def api_load(name):
    fp = DB / name
    if not fp.exists():
        return {"error": "not found"}, 404
    return jsonify(json.load(fp.open()))

@app.delete("/api/file/<name>")
def api_del(name):
    fp = DB / name
    if not fp.exists():
        return {"error": "not found"}, 404
    fp.unlink()
    return {"ok": True}

# ---------------------------------------------------------------------------
# Main — dev mode
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if not (STATIC / "index.html").exists():
        print("⚠ static/index.html missing")
    app.run(port=8000, debug=True)
#########################################################################3
###