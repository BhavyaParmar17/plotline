import { motion } from "framer-motion";

const ease = [0.22, 1, 0.36, 1];
const WEEK = [
  { day: "Mon", posts: [{ p: "IG", f: "Reel", t: "Behind the scenes", c: "#B7741A" }] },
  { day: "Tue", posts: [{ p: "in", f: "Document", t: "Educate", c: "#2F6FB0" }, { p: "IG", f: "Carousel", t: "Proof", c: "#1F8A5B" }] },
  { day: "Wed", posts: [{ p: "in", f: "Poll", t: "Conversation", c: "#B83B5E" }] },
  { day: "Thu", posts: [{ p: "IG", f: "Reel", t: "Showcase", c: "#7A4FB5" }, { p: "in", f: "Text", t: "Educate", c: "#2F6FB0" }] },
  { day: "Fri", posts: [{ p: "FB", f: "Image", t: "Offer", c: "#0E7C86" }] },
  { day: "Sat", posts: [{ p: "IG", f: "Story", t: "Conversation", c: "#B83B5E" }] },
  { day: "Sun", posts: [] },
];

export default function Hero({ onStart }) {
  let n = 0;
  return (
    <header className="hero" id="top">
      <div className="hero-copy">
        <h1>
          {["Plan the month", "from the goal down."].map((line, i) => (
            <span className="line" key={line}>
              <motion.span initial={{ y: "110%" }} animate={{ y: 0 }} transition={{ duration: 0.85, ease, delay: i * 0.1 }}>
                {line}
              </motion.span>
            </span>
          ))}
        </h1>
        <motion.p className="hero-lede" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.45, duration: 0.6 }}>
          Give Plotline a business goal, your audience, campaigns, services and the photos and videos you have. It builds a month of dated
          posts with a balanced mix of themes and formats, flags ideas that repeat, and exports the plan to CSV or Excel for review.
        </motion.p>
        <motion.div className="hero-actions" initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.55, duration: 0.6 }}>
          <button type="button" className="btn btn-primary" onClick={() => onStart("sample")}>Plan a sample month</button>
          <button type="button" className="btn btn-quiet" onClick={() => onStart("own")}>Start my own brief</button>
        </motion.div>
      </div>
      <div className="hero-week" aria-label="Example week of planned posts">
        {WEEK.map((d) => (
          <div key={d.day} className="hw-day">
            <span className="hw-label">{d.day}</span>
            <div className="hw-cell">
              {d.posts.map((p) => {
                n += 1;
                return (
                  <motion.div
                    key={p.p + p.f + p.t}
                    className="hw-tab"
                    style={{ "--c": p.c }}
                    initial={{ opacity: 0, y: -26, rotate: -4 }}
                    animate={{ opacity: 1, y: 0, rotate: 0 }}
                    transition={{ delay: 0.5 + n * 0.11, type: "spring", stiffness: 260, damping: 20 }}
                  >
                    <span className="hw-plat">{p.p}</span>
                    <span className="hw-fmt">{p.f}</span>
                    <span className="hw-theme">{p.t}</span>
                  </motion.div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </header>
  );
}
