import * as Sentry from "@sentry/browser";
import { BrowserTracing } from "@sentry/tracing";

Sentry.init({
  dsn: "https://SENTRY_DSN",
  integrations: [new BrowserTracing()],
  tracesSampleRate: 0.1,
  environment: "production"
});
