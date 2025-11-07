import { SpeedInsights } from "@vercel/speed-insights/react";
import React from "react";
import { createRoot } from "react-dom/client";
import { RouterProvider } from "react-router-dom";
import { router } from "./routes/router.jsx";
import "./styles.css";
import "./cursor.css";

import { Analytics } from "@vercel/analytics/react"; // <-- ajoutÃ©

createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <RouterProvider router={router} />
    <Analytics /> {/* <-- ajoutÃ© */}
      <SpeedInsights />
</React.StrictMode>
);

