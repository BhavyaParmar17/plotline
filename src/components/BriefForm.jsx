import { Field, Segmented, Stepper } from "./Field.jsx";

const GOAL_HINT = {
  awareness: "More people should know you exist.",
  leads: "More enquiries, calls or sign-ups.",
  sales: "More bookings or purchases this month.",
  engagement: "More comments, shares and saves.",
  launch: "A new product, service or location.",
  retention: "Existing customers come back more often.",
};

function Section({ n, title, note, children }) {
  return (
    <fieldset className="bf-section">
      <legend>
        <span className="bf-n">{n}</span>
        <span className="bf-title">{title}</span>
      </legend>
      {note && <p className="bf-note">{note}</p>}
      <div className="bf-body">{children}</div>
    </fieldset>
  );
}

export default function BriefForm({ brief, setBrief, config, error }) {
  const set = (path, value) =>
    setBrief((b) => {
      const next = structuredClone(b);
      const keys = path.split(".");
      let o = next;
      keys.slice(0, -1).forEach((k) => (o = o[k]));
      o[keys[keys.length - 1]] = value;
      return next;
    });
  const err = (field) => (error?.field === field ? error.message : undefined);
  const list = (key) => brief[key] || [];
  const updateItem = (key, i, patch) => setBrief((b) => ({ ...b, [key]: b[key].map((x, j) => (j === i ? { ...x, ...patch } : x)) }));
  const removeItem = (key, i) => setBrief((b) => ({ ...b, [key]: b[key].filter((_, j) => j !== i) }));
  const addItem = (key, item) => setBrief((b) => ({ ...b, [key]: [...(b[key] || []), item] }));
  const weekly = Object.values(brief.platforms).reduce((a, b) => a + Number(b || 0), 0);
  const [y, m] = brief.month.split("-").map(Number);
  const monthStart = `${brief.month}-01`;
  const monthEnd = `${brief.month}-${String(new Date(y, m, 0).getDate()).padStart(2, "0")}`;

  return (
    <div className="brief-form">
      <Section n="1" title="Business and goal">
        <div className="two">
          <Field label="Business name" value={brief.business_name} onChange={(e) => set("business_name", e.target.value)} placeholder="Brew & Bloom" />
          <Field label="Industry" value={brief.industry} onChange={(e) => set("industry", e.target.value)} placeholder="café and coffee" />
        </div>
        <div className="two">
          <Field label="Month to plan" type="month" value={brief.month} onChange={(e) => set("month", e.target.value)} error={err("month")} />
          <div className="field">
            <span className="label-like">Goal for the month</span>
            <select className="select" value={brief.goal.type} onChange={(e) => set("goal.type", e.target.value)} aria-label="Goal for the month">
              {config.goals.map((g) => (
                <option key={g.id} value={g.id}>{g.label}</option>
              ))}
            </select>
            <p className="field-hint">{GOAL_HINT[brief.goal.type]}</p>
          </div>
        </div>
        <Field
          label="In your own words"
          optional
          value={brief.goal.statement}
          onChange={(e) => set("goal.statement", e.target.value)}
          placeholder="Book 25 discovery calls before the new quarter"
        />
      </Section>

      <Section n="2" title="Audience" note="Pains and interests are woven into post ideas, so specific beats general.">
        <Field label="Who you’re talking to" value={brief.audience.description} onChange={(e) => set("audience.description", e.target.value)} placeholder="Young professionals in Ahmedabad, 20 to 35" />
        <div className="two">
          <Field as="textarea" rows={3} label="Their pains" optional value={brief.audience.pains} onChange={(e) => set("audience.pains", e.target.value)} placeholder="crowded cafés, overpriced coffee" hint="Comma separated." />
          <Field as="textarea" rows={3} label="Their interests" optional value={brief.audience.interests} onChange={(e) => set("audience.interests", e.target.value)} placeholder="specialty coffee, weekend brunch" hint="Comma separated." />
        </div>
      </Section>

      <Section n="3" title="Platforms" note={`${weekly} post${weekly === 1 ? "" : "s"} a week in total.`}>
        <ul className="platform-list">
          {config.platforms.map((p) => {
            const n = Number(brief.platforms[p.id] || 0);
            return (
              <li key={p.id} className={n ? "is-on" : ""}>
                <span className={`plat-badge plat-${p.id}`}>{p.short}</span>
                <span className="plat-name">{p.label}</span>
                <Stepper value={n} onChange={(v) => set(`platforms.${p.id}`, v)} label={`${p.label} posts a week`} />
                <span className="plat-unit">a week</span>
              </li>
            );
          })}
        </ul>
        {err("platforms") && <p className="field-error">{err("platforms")}</p>}
      </Section>

      <Section n="4" title="Services or products" note="Each one gets featured across the month.">
        <ul className="rows">
          {list("services").map((s, i) => (
            <li key={i} className="row row-service">
              <Field label={`Service ${i + 1}`} value={s.name} onChange={(e) => updateItem("services", i, { name: e.target.value })} placeholder="Weekend brunch" />
              <Field label="Short description" optional value={s.description} onChange={(e) => updateItem("services", i, { description: e.target.value })} placeholder="All-day menu on weekends" />
              <button type="button" className="row-remove" onClick={() => removeItem("services", i)} aria-label={`Remove service ${i + 1}`} disabled={list("services").length <= 1}>
                Remove
              </button>
            </li>
          ))}
        </ul>
        {err("services") && <p className="field-error">{err("services")}</p>}
        <button type="button" className="add-row" onClick={() => addItem("services", { name: "", description: "" })} disabled={list("services").length >= 12}>
          Add a service
        </button>
      </Section>

      <Section n="5" title="Campaigns" note="Plotline places an announcement, a closing reminder and supporting posts inside each campaign’s dates.">
        <ul className="rows">
          {list("campaigns").map((c, i) => (
            <li key={i} className="row row-campaign">
              <Field label="Campaign name" value={c.name} onChange={(e) => updateItem("campaigns", i, { name: e.target.value })} placeholder="Winter menu launch" />
              <Field label="Starts" type="date" min={monthStart} max={monthEnd} value={c.start} onChange={(e) => updateItem("campaigns", i, { start: e.target.value })} />
              <Field label="Ends" type="date" min={monthStart} max={monthEnd} value={c.end} onChange={(e) => updateItem("campaigns", i, { end: e.target.value })} />
              <div className="field">
                <span className="label-like">Service</span>
                <select className="select" value={c.service} onChange={(e) => updateItem("campaigns", i, { service: e.target.value })} aria-label="Campaign service">
                  <option value="">Any</option>
                  {list("services").filter((s) => s.name).map((s) => (
                    <option key={s.name} value={s.name}>{s.name}</option>
                  ))}
                </select>
              </div>
              <Field className="span-all" label="Key message" value={c.message} onChange={(e) => updateItem("campaigns", i, { message: e.target.value })} placeholder="Four new winter drinks made with local jaggery" />
              <Field label="Call to action" optional value={c.cta} onChange={(e) => updateItem("campaigns", i, { cta: e.target.value })} placeholder="Try the winter menu" />
              <button type="button" className="row-remove" onClick={() => removeItem("campaigns", i)}>Remove</button>
            </li>
          ))}
        </ul>
        {err("campaigns") && <p className="field-error">{err("campaigns")}</p>}
        <button type="button" className="add-row" onClick={() => addItem("campaigns", { name: "", start: monthStart, end: monthEnd, service: "", message: "", cta: "" })}>
          Add a campaign
        </button>
      </Section>

      <Section n="6" title="Assets and dates" note="Posts that need a photo or video draw from these counts. Anything short is flagged as an asset to source.">
        <div className="asset-grid">
          {config.assets.map((a) => (
            <div key={a.id} className="asset-row">
              <span>{a.label}</span>
              <Stepper value={Number(brief.assets[a.id] || 0)} onChange={(v) => set(`assets.${a.id}`, v)} max={99} label={a.label} />
            </div>
          ))}
        </div>
        <h4 className="bf-sub">Key dates</h4>
        <ul className="rows">
          {list("key_dates").map((k, i) => (
            <li key={i} className="row row-date">
              <Field label="Date" type="date" min={monthStart} max={monthEnd} value={k.date} onChange={(e) => updateItem("key_dates", i, { date: e.target.value })} />
              <Field label="What’s happening" value={k.name} onChange={(e) => updateItem("key_dates", i, { name: e.target.value })} placeholder="Store anniversary" />
              <button type="button" className="row-remove" onClick={() => removeItem("key_dates", i)}>Remove</button>
            </li>
          ))}
        </ul>
        <button type="button" className="add-row" onClick={() => addItem("key_dates", { date: monthStart, name: "" })}>Add a key date</button>
        <label className="check">
          <input type="checkbox" checked={brief.include_observances} onChange={(e) => set("include_observances", e.target.checked)} />
          <span>Include national and international days that fall this month (up to three)</span>
        </label>
      </Section>
    </div>
  );
}
