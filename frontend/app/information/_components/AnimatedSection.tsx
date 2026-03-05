"use client";

import { useInView } from "./useInView";

interface AnimatedSectionProps {
  children: React.ReactNode;
  animation?: string;
  className?: string;
  delay?: string;
}

export function AnimatedSection({
  children,
  animation = "promo-fade-up",
  className = "",
  delay,
}: AnimatedSectionProps) {
  const { ref, isVisible } = useInView();

  return (
    <div
      ref={ref}
      className={`promo-animated ${isVisible ? `promo-visible ${animation}` : ""} ${className}`}
      style={delay ? { animationDelay: delay } : undefined}
    >
      {children}
    </div>
  );
}
