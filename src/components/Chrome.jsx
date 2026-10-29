import { motion, useScroll, useSpring } from "framer-motion";

export function Logo({ size = 28 }) {
  return (
    <svg viewBox="0 0 32 32" width={size} height={size} aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="var(--ink)" />
      <rect x="6" y="7" width="6" height="6" rx="1.5" fill="#2F6FB0" />
      <rect x="13" y="7" width="6" height="6" rx="1.5" fill="var(--sun)" />
      <rect x="20" y="7" width="6" height="6" rx="1.5" fill="#1F8A5B" />
      <rect x="6" y="14" width="6" height="6" rx="1.5" fill="#B83B5E" />
      <rect x="13" y="14" width="6" height="6" rx="1.5" fill="#4A5A50" />
      <rect x="20" y="14" width="6" height="6" rx="1.5" fill="#7A4FB5" />
      <rect x="6" y="21" width="13" height="4" rx="1.5" fill="#4A5A50" />
    </svg>
  );
}

export function TopBar() {
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 200, damping: 40 });
  return (
    <>
      <motion.div className="scroll-meter" style={{ scaleX }} aria-hidden="true" />
      <nav className="topbar" aria-label="Main">
        <a href="#top" className="brand">
          <Logo />
          <span>Plotline</span>
        </a>
        <div className="topbar-links">
          <a href="#planner">Planner</a>
          <a href="#story">How it plans</a>
          <a href="#method">The rules</a>
        </div>
      </nav>
    </>
  );
}

export function Footer() {
  return (
    <footer className="footer">
      <div className="footer-brand">
        <Logo size={24} />
        <p>
          Plotline suggests a plan, not a verdict. Posting days and times are starting points; check them against your own analytics after
          the first month.
        </p>
      </div>
      <p className="footer-meta">Built with React, Framer Motion and a Flask API in Python.</p>
    </footer>
  );
}
