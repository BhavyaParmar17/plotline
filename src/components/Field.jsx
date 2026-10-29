import { forwardRef, useId } from "react";
import { motion } from "framer-motion";

export const Field = forwardRef(function Field({ label, hint, error, as = "input", optional, className = "", children, ...props }, ref) {
  const id = useId();
  const Tag = as;
  const d = hint || error ? `${id}-d` : undefined;
  return (
    <div className={`field ${error ? "has-error" : ""} ${className}`}>
      <label htmlFor={id}>
        <span>{label}</span>
        {optional && <span className="optional">optional</span>}
      </label>
      <Tag ref={ref} id={id} aria-invalid={Boolean(error)} aria-describedby={d} {...props}>
        {children}
      </Tag>
      {(error || hint) && (
        <p id={d} className={error ? "field-error" : "field-hint"}>
          {error || hint}
        </p>
      )}
    </div>
  );
});

export function Segmented({ options, value, onChange, name }) {
  return (
    <div className="segmented" role="radiogroup" aria-label={name}>
      {options.map((o) => {
        const active = o.value === value;
        return (
          <button key={o.value} type="button" role="radio" aria-checked={active} className={active ? "is-active" : ""} onClick={() => onChange(o.value)}>
            {active && <motion.span layoutId={`seg-${name}`} className="seg-pill" transition={{ type: "spring", stiffness: 500, damping: 40 }} />}
            <span className="seg-label">{o.label}</span>
          </button>
        );
      })}
    </div>
  );
}

export function Stepper({ value, onChange, min = 0, max = 7, label }) {
  return (
    <div className="stepper" role="group" aria-label={label}>
      <button type="button" onClick={() => onChange(Math.max(min, value - 1))} disabled={value <= min} aria-label={`Fewer ${label}`}>
        −
      </button>
      <output aria-live="polite">{value}</output>
      <button type="button" onClick={() => onChange(Math.min(max, value + 1))} disabled={value >= max} aria-label={`More ${label}`}>
        +
      </button>
    </div>
  );
}
