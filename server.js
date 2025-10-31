// server.js
require("dotenv").config({ path: ".env.local" });
const express = require("express");
const path = require("path");

// on récupère tes 2 handlers Vercel
const rejoindreHandler = require("./api/rejoindre.js");
const exportIntentsHandler = require("./api/export-intents.js");

const app = express();
app.use(express.json());

// route debug pour voir les env
app.get("/api/debug-env", (req, res) => {
  res.json({
    ok: true,
    env: {
      DATABASE_URL: process.env.DATABASE_URL || null,
      ADMIN_TOKEN: process.env.ADMIN_TOKEN || null,
    },
  });
});

// on adapte un tout petit peu l’interface pour Express
app.post("/api/rejoindre", (req, res) => {
  // ton handler Vercel reçoit (req, res) déjà, donc on peut l’appeler direct
  rejoindreHandler(req, res);
});

app.get("/api/export-intents", (req, res) => {
  exportIntentsHandler(req, res);
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log("API locale EGOEJO sur http://localhost:" + PORT);
});
