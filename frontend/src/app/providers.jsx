import React, { useEffect, useState } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

import { ToastProvider } from "../shared/hooks/useToast.jsx";
import { withFeedbackStyles } from "../shared/components/Feedback.jsx";

export function AppProviders({ children }) {
  const [queryClient] = useState(() => new QueryClient());

  useEffect(() => {
    withFeedbackStyles();
  }, []);

  return (
    <QueryClientProvider client={queryClient}>
      <ToastProvider>{children}</ToastProvider>
    </QueryClientProvider>
  );
}

