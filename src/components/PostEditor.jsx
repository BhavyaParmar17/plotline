import { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Field } from "./Field.jsx";

const STATUSES = ["Draft", "Ready", "Scheduled", "Posted"];

export default function PostEditor({ post, brief, config, flags, busy, onChange, onClose, onRegenerate, onDelete, onDuplicate }) {
  const ref = useRef(null);
  useEffect(() => {
    ref.current?.focus();
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [post.id, onClose]);

  const platformCfg = config.platforms.find((p) => p.id === post.platform);
  const enabled = config.platforms.filter((p) => brief.platforms[p.id]);
  const theme = config.themes.find((t) => t.id === post.theme);
  const set = (patch) => onChange(post.id, patch);

  return (
    <motion.aside
      className="editor"
      role="dialog"
      aria-modal="false"
      aria-labelledby="editor-h"
      initial={{ x: 40, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      transition={{ type: "spring", stiffness: 380, damping: 34 }}
      style={{ "--c": theme?.color }}
    >
      <div className="editor-head">
        <div>
          <p className="editor-kicker">{post.id}{post.campaign ? `, ${post.campaign}` : ""}{post.occasion ? `, ${post.occasion}` : ""}</p>
          <h3 id="editor-h" tabIndex={-1} ref={ref}>{post.title}</h3>
        </div>
        <button type="button" className="close" onClick={onClose} aria-label="Close editor">×</button>
      </div>

      {flags.length > 0 && (
        <ul className="editor-flags">
          {flags.map((f, i) => (
            <li key={i} className={`sev-${f.severity}`}>
              {f.message}
              <span>{f.suggestion}</span>
            </li>
          ))}
        </ul>
      )}

      <div className="editor-actions">
        <button type="button" className="btn btn-small" onClick={() => onRegenerate(post.id, false)} disabled={busy}>
          {busy ? "Thinking…" : "New idea"}
        </button>
        <button type="button" className="btn btn-small" onClick={() => onRegenerate(post.id, true)} disabled={busy}>
          Try another format
        </button>
        <button type="button" className="btn btn-small" onClick={() => onDuplicate(post.id)}>Duplicate</button>
        <button type="button" className="btn btn-small btn-danger" onClick={() => onDelete(post.id)}>Delete</button>
      </div>

      <div className="editor-body">
        <Field label="Idea" value={post.title} onChange={(e) => set({ title: e.target.value, template: `custom-${post.id}` })} />
        <Field as="textarea" rows={4} label="Brief" value={post.brief} onChange={(e) => set({ brief: e.target.value, template: `custom-${post.id}` })} />
        <div className="two">
          <Field label="Date" type="date" min={brief.first_day} max={brief.last_day} value={post.date} onChange={(e) => e.target.value && set({ date: e.target.value })} />
          <Field label="Time" type="time" value={post.time} onChange={(e) => set({ time: e.target.value })} />
        </div>
        <div className="two">
          <Field as="select" label="Platform" value={post.platform} onChange={(e) => set({ platform: e.target.value })}>
            {enabled.map((p) => (
              <option key={p.id} value={p.id}>{p.label}</option>
            ))}
          </Field>
          <Field as="select" label="Format" value={post.format} onChange={(e) => set({ format: e.target.value })}>
            {(platformCfg?.formats || []).map((f) => (
              <option key={f} value={f}>{config.formats[f].label}</option>
            ))}
          </Field>
        </div>
        <div className="two">
          <Field as="select" label="Pillar" value={post.theme} onChange={(e) => set({ theme: e.target.value })}>
            {config.themes.map((t) => (
              <option key={t.id} value={t.id}>{t.label}</option>
            ))}
          </Field>
          <Field as="select" label="Service" value={post.service} onChange={(e) => set({ service: e.target.value })}>
            {brief.services.map((s) => (
              <option key={s.name} value={s.name}>{s.name}</option>
            ))}
          </Field>
        </div>
        <Field label="Call to action" value={post.cta} onChange={(e) => set({ cta: e.target.value })} />
        <div className="two">
          <Field label="Asset" value={post.asset || ""} onChange={(e) => set({ asset: e.target.value })} placeholder="None needed" hint={post.asset_gap ? "Not in your asset list yet." : undefined} />
          <Field as="select" label="Status" value={post.status} onChange={(e) => set({ status: e.target.value })}>
            {STATUSES.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </Field>
        </div>
        <div className="how">
          <strong>How to make it</strong>
          <p>{post.how_to}</p>
          <p className="how-theme">
            <span className="pill" style={{ "--c": theme?.color }}>{theme?.label}</span> {theme?.about} Funnel stage: {post.funnel}.
          </p>
        </div>
      </div>
    </motion.aside>
  );
}
