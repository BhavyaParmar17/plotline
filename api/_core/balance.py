"""
Balance and repetition checks. Runs on any list of posts, so it re-checks the
calendar after people move, edit, add or delete posts.
"""
from __future__ import annotations

import re
from datetime import date

from .rules import FORMATS, GOALS, PLATFORMS, THEMES, WEEKDAYS

STOP = set("""
a an and are as at be by for from how in into is it its of on or our the their this to what when why with you your
we us they them more most about vs before after who isn’t isn't it’s it's this that these those month week
""".split())
REQUIRED = ("id", "date", "platform", "format", "theme", "title")


def tokens(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9’']+", (text or "").lower()) if w not in STOP and len(w) > 2}


def jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def clean_posts(posts: list) -> list[dict]:
    out = []
    for p in posts or []:
        if not isinstance(p, dict) or any(k not in p for k in REQUIRED):
            continue
        try:
            date.fromisoformat(p["date"])
        except ValueError:
            continue
        if p["platform"] not in PLATFORMS or p["theme"] not in THEMES or p["format"] not in FORMATS:
            continue
        out.append(p)
    return sorted(out, key=lambda p: (p["date"], list(PLATFORMS).index(p["platform"]), p["id"]))


def analyse(brief: dict, posts: list[dict]) -> dict:
    posts = clean_posts(posts)
    n = len(posts)
    mix = GOALS[brief["goal"]["type"]]["mix"]
    flags: list[dict] = []

    def flag(kind, severity, ids, message, suggestion):
        flags.append({"type": kind, "severity": severity, "posts": ids, "message": message, "suggestion": suggestion})

    # ---- theme balance
    theme_rows = []
    for t, meta in THEMES.items():
        count = sum(1 for p in posts if p["theme"] == t)
        pct = count / n * 100 if n else 0
        theme_rows.append({"theme": t, "label": meta["label"], "color": meta["color"], "count": count,
                           "pct": round(pct, 1), "target_pct": mix[t], "diff": round(pct - mix[t], 1)})
    theme_dev = sum(abs(r["diff"]) for r in theme_rows) / 2
    for r in theme_rows:
        if n >= 8 and r["diff"] > 12:
            flag("balance", "medium", [], f"{r['label']} is {r['pct']:.0f}% of the month, well above the {r['target_pct']}% this goal needs.",
                 f"Swap a few {r['label'].lower()} posts for under-used pillars.")
        elif n >= 8 and r["diff"] < -10:
            flag("balance", "low", [], f"{r['label']} is only {r['pct']:.0f}% of the month against a {r['target_pct']}% target.",
                 f"Add or convert a post to {r['label'].lower()}.")

    # ---- funnel
    funnel = {}
    for p in posts:
        f = THEMES[p["theme"]]["funnel"]
        funnel[f] = funnel.get(f, 0) + 1

    # ---- formats per platform
    format_rows = []
    format_dev = 0.0
    for pl, meta in PLATFORMS.items():
        mine = [p for p in posts if p["platform"] == pl]
        if not mine:
            continue
        rows = []
        for fmt, target in meta["formats"].items():
            c = sum(1 for p in mine if p["format"] == fmt)
            pct = c / len(mine) * 100
            rows.append({"format": fmt, "label": FORMATS[fmt]["label"], "count": c, "pct": round(pct, 1), "target_pct": target})
            format_dev += abs(pct - target) / 2 * len(mine) / max(n, 1)
        format_rows.append({"platform": pl, "label": meta["label"], "total": len(mine), "formats": rows})
        used = {p["format"] for p in mine}
        if len(mine) >= 6 and len(used) == 1:
            flag("format", "medium", [p["id"] for p in mine[:4]], f"Every {meta['label']} post is a {FORMATS[mine[0]['format']]['label'].lower()}.",
                 "Mix in another format so the feed doesn’t look the same every time.")

    # ---- streaks on each platform
    for pl in PLATFORMS:
        mine = [p for p in posts if p["platform"] == pl]
        for key, label in (("theme", "pillar"), ("format", "format")):
            if key == "format" and len(PLATFORMS[pl]["formats"]) == 1:
                continue
            run = []
            for p in mine + [None]:
                if p and run and p[key] == run[-1][key]:
                    run.append(p)
                    continue
                if len(run) >= 3:
                    name = THEMES[run[0]["theme"]]["label"] if key == "theme" else FORMATS[run[0]["format"]]["label"]
                    flag("streak", "medium" if len(run) >= 4 else "low", [x["id"] for x in run],
                         f"{len(run)} {PLATFORMS[pl]['label']} posts in a row use the same {label}: {name}.",
                         f"Change the {label} of the middle post.")
                run = [p] if p else []

    # ---- near-duplicate ideas
    seen_pairs = set()

    def idea_tokens(p):
        noise = tokens(p.get("service", "")) | tokens(p.get("campaign", "")) | tokens(p.get("occasion", ""))
        return tokens(p["title"]) - noise

    toks = {p["id"]: idea_tokens(p) for p in posts}
    for i, a in enumerate(posts):
        da = date.fromisoformat(a["date"])
        for b in posts[i + 1:]:
            gap = abs((date.fromisoformat(b["date"]) - da).days)
            if gap > 14:
                break
            if a.get("occasion") or b.get("occasion"):
                continue
            series = a.get("campaign") and a.get("campaign") == b.get("campaign")
            same_template = bool(a.get("template")) and a.get("template") == b.get("template") and a.get("service") == b.get("service")
            shared = toks[a["id"]] & toks[b["id"]]
            rotated = bool(a.get("template")) and a.get("template") == b.get("template") and a.get("service") != b.get("service")
            similar = not rotated and len(shared) >= 2 and jaccard(toks[a["id"]], toks[b["id"]]) >= 0.6
            same_platform = a["platform"] == b["platform"]
            near_clone = (same_platform and gap <= 5 and not series and a["theme"] == b["theme"]
                          and a.get("service") == b.get("service") and a["format"] == b["format"])
            if not (same_template or similar or near_clone):
                continue
            if series and not same_template:
                continue
            seen_pairs.add((a["id"], b["id"]))
            if same_template or similar:
                msg = f"“{a['title']}” and “{b['title']}” are close to the same idea, {gap} day{'s' if gap != 1 else ''} apart."
                sev = "high" if same_platform and gap <= 7 else "medium"
            else:
                msg = f"Two {PLATFORMS[a['platform']]['label']} posts about {a.get('service')} with the same pillar and format within {gap} days."
                sev = "medium"
            flag("repeat", sev, [a["id"], b["id"]], msg, "Regenerate one of them, or change its format or service.")

    # ---- templates over-used
    use = {}
    for p in posts:
        if p.get("template") and not p["template"].startswith(("ca-", "mo-occasion")):
            use.setdefault(p["template"], []).append(p["id"])
    for tpl, ids in use.items():
        if len(ids) >= 4:
            flag("repeat", "low", ids, f"The same idea angle is used {len(ids)} times this month.", "Regenerate a couple for fresh angles.")

    # ---- services and campaigns
    service_rows = []
    for s in brief["services"]:
        c = sum(1 for p in posts if p.get("service") == s["name"])
        service_rows.append({"name": s["name"], "count": c})
        if c == 0 and n:
            flag("coverage", "medium", [], f"{s['name']} isn’t featured anywhere this month.", "Change the service on one post to feature it.")
    campaign_rows = []
    for camp in brief["campaigns"]:
        c = sum(1 for p in posts if p.get("campaign") == camp["name"])
        campaign_rows.append({"name": camp["name"], "count": c, "start": camp["start"], "end": camp["end"]})
        if c == 0:
            flag("coverage", "high", [], f"The {camp['name']} campaign has no posts.", "Add posts inside its dates or check the platforms are on.")

    # ---- quiet stretches
    dates = sorted({date.fromisoformat(p["date"]) for p in posts})
    for a, b in zip(dates, dates[1:]):
        if (b - a).days >= 5:
            flag("gap", "low", [], f"Nothing is scheduled from {a.strftime('%d %b')} to {b.strftime('%d %b')}.", "Add a story or a quick post in the gap.")

    # ---- assets
    gaps = [p for p in posts if p.get("asset_gap")]
    if gaps:
        needed = {}
        for p in gaps:
            needed[p.get("asset") or "assets"] = needed.get(p.get("asset") or "assets", 0) + 1
        need_text = ", ".join(f"{v} × {k.lower()}" for k, v in needed.items())
        flag("asset", "medium", [p["id"] for p in gaps], f"{len(gaps)} posts need assets you haven’t listed: {need_text}.",
             "Plan a shoot or switch those posts to a text-led format.")

    weekday = {d: 0 for d in WEEKDAYS}
    for p in posts:
        weekday[WEEKDAYS[date.fromisoformat(p["date"]).weekday()]] += 1

    sev_cost = {"high": 7, "medium": 3, "low": 1}
    score = 100 - theme_dev * 0.9 - format_dev * 0.35 - sum(sev_cost[f["severity"]] for f in flags)
    score = int(max(0, min(100, round(score))))
    label = "Well balanced" if score >= 85 else "Mostly balanced" if score >= 70 else "Needs work"
    flagged_ids = sorted({i for f in flags for i in f["posts"]})
    return {
        "count": n,
        "score": score,
        "score_label": label,
        "themes": theme_rows,
        "funnel": funnel,
        "formats": format_rows,
        "services": service_rows,
        "campaigns": campaign_rows,
        "weekdays": weekday,
        "flags": flags,
        "flagged_posts": flagged_ids,
        "asset_gaps": len(gaps),
    }
