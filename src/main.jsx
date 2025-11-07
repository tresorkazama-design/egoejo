import "./sentry.client.js";
import React, { Suspense } from "react";
import { createRoot } from "react-dom/client";
import ErrorBoundary from "./ErrorBoundary.jsx";
import App from "./App.jsx";

const root = createRoot(document.getElementById("root"));
root.render(
  <ErrorBoundary>
    <Suspense fallback={<div/>}>
      <App />
    </Suspense>
  </ErrorBoundary>
);

