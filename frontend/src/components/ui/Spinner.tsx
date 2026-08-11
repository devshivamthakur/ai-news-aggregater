import { cn } from "@/lib/cn";

const SIZES = {
  sm: "h-4 w-4 border-2",
  md: "h-6 w-6 border-2",
  lg: "h-8 w-8 border-[3px]",
} as const;

interface SpinnerProps {
  size?: keyof typeof SIZES;
  className?: string;
}

export default function Spinner({ size = "md", className }: SpinnerProps) {
  return (
    <span
      role="status"
      aria-label="Loading"
      className={cn(
        "inline-block rounded-full border-brand-600 border-t-transparent animate-spin",
        SIZES[size],
        className
      )}
    />
  );
}
