import "./sentry.client.js";
import "./utils/gsap-extras.js";
import "./styles/global.css";
import React, { Suspense } from "react";
import { createRoot } from "react-dom/client";
import ErrorBoundary from "./ErrorBoundary.jsx";
import App from "./app/App.jsx";

const root = createRoot(document.getElementById("root"));
root.render(
  <ErrorBoundary>
    <Suspense fallback={<div />}>
      <App />
    </Suspense>
  </ErrorBoundary>
);

