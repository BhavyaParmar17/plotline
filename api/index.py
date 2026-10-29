"""Flask API for Plotline. Deployed on Vercel as a Python serverless function."""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, Response, jsonify, request  # noqa: E402

from _core.balance import analyse, clean_posts  # noqa: E402
from _core.export import to_csv, to_xlsx  # noqa: E402
from _core.planner import BriefError, normalise_brief, plan, regenerate  # noqa: E402
from _core.ideas import HOW_TO  # noqa: E402
from _core.rules import ASSET_TYPES, FORMATS, GOALS, PLATFORMS, THEMES  # noqa: E402
from _core.samples import SAMPLES  # noqa: E402

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2_000_000


@app.after_request
def add_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


def _payload():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BriefError("body", "Send a JSON object.")
    return data


@app.errorhandler(BriefError)
def handle_error(exc):
    return jsonify({"error": exc.message, "field": exc.field}), 400


@app.errorhandler(404)
def not_found(_e):
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(413)
def too_large(_e):
    return jsonify({"error": "That request is too large."}), 413


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "plotline"})


@app.route("/api/config")
def config():
    return jsonify({
        "goals": [{"id": k, "label": v["label"], "mix": v["mix"]} for k, v in GOALS.items()],
        "themes": [{"id": k, **v} for k, v in THEMES.items()],
        "platforms": [{"id": k, "label": v["label"], "short": v["short"], "formats": list(v["formats"])} for k, v in PLATFORMS.items()],
        "formats": {k: {"label": v["label"], "time": v["time"], "how_to": HOW_TO[k], "asset": v["asset"]} for k, v in FORMATS.items()},
        "assets": [{"id": k, "label": v} for k, v in ASSET_TYPES.items()],
        "samples": SAMPLES,
    })


def _brief_and_posts(data):
    brief = normalise_brief(data.get("brief") or {})
    posts = data.get("posts")
    if posts is not None:
        if not isinstance(posts, list) or len(posts) > 400:
            raise BriefError("posts", "Send up to 400 posts.")
        posts = clean_posts(posts)
    return brief, posts


@app.route("/api/plan", methods=["POST", "OPTIONS"])
def make_plan():
    if request.method == "OPTIONS":
        return "", 204
    brief = normalise_brief(_payload().get("brief") or {})
    posts = plan(brief)
    return jsonify({"brief": brief, "posts": posts, "analysis": analyse(brief, posts)})


@app.route("/api/analyze", methods=["POST", "OPTIONS"])
def analyze():
    if request.method == "OPTIONS":
        return "", 204
    brief, posts = _brief_and_posts(_payload())
    return jsonify({"analysis": analyse(brief, posts or [])})


@app.route("/api/regenerate", methods=["POST", "OPTIONS"])
def regen():
    if request.method == "OPTIONS":
        return "", 204
    data = _payload()
    brief, posts = _brief_and_posts(data)
    new = regenerate(brief, posts or [], str(data.get("post_id", "")), bool(data.get("change_format")))
    updated = [new if p["id"] == new["id"] else p for p in posts]
    return jsonify({"post": new, "analysis": analyse(brief, updated)})


@app.route("/api/export", methods=["POST", "OPTIONS"])
def export():
    if request.method == "OPTIONS":
        return "", 204
    data = _payload()
    brief, posts = _brief_and_posts(data)
    if posts is None:
        posts = plan(brief)
    analysis = analyse(brief, posts)
    slug = re.sub(r"[^a-z0-9]+", "-", f"{brief['business']}-{brief['month']}".lower()).strip("-") or "plotline"
    fmt = data.get("format", "csv")
    if fmt == "csv":
        return Response(to_csv(posts, analysis), mimetype="text/csv; charset=utf-8",
                        headers={"Content-Disposition": f'attachment; filename="{slug}-calendar.csv"'})
    if fmt == "xlsx":
        return Response(to_xlsx(brief, posts, analysis),
                        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        headers={"Content-Disposition": f'attachment; filename="{slug}-calendar.xlsx"'})
    raise BriefError("format", "Choose csv or xlsx.")


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
