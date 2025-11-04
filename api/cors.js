const allowedOrigins = new Set(
  ["http://localhost:5173", process.env.FRONTEND_URL]
    .filter(Boolean)
    .map((value) => value.replace(/\/$/, ""))
);

function prepareCors(req, res, options = {}) {
  const { methods = ["GET", "OPTIONS"], allowHeaders = ["Content-Type", "Authorization"] } = options;
  const origin = req.headers.origin || "";

  if (origin && !allowedOrigins.has(origin)) {
    res.setHeader("Vary", "Origin");
    return { allowed: false, origin };
  }

  const headerOrigin = origin || "*";
  res.setHeader("Access-Control-Allow-Origin", headerOrigin);
  res.setHeader("Access-Control-Allow-Methods", methods.join(","));
  res.setHeader("Access-Control-Allow-Headers", allowHeaders.join(","));
  res.setHeader("Access-Control-Max-Age", "86400");
  res.setHeader("Vary", "Origin");

  return { allowed: true, origin: headerOrigin };
}

module.exports = { prepareCors };

