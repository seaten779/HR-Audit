"use client";

import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { Eye, EyeOff, AlertCircle, CheckCircle } from 'lucide-react';

const inputVariants = cva(
  // Base styles
  "flex w-full rounded-lg border bg-transparent px-3 py-2 text-sm transition-all duration-200 placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 disabled:cursor-not-allowed disabled:opacity-50",
  {
    variants: {
      variant: {
        default: [
          "border-slate-700 bg-slate-800/50 text-slate-200",
          "hover:border-slate-600 hover:bg-slate-800",
          "focus-visible:border-blue-500 focus-visible:ring-blue-500/20",
        ],
        glass: [
          "border-white/20 bg-white/5 text-white backdrop-blur-sm",
          "hover:border-white/30 hover:bg-white/10",
          "focus-visible:border-blue-400 focus-visible:ring-blue-400/20",
        ],
        outline: [
          "border-slate-600 bg-transparent text-slate-200",
          "hover:border-slate-500",
          "focus-visible:border-blue-500 focus-visible:ring-blue-500/20",
        ]
      },
      size: {
        sm: "h-8 px-2 text-xs",
        md: "h-10 px-3 text-sm",
        lg: "h-12 px-4 text-base",
      },
      state: {
        default: "",
        error: [
          "border-red-500 bg-red-900/10",
          "focus-visible:border-red-500 focus-visible:ring-red-500/20",
          "placeholder:text-red-300"
        ],
        success: [
          "border-green-500 bg-green-900/10",
          "focus-visible:border-green-500 focus-visible:ring-green-500/20",
        ],
        warning: [
          "border-yellow-500 bg-yellow-900/10",
          "focus-visible:border-yellow-500 focus-visible:ring-yellow-500/20",
        ]
      }
    },
    defaultVariants: {
      variant: "default",
      size: "md",
      state: "default"
    }
  }
);

export interface InputProps
  extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'size'>,
    VariantProps<typeof inputVariants> {
  label?: string;
  description?: string;
  error?: string;
  success?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  loading?: boolean;
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ 
    className, 
    type, 
    variant, 
    size, 
    state, 
    label, 
    description, 
    error, 
    success,
    leftIcon, 
    rightIcon, 
    loading,
    disabled,
    ...props 
  }, ref) => {
    const [showPassword, setShowPassword] = React.useState(false);
    const isPassword = type === 'password';
    const inputType = isPassword && showPassword ? 'text' : type;
    
    // Determine state based on props
    const currentState = error ? 'error' : success ? 'success' : state;

    return (
      <div className="space-y-2">
        {/* Label */}
        {label && (
          <label className="text-sm font-medium text-slate-200 block">
            {label}
          </label>
        )}
        
        {/* Input container */}
        <div className="relative">
          {/* Left icon */}
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none">
              {leftIcon}
            </div>
          )}
          
          {/* Input field */}
          <input
            type={inputType}
            className={cn(
              inputVariants({ variant, size, state: currentState }),
              leftIcon && "pl-10",
              (rightIcon || isPassword || loading) && "pr-10",
              className
            )}
            ref={ref}
            disabled={disabled || loading}
            {...props}
          />
          
          {/* Right side icons */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            {/* Loading spinner */}
            {loading && (
              <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
            )}
            
            {/* State icons */}
            {!loading && currentState === 'error' && (
              <AlertCircle className="w-4 h-4 text-red-400" />
            )}
            {!loading && currentState === 'success' && (
              <CheckCircle className="w-4 h-4 text-green-400" />
            )}
            
            {/* Custom right icon */}
            {!loading && rightIcon && !isPassword && (
              <div className="text-slate-400">
                {rightIcon}
              </div>
            )}
            
            {/* Password toggle */}
            {!loading && isPassword && (
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="text-slate-400 hover:text-slate-300 transition-colors"
                tabIndex={-1}
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            )}
          </div>
        </div>
        
        {/* Description */}
        {description && !error && !success && (
          <p className="text-xs text-slate-400">
            {description}
          </p>
        )}
        
        {/* Error message */}
        {error && (
          <p className="text-xs text-red-400 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {error}
          </p>
        )}
        
        {/* Success message */}
        {success && (
          <p className="text-xs text-green-400 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            {success}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

// Select Component
const selectVariants = cva(
  "flex h-10 w-full items-center justify-between rounded-lg border bg-transparent px-3 py-2 text-sm transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:cursor-not-allowed disabled:opacity-50 [&>span]:line-clamp-1",
  {
    variants: {
      variant: {
        default: [
          "border-slate-700 bg-slate-800/50 text-slate-200",
          "hover:border-slate-600 hover:bg-slate-800",
          "focus:border-blue-500 focus:ring-blue-500/20",
        ],
        glass: [
          "border-white/20 bg-white/5 text-white backdrop-blur-sm",
          "hover:border-white/30 hover:bg-white/10",
          "focus:border-blue-400 focus:ring-blue-400/20",
        ],
      },
      state: {
        default: "",
        error: [
          "border-red-500 bg-red-900/10",
          "focus:border-red-500 focus:ring-red-500/20",
        ],
        success: [
          "border-green-500 bg-green-900/10",
          "focus:border-green-500 focus:ring-green-500/20",
        ]
      }
    },
    defaultVariants: {
      variant: "default",
      state: "default"
    }
  }
);

export interface SelectProps
  extends Omit<React.SelectHTMLAttributes<HTMLSelectElement>, 'size'>,
    VariantProps<typeof selectVariants> {
  label?: string;
  description?: string;
  error?: string;
  success?: string;
  placeholder?: string;
  loading?: boolean;
}

const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ 
    className, 
    variant, 
    state, 
    label, 
    description, 
    error, 
    success,
    placeholder,
    loading,
    disabled,
    children,
    ...props 
  }, ref) => {
    const currentState = error ? 'error' : success ? 'success' : state;

    return (
      <div className="space-y-2">
        {/* Label */}
        {label && (
          <label className="text-sm font-medium text-slate-200 block">
            {label}
          </label>
        )}
        
        {/* Select container */}
        <div className="relative">
          <select
            className={cn(
              selectVariants({ variant, state: currentState }),
              "appearance-none cursor-pointer",
              loading && "pr-10",
              className
            )}
            ref={ref}
            disabled={disabled || loading}
            {...props}
          >
            {placeholder && (
              <option value="" disabled>
                {placeholder}
              </option>
            )}
            {children}
          </select>
          
          {/* Dropdown arrow */}
          <div className="absolute right-3 top-1/2 -translate-y-1/2 pointer-events-none">
            {loading ? (
              <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
            ) : (
              <svg
                className="w-4 h-4 text-slate-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 9l-7 7-7-7"
                />
              </svg>
            )}
          </div>
        </div>
        
        {/* Description */}
        {description && !error && !success && (
          <p className="text-xs text-slate-400">
            {description}
          </p>
        )}
        
        {/* Error message */}
        {error && (
          <p className="text-xs text-red-400 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {error}
          </p>
        )}
        
        {/* Success message */}
        {success && (
          <p className="text-xs text-green-400 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            {success}
          </p>
        )}
      </div>
    );
  }
);

