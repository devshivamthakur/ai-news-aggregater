
import { cn } from "@/shared/cn";
import Spinner from "./Spinner";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  /** Shows a spinner and disables the button while true. */
  loading?: boolean;
  /** Icon rendered to the left of the label (hidden while loading). */
  icon?: React.ReactNode;
}

const VARIANTS: Record<ButtonVariant, string> = {
  primary: "bg-brand-600 hover:bg-brand-700 text-white shadow-soft hover:shadow-glow",
  secondary: "bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 hover:border-slate-300",
  danger: "bg-red-500 hover:bg-red-600 text-white shadow-soft",
  ghost: "text-slate-600 hover:bg-slate-100 hover:text-slate-900",
};

const SIZES: Record<ButtonSize, string> = {
  sm: "text-sm px-3 py-1.5 gap-1.5",
  md: "px-4 py-2 gap-2",
  lg: "text-lg px-6 py-3 gap-2",
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  icon,
  className,
  children,
  disabled,
  type = "button",
  ...rest
}: ButtonProps) {
  return (
    <button
      type={type}
      disabled={disabled || loading}
      className={cn(
        "inline-flex items-center justify-center rounded-xl font-medium transition-all duration-200",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-brand-500 focus-visible:ring-offset-2",
        "disabled:cursor-not-allowed disabled:opacity-50 enabled:active:scale-[0.97]",
        VARIANTS[variant],
        SIZES[size],
        className
      )}
      {...rest}
    >
      {loading ? <Spinner size="sm" /> : icon}
      {children}
    </button>
  );
}
