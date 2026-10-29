"""
The planner: turns a brief (goal, audience, campaigns, services, assets,
platforms) into a month of dated posts with a balanced mix of pillars and
formats. Deterministic for a given brief and seed.
"""
from __future__ import annotations

import calendar
import random
import re
from datetime import date, timedelta

from .ideas import CAMPAIGN_TEMPLATES, HOW_TO, TEMPLATES
from .rules import (
    AFFINITY,
    ASSET_TYPES,
    CTA_BY_FUNNEL,
    FORMATS,
    GOALS,
    OBSERVANCES,
    PLATFORMS,
    THEME_ASSETS,
    THEMES,
    WEEKDAYS,
)

PLATFORM_ORDER = list(PLATFORMS)
CAMPAIGN_THEMES = {"ca-announce": "showcase", "ca-why": "educate", "ca-how": "educate", "ca-proof": "proof",
                   "ca-faq": "educate", "ca-bts": "bts", "ca-question": "engage", "ca-last": "promote"}
TEXT_ONLY = {"text", "poll", "thread", "post", "document", "story", "carousel"}


class BriefError(ValueError):
    def __init__(self, field: str, message: str):
        super().__init__(message)
        self.field = field
        self.message = message


# --------------------------------------------------------------------------- #
# Brief
# --------------------------------------------------------------------------- #
def _split(value) -> list[str]:
    if isinstance(value, list):
        items = value
    else:
        items = re.split(r"[,\n;]", str(value or ""))
    return [i.strip() for i in items if i and str(i).strip()]


def _parse_date(value, field) -> date:
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        raise BriefError(field, "Use a valid date.")


def normalise_brief(raw: dict) -> dict:
    if not isinstance(raw, dict):
        raise BriefError("body", "Send the brief as an object.")
    month = str(raw.get("month") or "")
    m = re.fullmatch(r"(\d{4})-(\d{2})", month)
    if not m or not (2000 <= int(m.group(1)) <= 2100 and 1 <= int(m.group(2)) <= 12):
        raise BriefError("month", "Choose a month to plan.")
    year, mon = int(m.group(1)), int(m.group(2))

    goal = raw.get("goal") or {}
    goal_type = goal.get("type") or "awareness"
    if goal_type not in GOALS:
        raise BriefError("goal", "Choose a goal.")

    platforms = {}
    for key, value in (raw.get("platforms") or {}).items():
        if key not in PLATFORMS:
            continue
        try:
            n = int(value)
        except (TypeError, ValueError):
            raise BriefError("platforms", "Posts per week must be a whole number.")
        if not 0 <= n <= 7:
            raise BriefError("platforms", "Use between 0 and 7 posts a week per platform.")
        if n:
            platforms[key] = n
    if not platforms:
        raise BriefError("platforms", "Turn on at least one platform.")

    services = []
    for s in raw.get("services") or []:
        name = (s.get("name") if isinstance(s, dict) else str(s)).strip()
        if name:
            services.append({"name": name[:60], "description": (s.get("description") or "").strip()[:200] if isinstance(s, dict) else ""})
    if not services:
        raise BriefError("services", "Add at least one service or product.")
    services = services[:12]

    first_day = date(year, mon, 1)
    last_day = date(year, mon, calendar.monthrange(year, mon)[1])
    campaigns = []
    for c in raw.get("campaigns") or []:
        name = (c.get("name") or "").strip()
        if not name:
            continue
        start = _parse_date(c.get("start") or first_day.isoformat(), "campaigns")
        end = _parse_date(c.get("end") or last_day.isoformat(), "campaigns")
        if end < start:
            raise BriefError("campaigns", f"“{name}” ends before it starts.")
        if end < first_day or start > last_day:
            continue
        service = (c.get("service") or "").strip()
        campaigns.append({
            "name": name[:60],
            "start": max(start, first_day).isoformat(),
            "end": min(end, last_day).isoformat(),
            "service": service if any(s["name"] == service for s in services) else "",
            "message": (c.get("message") or "").strip()[:200] or f"what makes {name} worth paying attention to",
            "cta": (c.get("cta") or "").strip()[:80],
        })

    assets = {}
    for key in ASSET_TYPES:
        try:
            assets[key] = max(0, min(500, int((raw.get("assets") or {}).get(key, 0) or 0)))
        except (TypeError, ValueError):
            raise BriefError("assets", "Asset counts must be whole numbers.")

    key_dates = []
    for k in raw.get("key_dates") or []:
        name = (k.get("name") or "").strip()
        if not name or not k.get("date"):
            continue
        d = _parse_date(k["date"], "key_dates")
        if first_day <= d <= last_day:
            key_dates.append({"date": d.isoformat(), "name": name[:60], "custom": True})
    if raw.get("include_observances", True):
        for mo, day, name in OBSERVANCES:
            if mo == mon and not any(k["date"] == date(year, mo, day).isoformat() for k in key_dates):
                key_dates.append({"date": date(year, mo, day).isoformat(), "name": name, "custom": False})
    key_dates.sort(key=lambda k: k["date"])

    audience = raw.get("audience") or {}
    try:
        seed = int(raw.get("seed") or 0)
    except (TypeError, ValueError):
        seed = 0
    return {
        "business": (raw.get("business_name") or "").strip()[:60] or "our business",
        "industry": (raw.get("industry") or "").strip()[:60] or "our industry",
        "month": month,
        "year": year,
        "mon": mon,
        "first_day": first_day.isoformat(),
        "last_day": last_day.isoformat(),
        "goal": {"type": goal_type, "label": GOALS[goal_type]["label"], "statement": (goal.get("statement") or "").strip()[:240]},
        "audience": {
            "description": (audience.get("description") or "").strip()[:160] or "our customers",
            "pains": _split(audience.get("pains"))[:8],
            "interests": _split(audience.get("interests"))[:8],
        },
        "platforms": platforms,
        "services": services,
        "campaigns": campaigns,
        "assets": assets,
        "key_dates": key_dates,
        "seed": seed,
    }


