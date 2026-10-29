import { useState } from "react";
import { motion } from "framer-motion";
import { monthWeeks, parseISO, shortDate, WEEKDAYS } from "../lib/dates.js";

const SHORT = { instagram: "IG", linkedin: "in", facebook: "FB", x: "X", youtube_shorts: "YT" };

function PostTab({ post, color, flagged, focused, selected, onOpen, onDragStart }) {
  return (
    <motion.button
      layout
      layoutId={`post-${post.id}`}
      type="button"
      className={`post-tab${flagged ? " is-flagged" : ""}${focused ? " is-focus" : ""}${selected ? " is-selected" : ""}`}
      style={{ "--c": color }}
      draggable
      onDragStart={(e) => onDragStart(e, post.id)}
      onClick={() => onOpen(post.id)}
      transition={{ type: "spring", stiffness: 420, damping: 36 }}
      aria-label={`${post.platform_label} ${post.format_label}, ${post.theme_label}: ${post.title}${flagged ? ". Flagged" : ""}`}
    >
      <span className="pt-meta">
        <span className={`plat-badge plat-${post.platform}`}>{SHORT[post.platform]}</span>
        <span className="pt-fmt">{post.format_label}</span>
        {post.campaign && <span className="pt-camp" title={post.campaign}>Campaign</span>}
      </span>
      <span className="pt-title">{post.title}</span>
    </motion.button>
  );
}

export function MonthGrid({ brief, posts, themeColor, flagged, focusIds, selectedId, onOpen, onMove, onAdd }) {
  const weeks = monthWeeks(brief.month);
  const [over, setOver] = useState(null);
  const byDay = {};
  posts.forEach((p) => (byDay[p.date] = [...(byDay[p.date] || []), p]));
  const occasions = Object.fromEntries((brief.key_dates || []).map((k) => [k.date, k.name]));
  const campaignsOn = (iso) => (brief.campaigns || []).filter((c) => c.start <= iso && iso <= c.end);
  const today = new Date().toISOString().slice(0, 10);

  const dragStart = (e, id) => {
    e.dataTransfer.setData("text/plain", id);
    e.dataTransfer.effectAllowed = "move";
  };

  return (
    <div className="month" role="grid" aria-label="Month calendar">
      <div className="month-head" role="row">
        {WEEKDAYS.map((d) => (
          <span key={d} role="columnheader">{d}</span>
        ))}
      </div>
      {weeks.map((week, wi) => (
        <div className="month-week" role="row" key={wi}>
          {week.map((iso, di) =>
            iso ? (
              <div
                key={iso}
                role="gridcell"
                className={`day${over === iso ? " is-over" : ""}${iso === today ? " is-today" : ""}${di >= 5 ? " is-weekend" : ""}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  setOver(iso);
                }}
                onDragLeave={() => setOver((o) => (o === iso ? null : o))}
                onDrop={(e) => {
                  e.preventDefault();
                  setOver(null);
                  const id = e.dataTransfer.getData("text/plain");
                  if (id) onMove(id, iso);
                }}
              >
                <div className="day-head">
                  <span className="day-num">{parseISO(iso).getDate()}</span>
                  <button type="button" className="day-add" onClick={() => onAdd(iso)} aria-label={`Add a post on ${shortDate(iso)}`}>
                    +
                  </button>
                </div>
                {occasions[iso] && <span className="day-occasion">{occasions[iso]}</span>}
                {campaignsOn(iso).map((c) => (
                  <span key={c.name} className={`day-camp${c.start === iso ? " is-start" : ""}`} title={c.name}>
                    {c.start === iso ? c.name : ""}
                  </span>
                ))}
                <div className="day-posts">
                  {(byDay[iso] || []).map((p) => (
                    <PostTab
                      key={p.id}
                      post={p}
                      color={themeColor[p.theme]}
                      flagged={flagged.has(p.id)}
                      focused={focusIds.includes(p.id)}
                      selected={selectedId === p.id}
                      onOpen={onOpen}
                      onDragStart={dragStart}
                    />
                  ))}
                </div>
              </div>
            ) : (
              <div key={`e${wi}-${di}`} className="day day-empty" role="gridcell" aria-hidden="true" />
            )
          )}
        </div>
      ))}
    </div>
  );
}

export function ListView({ posts, themeColor, flagged, focusIds, onOpen }) {
  return (
    <div className="table-scroll">
      <table className="post-table">
        <thead>
          <tr>
            <th scope="col">Date</th>
            <th scope="col">Platform</th>
            <th scope="col">Format</th>
            <th scope="col">Pillar</th>
            <th scope="col">Idea</th>
            <th scope="col">Service</th>
            <th scope="col">Asset</th>
          </tr>
        </thead>
        <tbody>
          {posts.map((p) => (
            <tr
              key={p.id}
              className={`${flagged.has(p.id) ? "is-flagged" : ""} ${focusIds.includes(p.id) ? "is-focus" : ""}`}
              tabIndex={0}
              onClick={() => onOpen(p.id)}
              onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && (e.preventDefault(), onOpen(p.id))}
            >
              <th scope="row">
                {p.weekday} {shortDate(p.date)}
                <small>{p.time}</small>
              </th>
              <td><span className={`plat-badge plat-${p.platform}`}>{SHORT[p.platform]}</span> {p.platform_label}</td>
              <td>{p.format_label}</td>
              <td><span className="pill" style={{ "--c": themeColor[p.theme] }}>{p.theme_label}</span></td>
              <td className="idea-cell">
                {p.title}
                {p.campaign && <small>{p.campaign}</small>}
                {p.occasion && <small>{p.occasion}</small>}
              </td>
              <td>{p.service}</td>
              <td className={p.asset_gap ? "gap-cell" : ""}>{p.asset ? `${p.asset}${p.asset_gap ? " (to source)" : ""}` : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
