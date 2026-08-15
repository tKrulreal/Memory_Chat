import { cn } from "@/lib/utils";

function Skeleton({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-surface/80 border border-subtle/20", className)}
      {...props}
    />
  );
}

export { Skeleton };