def short_audience(description: str) -> str:
    first = re.split(r"[,.;(—–-]\s", description, maxsplit=1)[0].strip()
    words = first.split()
    return " ".join(words[:7]) if words else "our customers"


def soft_lower(name: str) -> str:
    """Lower-case a service name for use mid-sentence, keeping brand-like words."""
    out = []
    for i, w in enumerate(name.split()):
        if w.isupper() or (i > 0 and w[:1].isupper() and not w[1:].islower()):
            out.append(w)
        elif any(ch.isupper() for ch in w[1:]):
            out.append(w)
        else:
            out.append(w.lower())
    return " ".join(out)


# --------------------------------------------------------------------------- #
# Allocation helpers
# --------------------------------------------------------------------------- #
def largest_remainder(weights: dict, total: int) -> dict:
    s = sum(weights.values()) or 1
    raw = {k: v / s * total for k, v in weights.items()}
    base = {k: int(v) for k, v in raw.items()}
    rest = total - sum(base.values())
    for k in sorted(raw, key=lambda k: raw[k] - base[k], reverse=True)[:rest]:
        base[k] += 1
    return base


def month_dates(brief: dict) -> list[date]:
    d = date.fromisoformat(brief["first_day"])
    end = date.fromisoformat(brief["last_day"])
    out = []
    while d <= end:
        out.append(d)
        d += timedelta(days=1)
    return out


def build_slots(brief: dict) -> list[dict]:
    slots = []
    for d in month_dates(brief):
        for p in PLATFORM_ORDER:
            n = brief["platforms"].get(p, 0)
            if n and d.weekday() in PLATFORMS[p]["days"][:n]:
                slots.append({"date": d, "platform": p})
    return slots


class Context:
    """Running state while filling the month."""

    def __init__(self, brief: dict, rng: random.Random):
        self.brief = brief
        self.rng = rng
        self.assets = dict(brief["assets"])
        self.template_use: dict[str, int] = {}
        self.service_use = {s["name"]: 0 for s in brief["services"]}
        self.format_use = {p: {f: 0 for f in PLATFORMS[p]["formats"]} for p in brief["platforms"]}
        self.platform_total = {p: 0 for p in brief["platforms"]}
        self.last = {p: {"theme": None, "format": None, "service": None} for p in brief["platforms"]}
        self.pains = brief["audience"]["pains"] or ["getting it right the first time", "finding someone they can trust", "making their budget go further"]
        self.interests = brief["audience"]["interests"] or [f"{brief['industry']} ideas", "saving time", "what’s new this season"]
        self.pain_i = 0
        self.interest_i = 0
        self.cta_i = {k: 0 for k in CTA_BY_FUNNEL}

    def next_pain(self):
        v = self.pains[self.pain_i % len(self.pains)]
        self.pain_i += 1
        return v

    def next_interest(self):
        v = self.interests[self.interest_i % len(self.interests)]
        self.interest_i += 1
        return v

    def next_cta(self, funnel):
        options = CTA_BY_FUNNEL[funnel]
        v = options[self.cta_i[funnel] % len(options)]
        self.cta_i[funnel] += 1
        return v


