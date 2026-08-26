"use client";

import { useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function ErrorBoundary({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log the error to an error reporting service
    console.error(error);
  }, [error]);

  return (
    <div className="flex h-screen w-full flex-col items-center justify-center bg-background">
      <div className="flex max-w-md flex-col items-center gap-4 text-center">
        <h2 className="text-2xl font-bold">Something went wrong!</h2>
        <p className="text-sm text-muted-foreground">
          An unexpected error occurred. You can try reloading the page.
        </p>
        <Button onClick={() => reset()}>Try again</Button>
      </div>
    </div>
  );
}
