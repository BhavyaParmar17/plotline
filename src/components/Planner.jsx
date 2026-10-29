import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { download, getJson, postJson } from "../lib/api.js";
import { monthLabel, nextMonth, weekdayOf } from "../lib/dates.js";
import BriefForm from "./BriefForm.jsx";
import { ListView, MonthGrid } from "./Calendar.jsx";
import PostEditor from "./PostEditor.jsx";
import BalancePanel from "./BalancePanel.jsx";
import { Segmented } from "./Field.jsx";

const ASSET_ZERO = { photos: 0, videos: 0, product_shots: 0, team_photos: 0, testimonials: 0, case_studies: 0, blog_posts: 0, ugc: 0 };
const blankBrief = () => ({
  business_name: "",
  industry: "",
  month: nextMonth(),
  goal: { type: "awareness", statement: "" },
  audience: { description: "", pains: "", interests: "" },
  platforms: { instagram: 3, linkedin: 2, facebook: 0, x: 0, youtube_shorts: 0 },
  services: [{ name: "", description: "" }],
  campaigns: [],
  assets: { ...ASSET_ZERO, photos: 8, videos: 3 },
  key_dates: [],
  include_observances: true,
  seed: 0,
});

export default function Planner({ request, onRequestHandled }) {
  const [config, setConfig] = useState(null);
  const [brief, setBrief] = useState(blankBrief);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState(null);
  const [plan, setPlan] = useState(null);
  const [posts, setPosts] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [view, setView] = useState("month");
  const [platformFilter, setPlatformFilter] = useState([]);
  const [themeFilter, setThemeFilter] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [focusIds, setFocusIds] = useState([]);
  const [busy, setBusy] = useState(false);
  const [exportMsg, setExportMsg] = useState("");
  const [dirty, setDirty] = useState(false);
  const lastBrief = useRef(null);
  const counter = useRef(1);

  useEffect(() => {
    getJson("/api/config").then(setConfig).catch(setError);
  }, []);

  const loadSample = useCallback(
    (id) => {
      const s = config?.samples.find((x) => x.id === id);
      if (!s) return;
      const b = structuredClone(s.brief);
      setBrief({
        ...blankBrief(),
        ...b,
        audience: { description: b.audience.description, pains: b.audience.pains, interests: b.audience.interests },
        platforms: { instagram: 0, linkedin: 0, facebook: 0, x: 0, youtube_shorts: 0, ...b.platforms },
        assets: { ...ASSET_ZERO, ...b.assets },
        campaigns: b.campaigns.map((c) => ({ cta: "", ...c })),
        seed: 0,
      });
    },
    [config]
  );

  useEffect(() => {
    if (!request || !config) return;
    if (request === "sample") loadSample("cafe");
    document.getElementById("planner")?.scrollIntoView({ behavior: "smooth", block: "start" });
    onRequestHandled();
  }, [request, config, loadSample, onRequestHandled]);

  const run = async (seedBump = 0) => {
    const payload = { ...brief, seed: (brief.seed || 0) + seedBump };
    if (seedBump) setBrief(payload);
    setStatus("loading");
    setError(null);
    try {
      const data = await postJson("/api/plan", { brief: payload });
      lastBrief.current = payload;
      setPlan(data);
      setPosts(data.posts);
      setAnalysis(data.analysis);
      setSelectedId(null);
      setFocusIds([]);
      setDirty(false);
      setStatus("done");
      if (!seedBump) setTimeout(() => document.getElementById("calendar")?.scrollIntoView({ behavior: "smooth", block: "start" }), 120);
    } catch (err) {
      setError(err);
      setStatus("error");
    }
  };

  // re-check balance after edits
  useEffect(() => {
    if (!dirty || !lastBrief.current) return undefined;
    const t = setTimeout(() => {
      postJson("/api/analyze", { brief: lastBrief.current, posts })
        .then((d) => setAnalysis(d.analysis))
        .catch(() => {});
    }, 300);
    return () => clearTimeout(t);
  }, [posts, dirty]);

  const derive = useCallback(
    (post, patch) => {
      const next = { ...post, ...patch };
      if (patch.platform) {
        const pl = config.platforms.find((p) => p.id === patch.platform);
        next.platform_label = pl.label;
        if (!pl.formats.includes(next.format)) next.format = pl.formats[0];
      }
      if (patch.platform || patch.format) {
        const f = config.formats[next.format];
        next.format_label = f.label;
        next.how_to = f.how_to;
        if (patch.format) next.asset_gap = false;
      }
      if (patch.theme) {
        const t = config.themes.find((x) => x.id === patch.theme);
        next.theme_label = t.label;
        next.funnel = t.funnel;
      }
      if (patch.date) next.weekday = weekdayOf(patch.date);
      if ("asset" in patch) next.asset_gap = false;
      return next;
    },
    [config]
  );

  const updatePost = useCallback(
    (id, patch) => {
      setPosts((ps) => ps.map((p) => (p.id === id ? derive(p, patch) : p)).sort((a, b) => a.date.localeCompare(b.date)));
      setDirty(true);
    },
    [derive]
  );

  const addPost = (date) => {
    const platform = config.platforms.find((p) => plan.brief.platforms[p.id]);
    const id = `N${String(counter.current++).padStart(3, "0")}`;
    const fmt = platform.formats[0];
    const post = derive(
      {
        id,
        date,
        weekday: weekdayOf(date),
        time: config.formats[fmt].time,
        platform: platform.id,
        platform_label: platform.label,
        format: fmt,
        theme: "educate",
        service: plan.brief.services[0].name,
        campaign: "",
        occasion: "",
        title: "New post",
        brief: "Describe the idea.",
        cta: "",
        asset: "",
        asset_gap: false,
        template: `custom-${id}`,
        status: "Draft",
      },
      { platform: platform.id, theme: "educate" }
    );
    setPosts((ps) => [...ps, post].sort((a, b) => a.date.localeCompare(b.date)));
    setSelectedId(id);
    setDirty(true);
  };

  const deletePost = (id) => {
    setPosts((ps) => ps.filter((p) => p.id !== id));
    setSelectedId(null);
    setDirty(true);
  };

  const duplicatePost = (id) => {
    const src = posts.find((p) => p.id === id);
    const newId = `N${String(counter.current++).padStart(3, "0")}`;
    setPosts((ps) => [...ps, { ...src, id: newId, template: `custom-${newId}`, title: `${src.title} (copy)` }].sort((a, b) => a.date.localeCompare(b.date)));
    setSelectedId(newId);
    setDirty(true);
  };

  const regenerate = async (id, changeFormat) => {
    setBusy(true);
    try {
      const d = await postJson("/api/regenerate", { brief: lastBrief.current, posts, post_id: id, change_format: changeFormat });
      setPosts((ps) => ps.map((p) => (p.id === id ? d.post : p)));
      setAnalysis(d.analysis);
    } catch (err) {
      setExportMsg(err.message);
    } finally {
      setBusy(false);
    }
  };

  const doExport = async (format) => {
    setExportMsg("");
    try {
      const name = await download("/api/export", { brief: lastBrief.current, posts, format });
      setExportMsg(`Saved ${name}`);
    } catch (err) {
      setExportMsg(err.message);
    }
  };

  const themeColor = useMemo(() => Object.fromEntries((config?.themes || []).map((t) => [t.id, t.color])), [config]);
  const flagged = useMemo(() => new Set(analysis?.flagged_posts || []), [analysis]);
  const visible = posts.filter(
    (p) => (!platformFilter.length || platformFilter.includes(p.platform)) && (!themeFilter.length || themeFilter.includes(p.theme))
  );
  const selected = posts.find((p) => p.id === selectedId);
  const selectedFlags = selected && analysis ? analysis.flags.filter((f) => f.posts.includes(selected.id)) : [];
  const toggle = (setter, value) => setter((arr) => (arr.includes(value) ? arr.filter((x) => x !== value) : [...arr, value]));

  const focusFlag = (ids) => {
    setFocusIds(ids);
    if (ids.length) {
      const first = posts.find((p) => p.id === ids[0]);
      if (first) {
        setPlatformFilter([]);
        setThemeFilter([]);
        setTimeout(() => document.querySelector(".is-focus")?.scrollIntoView({ behavior: "smooth", block: "center" }), 80);
      }
    }
  };

  if (!config) {
    return (
      <section className="planner" id="planner">
        <p className="loading-note">{error ? error.message : "Loading the planner…"}</p>
      </section>
    );
  }

  const goal = config.goals.find((g) => g.id === brief.goal.type);
  const weekly = Object.values(brief.platforms).reduce((a, b) => a + Number(b || 0), 0);
  const changed = plan && lastBrief.current && JSON.stringify({ ...lastBrief.current, seed: 0 }) !== JSON.stringify({ ...brief, seed: 0 });

  return (
    <section className="planner" id="planner" aria-labelledby="planner-h">
      <div className="planner-head">
        <h2 id="planner-h">The brief</h2>
        <div className="sample-row" role="group" aria-label="Load a sample brief">
          <span>Load a sample:</span>
          {config.samples.map((s) => (
            <button key={s.id} type="button" className="chip" onClick={() => loadSample(s.id)}>
              {s.label}
            </button>
          ))}
          <button type="button" className="chip chip-ghost" onClick={() => setBrief(blankBrief())}>Clear</button>
        </div>
      </div>

      <div className="brief-layout">
        <BriefForm brief={brief} setBrief={setBrief} config={config} error={error} />
        <aside className="brief-summary" aria-label="Plan preview">
          <p className="sum-k">Planning</p>
          <p className="sum-month">{monthLabel(brief.month)}</p>
          <p className="sum-line">
            About <strong>{Math.round((weekly * 30.4) / 7)}</strong> posts across{" "}
            <strong>{Object.values(brief.platforms).filter(Number).length}</strong> platforms, built to {goal.label.toLowerCase()}.
          </p>
          <p className="sum-k">Pillar mix for this goal</p>
          <ul className="mix">
            {config.themes.map((t) => (
              <li key={t.id}>
                <motion.span
                  className="mix-bar"
                  initial={false}
                  animate={{ width: `${goal.mix[t.id] * 2.4}%` }}
                  transition={{ type: "spring", stiffness: 200, damping: 26 }}
                  style={{ background: t.color }}
                />
                <span className="mix-label">{t.label}</span>
                <span className="mix-n">{goal.mix[t.id]}%</span>
              </li>
            ))}
          </ul>
          <button type="button" className="btn btn-primary btn-big" onClick={() => run(0)} disabled={status === "loading"}>
            {status === "loading" ? "Planning…" : plan ? "Rebuild the calendar" : "Build my calendar"}
          </button>
          {error && <p className="banner" role="alert">{error.message}</p>}
          {changed && !error && <p className="run-note">The brief has changed since this calendar was built.</p>}
        </aside>
      </div>

      {plan && analysis && (
        <motion.div
          className="results"
          id="calendar"
          key={`${plan.brief.month}-${plan.brief.seed}`}
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        >
          <div className="results-head">
            <div>
              <p className="sum-k">{plan.brief.business}</p>
              <h2>{monthLabel(plan.brief.month)}</h2>
              <p className="results-sub">
                {posts.length} posts, {plan.brief.goal.label.toLowerCase()}
                {plan.brief.goal.statement ? `: ${plan.brief.goal.statement}` : "."}
              </p>
            </div>
            <div className="results-actions">
              <button type="button" className="btn btn-quiet" onClick={() => run(1)} disabled={status === "loading"}>
                Fresh ideas
              </button>
              <button type="button" className="btn btn-quiet" onClick={() => doExport("csv")}>Export CSV</button>
              <button type="button" className="btn btn-primary" onClick={() => doExport("xlsx")}>Export Excel</button>
              {exportMsg && <p className="export-msg" role="status">{exportMsg}</p>}
            </div>
          </div>

          <div className="toolbar">
            <Segmented
              name="view"
              value={view}
              onChange={setView}
              options={[
                { value: "month", label: "Month" },
                { value: "list", label: "List" },
              ]}
            />
            <div className="filters" role="group" aria-label="Filter by platform">
              {config.platforms
                .filter((p) => plan.brief.platforms[p.id])
                .map((p) => (
                  <button key={p.id} type="button" className={`filter${platformFilter.includes(p.id) ? " is-on" : ""}`} aria-pressed={platformFilter.includes(p.id)} onClick={() => toggle(setPlatformFilter, p.id)}>
                    <span className={`plat-badge plat-${p.id}`}>{p.short}</span> {p.label}
                  </button>
                ))}
            </div>
            <div className="filters" role="group" aria-label="Filter by pillar">
              {config.themes.map((t) => (
                <button key={t.id} type="button" className={`filter${themeFilter.includes(t.id) ? " is-on" : ""}`} aria-pressed={themeFilter.includes(t.id)} onClick={() => toggle(setThemeFilter, t.id)} style={{ "--c": t.color }}>
                  <span className="sw" /> {t.label}
                </button>
              ))}
            </div>
          </div>
          <p className="drag-hint">Drag a post to another day to move it. Select a post to edit it, get a new idea or change its format.</p>

          <div className="cal-layout">
            <div className="cal-main">
              {view === "month" ? (
                <MonthGrid
                  brief={plan.brief}
                  posts={visible}
                  themeColor={themeColor}
                  flagged={flagged}
                  focusIds={focusIds}
                  selectedId={selectedId}
                  onOpen={setSelectedId}
                  onMove={(id, date) => updatePost(id, { date })}
                  onAdd={addPost}
                />
              ) : (
                <ListView posts={visible} themeColor={themeColor} flagged={flagged} focusIds={focusIds} onOpen={setSelectedId} />
              )}
            </div>
            <BalancePanel analysis={analysis} onFocusFlag={focusFlag} focusKey={focusIds.join(",")} />
          </div>

          <AnimatePresence>
            {selected && (
              <PostEditor
                key={selected.id}
                post={selected}
                brief={plan.brief}
                config={config}
                flags={selectedFlags}
                busy={busy}
                onChange={updatePost}
                onClose={() => setSelectedId(null)}
                onRegenerate={regenerate}
                onDelete={deletePost}
                onDuplicate={duplicatePost}
              />
            )}
          </AnimatePresence>
        </motion.div>
      )}
    </section>
  );
}