def choose_format(ctx: Context, platform: str, theme: str, platform_slots: int, exclude: str | None = None) -> str:
    targets = PLATFORMS[platform]["formats"]
    best, best_score = None, -1e9
    for fmt, pct in targets.items():
        if fmt == exclude and len(targets) > 1:
            continue
        target = pct / 100 * platform_slots
        deficit = target - ctx.format_use[platform][fmt]
        score = (deficit + 1.2) * AFFINITY.get(theme, {}).get(fmt, 1.0)
        need = FORMATS[fmt]["asset"]
        if need and ctx.assets.get(need, 0) <= 0 and not (need == "videos" and ctx.assets.get("ugc", 0) > 0):
            score *= 0.35
        if ctx.last[platform]["format"] == fmt:
            score *= 0.55
        score += ctx.rng.random() * 0.15
        if score > best_score:
            best, best_score = fmt, score
    return best


def choose_service(ctx: Context, platform: str) -> str:
    names = list(ctx.service_use)
    ctx.rng.shuffle(names)
    names.sort(key=lambda n: (ctx.service_use[n] + (2.0 if ctx.last[platform]["service"] == n else 0)))
    return names[0]


def allocate_asset(ctx: Context, theme: str, fmt: str) -> tuple[str | None, bool]:
    """Returns (asset label, is_gap)."""
    need = FORMATS[fmt]["asset"]
    prefs = THEME_ASSETS.get(theme, [])
    if need == "videos":
        order = ["videos", "ugc"] if theme != "proof" else ["ugc", "videos"]
    elif need == "photos":
        order = [p for p in prefs if p not in ("videos", "blog_posts")] + ["photos", "ugc"]
    elif need:
        order = [need]
    else:
        order = [p for p in prefs if p in ("testimonials", "case_studies", "blog_posts")] if fmt in TEXT_ONLY else []
        for key in order:
            if ctx.assets.get(key, 0) > 0:
                ctx.assets[key] -= 1
                return ASSET_TYPES[key], False
        return None, False
    for key in order:
        if ctx.assets.get(key, 0) > 0:
            ctx.assets[key] -= 1
            return ASSET_TYPES[key], False
    return ASSET_TYPES[need if need in ASSET_TYPES else "photos"], True


def fill(template: tuple, ctx: Context, *, service: str, campaign: dict | None = None, occasion: str = "") -> tuple[str, str]:
    brief = ctx.brief
    values = {
        "service": service,
        "service_lower": soft_lower(service),
        "audience": short_audience(brief["audience"]["description"]),
        "business": brief["business"],
        "industry": brief["industry"].capitalize(),
        "campaign": campaign["name"] if campaign else "",
        "message": campaign["message"] if campaign else "",
        "occasion": occasion,
    }
    title_t, brief_t = template[1], template[2]
    if "{pain}" in title_t + brief_t:
        values["pain"] = ctx.next_pain()
    if "{interest}" in title_t + brief_t:
        values["interest"] = ctx.next_interest()
    title = title_t.format(**values)
    text = brief_t.format(**values)
    title = title[:1].upper() + title[1:]
    return title, text


def pick_template(ctx: Context, theme: str, service: str, exclude: str | None = None) -> tuple:
    options = [t for t in TEMPLATES[theme] if t[0] != exclude and t[0] not in ("mo-occasion",)]
    ctx.rng.shuffle(options)
    options.sort(key=lambda t: (ctx.template_use.get(t[0], 0), ctx.template_use.get(f"{t[0]}::{service}", 0)))
    return options[0]


