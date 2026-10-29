import { motion } from "framer-motion";

const FUNNEL = ["Awareness", "Consideration", "Decision"];
const FUNNEL_COLOR = { Awareness: "#8FB3A0", Consideration: "#4E7B66", Decision: "#142019" };

export default function BalancePanel({ analysis, onFocusFlag, focusKey }) {
  const max = Math.max(...analysis.themes.map((t) => Math.max(t.pct, t.target_pct)), 10);
  const funnelTotal = FUNNEL.reduce((n, f) => n + (analysis.funnel[f] || 0), 0) || 1;
  const wdMax = Math.max(...Object.values(analysis.weekdays), 1);
  const sevOrder = { high: 0, medium: 1, low: 2 };
  const flags = [...analysis.flags].sort((a, b) => sevOrder[a.severity] - sevOrder[b.severity]);

  return (
    <aside className="balance" aria-label="Balance and checks">
      <div className={`score score-${analysis.score >= 85 ? "good" : analysis.score >= 70 ? "ok" : "low"}`}>
        <span className="score-n">{analysis.score}</span>
        <span className="score-l">
          <strong>{analysis.score_label}</strong>
          Balance score from pillar and format mix, repeats and gaps.
        </span>
      </div>

      <section>
        <h4>Pillar mix</h4>
        <p className="b-note">Bar is this month. The mark is what the goal calls for.</p>
        <ul className="bars">
          {analysis.themes.map((t) => (
            <li key={t.theme}>
              <span className="bar-label">{t.label}</span>
              <span className="bar-track">
                <motion.span className="bar-fill" style={{ background: t.color }} initial={false} animate={{ width: `${(t.pct / max) * 100}%` }} transition={{ type: "spring", stiffness: 160, damping: 24 }} />
                <span className="bar-target" style={{ left: `${(t.target_pct / max) * 100}%` }} title={`Target ${t.target_pct}%`} />
              </span>
              <span className="bar-n">{t.count}</span>
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h4>Funnel</h4>
        <div className="stack" role="img" aria-label={FUNNEL.map((f) => `${f} ${analysis.funnel[f] || 0}`).join(", ")}>
          {FUNNEL.map((f) => (
            <motion.span key={f} initial={false} animate={{ flexGrow: analysis.funnel[f] || 0.0001 }} style={{ background: FUNNEL_COLOR[f] }} />
          ))}
        </div>
        <ul className="legend">
          {FUNNEL.map((f) => (
            <li key={f}>
              <span className="sw" style={{ background: FUNNEL_COLOR[f] }} />
              {f} {Math.round(((analysis.funnel[f] || 0) / funnelTotal) * 100)}%
            </li>
          ))}
        </ul>
      </section>

      <section>
        <h4>Formats</h4>
        {analysis.formats.map((pl) => (
          <div key={pl.platform} className="fmt-block">
            <span className="fmt-plat">
              <span className={`plat-badge plat-${pl.platform}`}>{pl.label.slice(0, 2)}</span> {pl.label}, {pl.total} posts
            </span>
            <ul className="fmt-chips">
              {pl.formats.map((f) => (
                <li key={f.format} className={f.count === 0 ? "is-zero" : ""} title={`Target ${f.target_pct}%`}>
                  {f.label} <strong>{f.count}</strong>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </section>

      <section>
        <h4>Services featured</h4>
        <ul className="svc">
          {analysis.services.map((s) => (
            <li key={s.name} className={s.count ? "" : "is-zero"}>
              <span>{s.name}</span>
              <strong>{s.count}</strong>
            </li>
          ))}
        </ul>
        {analysis.campaigns.length > 0 && (
          <ul className="svc camp">
            {analysis.campaigns.map((c) => (
              <li key={c.name} className={c.count ? "" : "is-zero"}>
                <span>{c.name}</span>
                <strong>{c.count}</strong>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section>
        <h4>Days of the week</h4>
        <div className="wd">
          {Object.entries(analysis.weekdays).map(([d, n]) => (
            <div key={d}>
              <motion.span initial={false} animate={{ height: `${(n / wdMax) * 100}%` }} />
              <small>{d.slice(0, 2)}</small>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h4>Flags</h4>
        {flags.length === 0 ? (
          <p className="b-note">Nothing repeats and every service and campaign is covered.</p>
        ) : (
          <ul className="flag-list">
            {flags.map((f, i) => {
              const key = `${f.type}-${i}-${f.posts.join(",")}`;
              return (
                <li key={key}>
                  <button
                    type="button"
                    className={`flag sev-${f.severity}${focusKey === f.posts.join(",") && f.posts.length ? " is-on" : ""}`}
                    onClick={() => onFocusFlag(f.posts)}
                    disabled={!f.posts.length}
                  >
                    <span className="flag-msg">{f.message}</span>
                    <span className="flag-fix">{f.suggestion}</span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>
    </aside>
  );
}
