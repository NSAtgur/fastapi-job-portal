import { forwardRef, useId } from 'react';
import type { InputHTMLAttributes } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, hint, className = '', id, ...props }, ref) => {
    const generatedId = useId();
    const inputId = id || generatedId;

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-[13px] font-medium text-paper-dim tracking-wide"
          >
            {label}
          </label>
        )}
        <input
          ref={ref}
          id={inputId}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : hint ? `${inputId}-hint` : undefined}
          className={`h-10 rounded-md border bg-graphite-900 px-3 text-sm text-paper
            placeholder:text-paper-faint outline-none transition-colors
            border-graphite-700 focus:border-amber
            ${error ? 'border-status-rejected focus:border-status-rejected' : ''}
            ${className}`}
          {...props}
        />
        {error ? (
          <span id={`${inputId}-error`} className="text-[12px] text-status-rejected">
            {error}
          </span>
        ) : hint ? (
          <span id={`${inputId}-hint`} className="text-[12px] text-paper-faint">
            {hint}
          </span>
        ) : null}
      </div>
    );
  }
);
Input.displayName = 'Input';
