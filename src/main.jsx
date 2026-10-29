import React from "react";
import ReactDOM from "react-dom/client";
import { MotionConfig } from "framer-motion";
import App from "./App.jsx";
import "@fontsource/darker-grotesque/700";
import "@fontsource/darker-grotesque/800";
import "@fontsource/darker-grotesque/900";
import "@fontsource/onest/400";
import "@fontsource/onest/500";
import "@fontsource/onest/600";
import "@fontsource/onest/700";
import "./styles.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <MotionConfig reducedMotion="user">
      <App />
    </MotionConfig>
  </React.StrictMode>
);
