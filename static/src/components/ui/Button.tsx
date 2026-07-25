import { forwardRef } from 'react';
import type { ButtonHTMLAttributes } from 'react';
import { motion } from 'framer-motion';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'outline' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
}

const variants = {
  primary:
    'bg-amber text-graphite-950 hover:bg-amber-bright active:bg-amber-dim disabled:bg-graphite-700 disabled:text-paper-faint',
  outline:
    'border border-graphite-600 text-paper hover:border-amber hover:text-amber bg-transparent disabled:opacity-40',
  ghost:
    'text-paper-dim hover:text-paper hover:bg-graphite-800 bg-transparent disabled:opacity-40',
  danger:
    'bg-status-rejected/90 text-paper hover:bg-status-rejected disabled:opacity-40',
};

const sizes = {
  sm: 'h-8 px-3 text-[13px]',
  md: 'h-10 px-4 text-sm',
  lg: 'h-12 px-6 text-[15px]',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    { variant = 'primary', size = 'md', loading, className = '', children, disabled, ...props },
    ref
  ) => {
    const isDisabled = disabled || loading;
    return (
      <motion.button
        ref={ref}
        disabled={isDisabled}
        whileTap={isDisabled ? undefined : { scale: 0.97 }}
        transition={{ duration: 0.12, ease: 'easeOut' }}
        className={`inline-flex items-center justify-center gap-2 rounded-md font-medium
          tracking-tight transition-colors duration-150 cursor-pointer
          disabled:cursor-not-allowed
          ${variants[variant]} ${sizes[size]} ${className}`}
        {...(props as any)}
      >
        {loading ? (
          <span className="h-3.5 w-3.5 rounded-full border-2 border-current border-t-transparent animate-spin" />
        ) : null}
        {children}
      </motion.button>
    );
  }
);
Button.displayName = 'Button';
