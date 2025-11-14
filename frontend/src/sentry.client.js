import * as Sentry from "@sentry/browser";
import { BrowserTracing } from "@sentry/tracing";

<<<<<<< HEAD:src/sentry.client.js
const dsn = import.meta.env.VITE_SENTRY_DSN && import.meta.env.VITE_SENTRY_DSN.trim();

if (dsn) {
  const environment =
    import.meta.env.VITE_SENTRY_ENV ||
    (import.meta.env.DEV ? "development" : import.meta.env.MODE || "production");

  const tracesSampleRate = Number.parseFloat(import.meta.env.VITE_SENTRY_TRACES_SAMPLE_RATE || "0.1");

  Sentry.init({
    dsn,
    integrations: [new BrowserTracing()],
    tracesSampleRate: Number.isFinite(tracesSampleRate) ? tracesSampleRate : 0.1,
    environment
  });
} else if (import.meta.env.DEV) {
  console.info(
    "[Sentry] VITE_SENTRY_DSN non défini : instrumentation désactivée pour cet environnement."
  );
}
=======
Sentry.init({
  dsn: "https://SENTRY_DSN",
  integrations: [new BrowserTracing()],
  tracesSampleRate: 0.1,
  environment: "production"
});
>>>>>>> 154e1db72fc940dea87fbfb88c6ceeb01aac9d19:frontend/src/sentry.client.js
