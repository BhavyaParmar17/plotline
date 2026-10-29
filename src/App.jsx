import { useCallback, useState } from "react";
import { Footer, TopBar } from "./components/Chrome.jsx";
import Hero from "./components/Hero.jsx";
import Planner from "./components/Planner.jsx";
import Story from "./components/Story.jsx";
import Method from "./components/Method.jsx";

export default function App() {
  const [request, setRequest] = useState(null);
  const handled = useCallback(() => setRequest(null), []);
  return (
    <>
      <a href="#planner" className="skip-link">Skip to the planner</a>
      <TopBar />
      <main>
        <Hero onStart={setRequest} />
        <Planner request={request} onRequestHandled={handled} />
        <Story />
        <Method />
      </main>
      <Footer />
    </>
  );
}
