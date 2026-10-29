import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion, useMotionValueEvent, useScroll, useSpring } from "framer-motion";
import { getJson, postJson } from "../lib/api.js";
import { monthLabel, monthWeeks, parseISO } from "../lib/dates.js";

const STEPS = [
  { at: 0, title: "The goal sets the mix", text: "Engagement leans on conversation and behind-the-scenes posts. A sales goal would lean on offers and proof." },
  { at: 0.18, title: "Posts land on each platform’s strongest days", text: "Instagram, Facebook and Shorts each get their own rhythm. Campaign posts and key dates are placed first." },
  { at: 0.55, title: "Pillars and formats are balanced as it goes", text: "No pillar twice in a row on one platform, formats rotate, and services take turns." },
  { at: 0.8, title: "Repeats and gaps are flagged", text: "Near-duplicate ideas, streaks and missing assets are marked for you to fix before anything is scheduled." },
];

export default function Story() {
  const ref = useRef(null);
  const [data, setData] = useState(null);
  const [progress, setProgress] = useState(0);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end end"] });
  const smooth = useSpring(scrollYProgress, { stiffness: 120, damping: 28, mass: 0.4 });
  useMotionValueEvent(smooth, "change", setProgress);

  useEffect(() => {
    getJson("/api/config")
      .then((cfg) => postJson("/api/plan", { brief: cfg.samples[0].brief }).then((plan) => setData({ cfg, plan })))
      .catch(() => {});
  }, []);

  const step = STEPS.reduce((acc, s, i) => (progress >= s.at ? i : acc), 0);
  if (!data) {
    return <section className="story" id="story" ref={ref} aria-label="How Plotline plans a month" />;
  }
  const { cfg, plan } = data;
  const posts = plan.posts;
  const fill = Math.max(0, Math.min(1, (progress - 0.18) / 0.55));
  const shown = Math.round(fill * posts.length);
  const placed = posts.slice(0, shown);
  const flaggedOn = progress >= 0.8;
  const flagged = new Set(plan.analysis.flagged_posts);
  const color = Object.fromEntries(cfg.themes.map((t) => [t.id, t.color]));
  const byDay = {};
  placed.forEach((p) => (byDay[p.date] = [...(byDay[p.date] || []), p]));
  const goal = cfg.goals.find((g) => g.id === plan.brief.goal.type);
  const counts = Object.fromEntries(cfg.themes.map((t) => [t.id, placed.filter((p) => p.theme === t.id).length]));
  const targets = Object.fromEntries(cfg.themes.map((t) => [t.id, Math.round((goal.mix[t.id] / 100) * posts.length)]));
  const maxBar = Math.max(...Object.values(targets), ...Object.values(counts), 1);

  return (
    <section className="story" id="story" ref={ref} aria-labelledby="story-h">
      <div className="story-sticky">
        <div className="story-copy">
          <p className="story-k">How it plans: {plan.brief.business}, {monthLabel(plan.brief.month)}</p>
          <h2 id="story-h">One goal in. A month out.</h2>
          <ol className="story-steps">
            {STEPS.map((s, i) => (
              <li key={s.title} className={i === step ? "is-on" : i < step ? "is-done" : ""}>
                <span className="story-n">{i + 1}</span>
                <div>
                  <strong>{s.title}</strong>
                  <AnimatePresence initial={false}>
                    {i === step && (
                      <motion.p initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}>
                        {s.text}
                      </motion.p>
                    )}
                  </AnimatePresence>
                </div>
              </li>
            ))}
          </ol>
          <p className="story-count">
            {shown} of {posts.length} posts placed{flaggedOn ? `, ${plan.analysis.flags.length} flags raised` : ""}
          </p>
        </div>
        <div className="story-visual">
          <div className="mini-month" aria-hidden="true">
            {["M", "T", "W", "T", "F", "S", "S"].map((d, i) => (
              <span key={i} className="mm-head">{d}</span>
            ))}
            {monthWeeks(plan.brief.month).flat().map((iso, i) => (
              <div key={i} className={`mm-day${iso ? "" : " is-empty"}`}>
                {iso && <span className="mm-num">{parseISO(iso).getDate()}</span>}
                <div className="mm-dots">
                  {(byDay[iso] || []).map((p) => (
                    <motion.span
                      key={p.id}
                      className={`mm-dot${flaggedOn && flagged.has(p.id) ? " is-flag" : ""}`}
                      style={{ background: color[p.theme] }}
                      initial={{ scale: 0, y: -10 }}
                      animate={{ scale: 1, y: 0 }}
                      transition={{ type: "spring", stiffness: 400, damping: 18 }}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
          <ul className="mini-bars">
            {cfg.themes.map((t) => (
              <li key={t.id}>
                <span className="mb-label">{t.label}</span>
                <span className="mb-track">
                  <span className="mb-target" style={{ width: `${(targets[t.id] / maxBar) * 100}%` }} />
                  <motion.span className="mb-fill" style={{ background: t.color }} initial={false} animate={{ width: `${(counts[t.id] / maxBar) * 100}%` }} />
                </span>
                <span className="mb-n">{counts[t.id]}/{targets[t.id]}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </section>
  );
}