# --------------------------------------------------------------------------- #
def make_post(ctx: Context, slot: dict, theme: str, *, service: str, template: tuple, campaign: dict | None = None,
              occasion: str = "", fmt: str | None = None) -> dict:
    platform = slot["platform"]
    platform_slots = ctx.slots_per_platform[platform]
    fmt = fmt or choose_format(ctx, platform, theme, platform_slots)
    asset, gap = allocate_asset(ctx, theme, fmt)
    title, text = fill(template, ctx, service=service, campaign=campaign, occasion=occasion)
    funnel = THEMES[theme]["funnel"]
    if campaign and campaign.get("cta"):
        cta = campaign["cta"]
    elif template[0] in ("ca-last", "ca-announce") or theme == "promote":
        cta = ctx.next_cta("Decision")
    else:
        cta = ctx.next_cta(funnel)

    ctx.format_use[platform][fmt] += 1
    ctx.platform_total[platform] += 1
    ctx.service_use[service] = ctx.service_use.get(service, 0) + 1
    ctx.template_use[template[0]] = ctx.template_use.get(template[0], 0) + 1
    ctx.template_use[f"{template[0]}::{service}"] = ctx.template_use.get(f"{template[0]}::{service}", 0) + 1
    ctx.last[platform] = {"theme": theme, "format": fmt, "service": service}
    d = slot["date"]
    return {
        "date": d.isoformat(),
        "weekday": WEEKDAYS[d.weekday()],
        "time": FORMATS[fmt]["time"],
        "platform": platform,
        "platform_label": PLATFORMS[platform]["label"],
        "format": fmt,
        "format_label": FORMATS[fmt]["label"],
        "theme": theme,
        "theme_label": THEMES[theme]["label"],
        "funnel": funnel,
        "service": service,
        "campaign": campaign["name"] if campaign else "",
        "occasion": occasion,
        "title": title,
        "brief": text,
        "how_to": HOW_TO[fmt],
        "cta": cta,
        "asset": asset,
        "asset_gap": gap,
        "template": template[0],
        "status": "Draft",
        "extra": bool(slot.get("extra")),
    }


def plan(brief: dict) -> list[dict]:
    rng = random.Random(f"{brief['month']}|{brief['business']}|{brief['seed']}")
    ctx = Context(brief, rng)
    slots = build_slots(brief)

    # occasions: use a slot that day or add one on the main platform
    primary = next(p for p in ("instagram", "linkedin", "facebook", "x", "youtube_shorts") if p in brief["platforms"])
    auto_count = 0
    for kd in brief["key_dates"]:
        if not kd["custom"]:
            if auto_count >= 3:
                continue
            auto_count += 1
        d = date.fromisoformat(kd["date"])
        same_day = [s for s in slots if s["date"] == d and "fixed" not in s]
        if same_day:
            target = sorted(same_day, key=lambda s: PLATFORM_ORDER.index(s["platform"]) if s["platform"] != "youtube_shorts" else 9)[0]
        else:
            target = {"date": d, "platform": primary, "extra": True}
            slots.append(target)
        target["fixed"] = {"kind": "occasion", "name": kd["name"]}
    slots.sort(key=lambda s: (s["date"], PLATFORM_ORDER.index(s["platform"])))

    ctx.slots_per_platform = {p: sum(1 for s in slots if s["platform"] == p) for p in brief["platforms"]}

    # campaigns: an announcement, a closing reminder and evenly spaced posts between
    for camp in brief["campaigns"]:
        start, end = date.fromisoformat(camp["start"]), date.fromisoformat(camp["end"])
        window = [s for s in slots if start <= s["date"] <= end and "fixed" not in s]
        if not window:
            continue
        count = min(len(window), len(CAMPAIGN_TEMPLATES), max(2 if len(window) > 1 else 1, round(len(window) * 0.4)))
        if count == 1:
            picks = [0]
        else:
            picks = sorted({round(i * (len(window) - 1) / (count - 1)) for i in range(count)})
        middle = CAMPAIGN_TEMPLATES[1:-1]
        for j, idx in enumerate(picks):
            if j == 0:
                tpl = CAMPAIGN_TEMPLATES[0]
            elif j == len(picks) - 1:
                tpl = CAMPAIGN_TEMPLATES[-1]
            else:
                tpl = middle[(j - 1) % len(middle)]
            window[idx]["fixed"] = {"kind": "campaign", "campaign": camp, "template": tpl}

    targets = largest_remainder(GOALS[brief["goal"]["type"]]["mix"], len(slots))
    assigned = {t: 0 for t in THEMES}
    for s in slots:
        f = s.get("fixed")
        if f and f["kind"] == "occasion":
            assigned["moments"] += 1
        elif f and f["kind"] == "campaign":
            assigned[CAMPAIGN_THEMES[f["template"][0]]] += 1

    posts = []
    day_themes: dict[str, list[str]] = {}
    for s in slots:
        f = s.get("fixed")
        key = s["date"].isoformat()
        if f and f["kind"] == "occasion":
            theme = "moments"
            service = choose_service(ctx, s["platform"])
            tpl = next(t for t in TEMPLATES["moments"] if t[0] == "mo-occasion")
            post = make_post(ctx, s, theme, service=service, template=tpl, occasion=f["name"])
        elif f and f["kind"] == "campaign":
            camp, tpl = f["campaign"], f["template"]
            theme = CAMPAIGN_THEMES[tpl[0]]
            service = camp["service"] or choose_service(ctx, s["platform"])
            post = make_post(ctx, s, theme, service=service, template=tpl, campaign=camp)
        else:
            def score(t):
                deficit = targets[t] - assigned[t]
                sc = deficit + rng.random() * 0.3
                if ctx.last[s["platform"]]["theme"] == t:
                    sc -= 2.5
                if t in day_themes.get(key, []):
                    sc -= 1.2
                if t == "moments":
                    sc -= 0.8
                return sc

            theme = max(THEMES, key=score)
            assigned[theme] += 1
            service = choose_service(ctx, s["platform"])
            tpl = pick_template(ctx, theme, service)
            post = make_post(ctx, s, theme, service=service, template=tpl)
        day_themes.setdefault(key, []).append(post["theme"])
        posts.append(post)

    for i, p in enumerate(posts, start=1):
        p["id"] = f"P{i:03d}"
    return posts


