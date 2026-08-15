import { cn } from "@/lib/utils";

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "secondary" | "ghost" | "warning";
  size?: "sm" | "md" | "lg";
};

export function Button({
  className,
  variant = "primary",
  size = "md",
  ...props
}: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center font-medium transition-colors disabled:opacity-50 disabled:pointer-events-none",
        {
          "bg-accent text-black hover:bg-accent-hover": variant === "primary",
          "bg-elevated text-primary hover:bg-input": variant === "secondary",
          "bg-transparent text-secondary hover:text-primary hover:bg-elevated":
            variant === "ghost",
          "bg-warning text-black hover:opacity-90": variant === "warning",
          "h-8 px-3 text-sm rounded-button": size === "sm",
          "h-10 px-4 text-sm rounded-button": size === "md",
          "h-12 px-6 text-base rounded-composer": size === "lg",
        },
        className,
      )}
      {...props}
    />
  );
}
