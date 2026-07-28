import os, json, logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

FIELD_NAMES = [
    "客户/品牌名称","联系人","联系方式","所属行业","核心产品/服务",
    "项目所处阶段","所在城市","目标用户画像","用户核心痛点","用户决策路径",
    "主要竞品","你的核心差异","营销目标","推广渠道偏好","预算范围",
    "期望周期","品牌调性","有没有参考账号","现有素材情况","其他补充"
]

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"n8n_webhook": ""}
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"n8n_webhook": ""}

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

@app.route("/")
def index():
    return render_template("form.html")

@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "POST":
        data = request.json or {}
        cfg = load_config()
        if "n8n_webhook" in data:
            cfg["n8n_webhook"] = data["n8n_webhook"]
        save_config(cfg)
        return jsonify({"ok": True})
    cfg = load_config()
    return jsonify(cfg)

@app.route("/api/submit", methods=["POST"])
def api_submit():
    cfg = load_config()
    data = request.json or {}
    results = {"n8n": None}
    payload = {n: data.get(n, "") for n in FIELD_NAMES}
    if cfg.get("n8n_webhook"):
        try:
            resp = requests.post(cfg["n8n_webhook"], json=payload, timeout=15)
            results["n8n"] = {"ok": resp.status_code < 400, "status": resp.status_code}
            log.info(f"n8n 发送成功: {resp.status_code}")
        except Exception as e:
            results["n8n"] = {"ok": False, "error": str(e)}
            log.warning(f"n8n 发送失败: {e}")
    return jsonify({"ok": True, "results": results})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5101))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
