const Sentry = require("@sentry/node");
if (process.env.SENTRY_DSN) {
  Sentry.init({ dsn: process.env.SENTRY_DSN, tracesSampleRate: 0.1, environment: "production" });
  process.on("uncaughtException", (e)=>Sentry.captureException(e));
  process.on("unhandledRejection", (e)=>Sentry.captureException(e));
}
module.exports = Sentry;