Select.displayName = "Select";

// TextArea Component
export interface TextAreaProps
  extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  description?: string;
  error?: string;
  success?: string;
  variant?: 'default' | 'glass';
  state?: 'default' | 'error' | 'success';
  resize?: boolean;
}

const TextArea = forwardRef<HTMLTextAreaElement, TextAreaProps>(
  ({ 
    className, 
    label, 
    description, 
    error, 
    success,
    variant = 'default',
    state = 'default',
    resize = true,
    disabled,
    ...props 
  }, ref) => {
    const currentState = error ? 'error' : success ? 'success' : state;

    return (
      <div className="space-y-2">
        {/* Label */}
        {label && (
          <label className="text-sm font-medium text-slate-200 block">
            {label}
          </label>
        )}
        
        {/* TextArea */}
        <textarea
          className={cn(
            "flex min-h-[80px] w-full rounded-lg border px-3 py-2 text-sm transition-all duration-200 placeholder:text-slate-500 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-900 disabled:cursor-not-allowed disabled:opacity-50",
            // Variant styles
            variant === 'default' && [
              "border-slate-700 bg-slate-800/50 text-slate-200",
              "hover:border-slate-600 hover:bg-slate-800",
              "focus-visible:border-blue-500 focus-visible:ring-blue-500/20",
            ],
            variant === 'glass' && [
              "border-white/20 bg-white/5 text-white backdrop-blur-sm",
              "hover:border-white/30 hover:bg-white/10",
              "focus-visible:border-blue-400 focus-visible:ring-blue-400/20",
            ],
            // State styles
            currentState === 'error' && [
              "border-red-500 bg-red-900/10",
              "focus-visible:border-red-500 focus-visible:ring-red-500/20",
            ],
            currentState === 'success' && [
              "border-green-500 bg-green-900/10",
              "focus-visible:border-green-500 focus-visible:ring-green-500/20",
            ],
            !resize && "resize-none",
            className
          )}
          ref={ref}
          disabled={disabled}
          {...props}
        />
        
        {/* Description */}
        {description && !error && !success && (
          <p className="text-xs text-slate-400">
            {description}
          </p>
        )}
        
        {/* Error message */}
        {error && (
          <p className="text-xs text-red-400 flex items-center gap-1">
            <AlertCircle className="w-3 h-3" />
            {error}
          </p>
        )}
        
        {/* Success message */}
        {success && (
          <p className="text-xs text-green-400 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            {success}
          </p>
        )}
      </div>
    );
  }
);

TextArea.displayName = "TextArea";

export { Input, Select, TextArea, inputVariants, selectVariants };