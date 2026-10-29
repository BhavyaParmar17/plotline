import { useEffect, useState } from "react";
import { getJson } from "../lib/api.js";

const RULES = [
  ["Pillars follow the goal", "Each goal has a target mix across seven content pillars. Campaign posts and key dates count towards it."],
  ["Each platform keeps its rhythm", "Posts go on each platform’s usually stronger days first, for example Tuesday to Thursday on LinkedIn. Times are starting points to check against your analytics."],
  ["Formats rotate", "Every platform has a format mix (Reels, carousels, documents, polls and so on). A format fits some pillars better, and anything needing a video uses your video count first."],
  ["Ideas come from your brief", "Post ideas are filled from your services, audience pains and interests, campaign messages and dates, and rotate so the same angle isn’t reused for the same service."],
  ["Repeats are caught, even after edits", "Near-identical ideas within 14 days, three of the same pillar or format in a row, unfeatured services, empty campaigns and quiet stretches of five days or more are all flagged."],
];

export default function Method() {
  const [cfg, setCfg] = useState(null);
  useEffect(() => {
    getJson("/api/config").then(setCfg).catch(() => {});
  }, []);
  return (
    <section className="method" id="method" aria-labelledby="method-h">
      <h2 id="method-h">The rules behind the plan</h2>
      <div className="method-grid">
        <dl className="rules">
          {RULES.map(([k, v]) => (
            <div key={k}>
              <dt>{k}</dt>
              <dd>{v}</dd>
            </div>
          ))}
        </dl>
        {cfg && (
          <div className="mix-table-wrap">
            <h3>Pillar mix by goal</h3>
            <div className="table-scroll">
              <table className="mix-table">
                <thead>
                  <tr>
                    <th scope="col">Goal</th>
                    {cfg.themes.map((t) => (
                      <th key={t.id} scope="col">
                        <span className="sw" style={{ background: t.color }} />
                        {t.label}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {cfg.goals.map((g) => (
                    <tr key={g.id}>
                      <th scope="row">{g.label}</th>
                      {cfg.themes.map((t) => (
                        <td key={t.id} style={{ "--a": g.mix[t.id] / 35, "--c": t.color }}>
                          {g.mix[t.id]}%
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
