import React from "react";
import { createRoot } from "react-dom/client";
import Legacy from "./main.backup.jsx";

const root = createRoot(document.getElementById("root"));
root.render(<Legacy />);
