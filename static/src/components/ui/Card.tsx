import type { HTMLAttributes } from 'react';

export function Card({ className = '', children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={`rounded-lg border border-graphite-800 bg-graphite-900 ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}
