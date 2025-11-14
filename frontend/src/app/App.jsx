import React from "react";
import { RouterProvider } from "react-router-dom";

import { AppProviders } from "./providers.jsx";
import router from "./router.jsx";

export default function App() {
  return (
    <AppProviders>
      <div style={{ minHeight: "100vh", background: "#fff", color: "#111" }}>
        <RouterProvider router={router} />
      </div>
    </AppProviders>
  );
}

