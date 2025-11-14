import * as Sentry from "@sentry/browser";
import { BrowserTracing } from "@sentry/tracing";

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
