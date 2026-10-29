# Plotline — Social Media Calendar Planner from Business Goals

Generate a **monthly content calendar** from a business goal, target audience, campaigns, services and available assets. Plotline **balances formats and themes**, **flags repetitive ideas**, and **exports to CSV or Excel** for review.

**Tech stack:** Python · Flask (API) · openpyxl (Excel export) · React 18 (Vite) · Framer Motion · deployed on Vercel. No paid AI API or key is needed: the planner is rule-based and deterministic, so every decision can be explained and tested.

---

## Features

### The brief
1. **Business and goal:** name, industry, month and one of six goals (awareness, leads, sales, engagement, launch, retention), plus the goal in your own words.
2. **Audience:** who they are, their pains and their interests. These are woven into post ideas.
3. **Platforms:** Instagram, LinkedIn, Facebook, X and YouTube Shorts, with posts per week for each.
4. **Services or products:** each one is featured across the month.
5. **Campaigns:** name, dates, focus service, key message and call to action.
6. **Assets and dates:** counts of photos, videos, product shots, team photos, testimonials, case studies, blog posts and customer posts, plus your key dates and optional national and international days.

Two sample briefs are included: a neighbourhood café and a B2B software company.

### How the plan is built
- **Pillar mix from the goal:** seven content pillars (Educate, Showcase, Proof, Behind the scenes, Conversation, Offer, Moments). Each goal has a target mix; for example *Generate leads* leans on Educate, Showcase and Proof.
- **Platform rhythm:** posts go on each platform's usually stronger days first, with a suggested time per format.
- **Campaigns first:** each campaign gets an announcement, a closing reminder and evenly spaced supporting posts inside its dates.
- **Key dates:** each one gets a post on the day, adding a slot if none exists.
- **Format balance:** every platform has a format mix (Reels, carousels, document carousels, polls, threads, Shorts…), weighted by how well a format suits the pillar.
- **Assets:** posts that need a photo or video draw from your counts. If you run short, the post is marked as an asset to source.
- **Ideas:** filled from your services, audience pains and interests, campaign messages and occasions, with rotation so the same angle isn't reused for the same service. Every post has an idea, a brief, *how to make it*, a call to action and its funnel stage.

### Checking and editing
- **Balance score (0–100)** with pillar mix against target, funnel split, formats per platform, services and campaigns featured, and days of the week.
- **Flags:** near-duplicate ideas within 14 days, three or more of the same pillar or format in a row on one platform, services never featured, campaigns with no posts, quiet stretches of five days or more, and missing assets. Select a flag to highlight its posts.
- **Edit everything:** drag a post to another day, open it to change the idea, brief, date, time, platform, format, pillar, service, call to action, asset or status. Get a **new idea**, **try another format**, duplicate, delete or add a post. The balance and flags are re-checked after every change.
- **Month and list views**, with filters by platform and pillar. **Fresh ideas** re-plans the month with a new seed.

### Export
- **CSV:** one row per post with date, day, time, platform, format, pillar, funnel stage, campaign, occasion, service, idea, brief, how to make it, call to action, asset, asset to source, status and flags.
- **Excel (.xlsx):** four sheets: *Calendar* (formatted table, colour-coded pillars), *Month view* (a printable grid), *Balance* and *Flags*.

---

## Project structure

```
plotline/
├── api/
│   ├── index.py               # Flask app (Vercel serverless function)
│   └── _core/
│       ├── rules.py           # Pillars, goal mixes, platforms, formats, assets, observances
│       ├── ideas.py           # Idea templates and how-to notes
│       ├── planner.py         # Brief validation, slot building, allocation, regenerate
│       ├── balance.py         # Balance score, mix analysis, repetition and gap flags
│       ├── export.py          # CSV and Excel export
│       └── samples.py         # Sample briefs
├── tests/test_plotline.py     # Pytest suite
├── src/                       # React app (components/, lib/, styles.css)
├── index.html, package.json, vite.config.js
├── requirements.txt
└── vercel.json
```

---

## Run locally

Requirements: **Python 3.9+** and **Node.js 18+**.

```bash
pip install -r requirements.txt
npm install

# terminal 1 — Flask API on http://127.0.0.1:5000
python api/index.py

# terminal 2 — frontend on http://localhost:5173
npm run dev
```

Vite proxies `/api/*` to Flask during development.

- **Tests:** `pip install pytest` then `python -m pytest tests -q`
- **Production build:** `npm run build`

---

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/config` | Goals, pillars, platforms, formats, asset types, sample briefs |
| POST | `/api/plan` | Build the month from `{ "brief": … }` |
| POST | `/api/analyze` | Re-check balance and flags for `{ "brief", "posts" }` after edits |
| POST | `/api/regenerate` | New idea for one post: `{ "brief", "posts", "post_id", "change_format" }` |
| POST | `/api/export` | Download `{ "brief", "posts", "format": "csv" | "xlsx" }` |

Example brief (shortened):

```json
{
  "business_name": "Brew & Bloom",
  "industry": "café and coffee",
  "month": "2026-11",
  "goal": { "type": "engagement", "statement": "Fill weekday afternoons" },
  "audience": { "description": "Young professionals in Ahmedabad", "pains": "crowded cafés", "interests": "specialty coffee" },
  "platforms": { "instagram": 4, "facebook": 2, "youtube_shorts": 1 },
  "services": [{ "name": "Weekend brunch", "description": "All-day brunch" }],
  "campaigns": [{ "name": "Winter menu launch", "start": "2026-11-10", "end": "2026-11-24", "service": "Weekend brunch", "message": "Four new winter drinks" }],
  "assets": { "photos": 20, "videos": 6 },
  "key_dates": [{ "date": "2026-11-21", "name": "Our third anniversary" }],
  "include_observances": true
}
```

Errors return HTTP 400 with `{"error": "...", "field": "..."}`.

---

## Deploy to Vercel

`vercel.json` builds the Vite frontend into `dist/` and routes `/api/*` to `api/index.py`, which Vercel runs as a Python function using `requirements.txt` (Flask and openpyxl).

1. Push this folder to its own GitHub repository.
2. On vercel.com: **Add New → Project**, import the repository, click **Deploy**.

Or with the CLI: `npm i -g vercel && vercel --prod`.

---

## Author

_Your name, course and university here._
