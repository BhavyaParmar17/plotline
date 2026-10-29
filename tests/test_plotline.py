import os
import sys
from datetime import date

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

from _core.balance import analyse  # noqa: E402
from _core.planner import BriefError, normalise_brief, plan, regenerate  # noqa: E402
from _core.rules import GOALS, PLATFORMS  # noqa: E402
from _core.samples import SAMPLES  # noqa: E402
from index import app  # noqa: E402


def sample(i=0):
    b = normalise_brief(SAMPLES[i]["brief"])
    return b, plan(b)


@pytest.mark.parametrize("i", [0, 1])
def test_posts_stay_inside_month_and_on_enabled_platforms(i):
    b, posts = sample(i)
    first, last = date.fromisoformat(b["first_day"]), date.fromisoformat(b["last_day"])
    assert posts
    for p in posts:
        assert first <= date.fromisoformat(p["date"]) <= last
        assert p["platform"] in b["platforms"]
        assert p["format"] in PLATFORMS[p["platform"]]["formats"]


def test_posting_frequency_matches_brief():
    b, posts = sample(1)
    for platform, per_week in b["platforms"].items():
        count = sum(1 for p in posts if p["platform"] == platform and not p.get("extra"))
        assert per_week * 4 <= count <= per_week * 5


def test_plan_is_deterministic_and_seed_changes_it():
    b, posts = sample(0)
    assert [p["title"] for p in plan(b)] == [p["title"] for p in posts]
    b2 = normalise_brief({**SAMPLES[0]["brief"], "seed": 7})
    assert [p["title"] for p in plan(b2)] != [p["title"] for p in posts]


@pytest.mark.parametrize("i", [0, 1])
def test_pillar_mix_close_to_goal(i):
    b, posts = sample(i)
    a = analyse(b, posts)
    for row in a["themes"]:
        assert abs(row["diff"]) <= 9, row
    assert a["score"] >= 75


def test_campaign_has_announcement_and_last_call_inside_window():
    b, posts = sample(0)
    camp = b["campaigns"][0]
    mine = [p for p in posts if p["campaign"] == camp["name"]]
    assert len(mine) >= 3
    assert all(camp["start"] <= p["date"] <= camp["end"] for p in mine)
    assert mine[0]["template"] == "ca-announce" and mine[-1]["template"] == "ca-last"


def test_key_dates_get_a_post():
    b, posts = sample(0)
    assert any(p["occasion"] == "Our third anniversary" and p["date"] == "2026-11-21" for p in posts)


def test_every_service_featured():
    b, posts = sample(1)
    featured = {p["service"] for p in posts}
    assert {s["name"] for s in b["services"]} <= featured


def test_repeated_idea_is_flagged():
    b, posts = sample(0)
    clone = dict(posts[1], id="X1", date=posts[1]["date"], template="custom-X1")
    a = analyse(b, posts + [clone])
    assert any(f["type"] == "repeat" and "X1" in f["posts"] for f in a["flags"])


def test_streak_is_flagged():
    b, posts = sample(1)
    ig = [p for p in posts if p["platform"] == "linkedin"][:4]
    edited = [dict(p, theme="promote") if p in ig else p for p in posts]
    a = analyse(b, edited)
    assert any(f["type"] == "streak" for f in a["flags"])


def test_regenerate_changes_idea_and_format():
    b, posts = sample(0)
    target = next(p for p in posts if not p["campaign"] and not p["occasion"] and p["platform"] == "instagram")
    new = regenerate(b, posts, target["id"])
    assert new["id"] == target["id"] and new["title"] != target["title"]
    new2 = regenerate(b, posts, target["id"], change_format=True)
    assert new2["format"] != target["format"]


def test_validation():
    with pytest.raises(BriefError):
        normalise_brief({**SAMPLES[0]["brief"], "platforms": {}})
    with pytest.raises(BriefError):
        normalise_brief({**SAMPLES[0]["brief"], "services": []})
    with pytest.raises(BriefError):
        normalise_brief({**SAMPLES[0]["brief"], "month": "2026-13"})
    assert set(GOALS) >= {"awareness", "leads", "sales"}


def test_api_endpoints_and_exports():
    c = app.test_client()
    cfg = c.get("/api/config").get_json()
    brief = cfg["samples"][1]["brief"]
    r = c.post("/api/plan", json={"brief": brief}).get_json()
    posts = r["posts"]
    assert c.post("/api/analyze", json={"brief": brief, "posts": posts[:10]}).status_code == 200
    g = c.post("/api/regenerate", json={"brief": brief, "posts": posts, "post_id": posts[2]["id"]}).get_json()
    assert g["post"]["id"] == posts[2]["id"]
    csv = c.post("/api/export", json={"brief": brief, "posts": posts, "format": "csv"})
    assert csv.status_code == 200 and "Idea" in csv.data.decode("utf-8")
    xlsx = c.post("/api/export", json={"brief": brief, "posts": posts, "format": "xlsx"})
    assert xlsx.status_code == 200 and xlsx.data[:2] == b"PK"
    assert c.post("/api/plan", json={"brief": {**brief, "platforms": {}}}).status_code == 400