def regenerate(brief: dict, posts: list[dict], post_id: str, change_format: bool = False) -> dict:
    """New idea for one post, avoiding templates and formats already used nearby."""
    target = next((p for p in posts if p.get("id") == post_id), None)
    if not target:
        raise BriefError("post", "That post isn’t in the plan.")
    rng = random.Random(f"{post_id}|{target.get('template')}|{len(posts)}|{brief['seed']}|{target.get('title')}")
    ctx = Context(brief, rng)
    for p in posts:
        if p.get("id") == post_id:
            continue
        ctx.template_use[p.get("template", "")] = ctx.template_use.get(p.get("template", ""), 0) + 1
        ctx.template_use[f"{p.get('template')}::{p.get('service')}"] = ctx.template_use.get(f"{p.get('template')}::{p.get('service')}", 0) + 1
        if p.get("platform") in ctx.format_use and p.get("format") in ctx.format_use[p["platform"]]:
            ctx.format_use[p["platform"]][p["format"]] += 1
    ctx.slots_per_platform = {pl: sum(1 for p in posts if p.get("platform") == pl) for pl in brief["platforms"]}
    platform = target["platform"] if target["platform"] in brief["platforms"] else next(iter(brief["platforms"]))
    theme = target["theme"] if target["theme"] in THEMES else "educate"
    service = target.get("service") or brief["services"][0]["name"]
    camp = next((c for c in brief["campaigns"] if c["name"] == target.get("campaign")), None)
    ctx.pain_i = rng.randrange(0, 50)
    ctx.interest_i = rng.randrange(0, 50)
    ctx.cta_i = {k: rng.randrange(0, 5) for k in ctx.cta_i}
    if camp:
        options = [t for t in CAMPAIGN_TEMPLATES if t[0] != target.get("template") and CAMPAIGN_THEMES[t[0]] == theme] or \
                  [t for t in CAMPAIGN_TEMPLATES if t[0] != target.get("template")]
        tpl = rng.choice(options)
        theme = CAMPAIGN_THEMES[tpl[0]]
    elif target.get("occasion"):
        tpl = next(t for t in TEMPLATES["moments"] if t[0] == "mo-occasion")
    else:
        tpl = pick_template(ctx, theme, service, exclude=target.get("template"))
    fmt = target["format"]
    if change_format or fmt not in PLATFORMS[platform]["formats"]:
        fmt = choose_format(ctx, platform, theme, ctx.slots_per_platform.get(platform, 1), exclude=fmt if change_format else None)
    slot = {"date": date.fromisoformat(target["date"]), "platform": platform, "extra": target.get("extra")}
    new = make_post(ctx, slot, theme, service=service, template=tpl, campaign=camp, occasion=target.get("occasion", ""), fmt=fmt)
    new["id"] = post_id
    new["status"] = target.get("status", "Draft")
    return new
