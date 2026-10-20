
import { useEffect, useRef, useState } from "react";
import { cn } from "@/shared/cn";

interface RevealProps {
  children: React.ReactNode;
  className?: string;
  /** Stagger delay in milliseconds before the element animates in. */
  delay?: number;
}

/**
 * Fades + slides children in the first time they enter the viewport.
 * Uses a one-shot IntersectionObserver so the animation plays once, then the
 * element stays visible (avoids re-hiding on scroll). Honors the global
 * `prefers-reduced-motion` rule via the `.reveal` CSS class.
 */
export default function Reveal({ children, className, delay = 0 }: RevealProps) {
  const ref = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (typeof IntersectionObserver === "undefined") {
      setVisible(true);
      return;
    }
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
      className={cn("reveal", visible && "reveal-visible", className)}
    >
      {children}
    </div>
  );
}
