"""
aug_gc Server — Local deployment via Flask + SSE streaming.
Run:  python app.py
Then: open http://localhost:9360
"""

import json
import time
from flask import Flask, request, Response, send_from_directory
from engine import AugGC
from etymos import TMIAnalyzer, ETYMOS_DB

app = Flask(__name__, static_folder="static")
gc = AugGC()
tmi = TMIAnalyzer()

# ── Serve frontend ──────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

# ── API ─────────────────────────────────────────────────────

@app.route("/api/status")
def status():
    return json.dumps(gc.status()), 200, {"Content-Type": "application/json"}

@app.route("/api/compose", methods=["POST"])
def compose():
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()
    if not text:
        return json.dumps({"error": "Empty signal"}), 400

    def stream():
        for event in gc.compose_streaming(text):
            yield f"data: {json.dumps(event)}\n\n"

    return Response(stream(), content_type="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

@app.route("/api/history")
def history():
    entries = gc.ratchet.entries[-20:]
    return json.dumps({
        "entries": entries,
        "total_mass": gc.ratchet.total_mass(),
        "phase_locks": gc.field.phase_lock_count,
    }), 200, {"Content-Type": "application/json"}

@app.route("/api/etymos/<word>")
def etymos_lookup(word):
    rec = tmi.analyze_word(word)
    return json.dumps(rec.to_dict()), 200, {"Content-Type": "application/json"}

@app.route("/api/tmi", methods=["POST"])
def tmi_analyze():
    body = request.get_json(silent=True) or {}
    text = body.get("text", "").strip()
    if not text:
        return json.dumps({"error": "Empty text"}), 400
    analysis = tmi.analyze_text(text)
    return json.dumps(analysis.to_dict()), 200, {"Content-Type": "application/json"}

# ── Boot ────────────────────────────────────────────────────

if __name__ == "__main__":
    print()
    print("  ╔══════════════════════════════════════════════╗")
    print("  ║  aug_gc — Augmented Generative Composer      ║")
    print("  ║  Temporal Composition via τₖ Field Dynamics   ║")
    print("  ╚══════════════════════════════════════════════╝")
    print()
    s = gc.status()
    print(f"  substrate : {s['substrate']}  ({s.get('substrate_kind', 'native')})")
    if s['substrate_available'] and s.get('substrate_kind') == 'atmanOS-faculties':
        mode = "atmanOS faculties (Archivist→Oracle→Harmonizer→Composer) + τₖ selection"
    elif s['substrate_available']:
        mode = "Ollama backbone + τₖ selection"
    else:
        mode = "native coherence engine (set ANTHROPIC_API_KEY + pip install anthropic for faculties)"
    print(f"  mode      : {mode}")
    print(f"  port      : 9360  (936 Hz × 10)")
    print()
    print("  → http://localhost:9360")
    print()
    app.run(host="0.0.0.0", port=9360, debug=False, threaded=True)
