"use client";

import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const buttonVariants = cva(
  // Base styles
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-lg text-sm font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 relative overflow-hidden",
  {
    variants: {
      variant: {
        primary: [
          "bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-md",
          "hover:from-blue-700 hover:to-blue-800 hover:shadow-lg hover:shadow-blue-500/25",
          "active:from-blue-800 active:to-blue-900",
          "focus-visible:ring-blue-500",
          "border border-blue-600/20",
        ],
        secondary: [
          "bg-slate-800 text-slate-200 border border-slate-700 shadow-sm",
          "hover:bg-slate-700 hover:border-slate-600 hover:text-white hover:shadow-md",
          "active:bg-slate-900 active:border-slate-800",
          "focus-visible:ring-slate-400",
        ],
        accent: [
          "bg-gradient-to-r from-cyan-500 to-teal-500 text-white shadow-md",
          "hover:from-cyan-600 hover:to-teal-600 hover:shadow-lg hover:shadow-cyan-500/25",
          "active:from-cyan-700 active:to-teal-700",
          "focus-visible:ring-cyan-400",
          "border border-cyan-400/20",
        ],
        success: [
          "bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-md",
          "hover:from-green-700 hover:to-emerald-700 hover:shadow-lg hover:shadow-green-500/25",
          "active:from-green-800 active:to-emerald-800",
          "focus-visible:ring-green-500",
          "border border-green-500/20",
        ],
        warning: [
          "bg-gradient-to-r from-yellow-500 to-orange-500 text-white shadow-md",
          "hover:from-yellow-600 hover:to-orange-600 hover:shadow-lg hover:shadow-yellow-500/25",
          "active:from-yellow-700 active:to-orange-700",
          "focus-visible:ring-yellow-400",
          "border border-yellow-400/20",
        ],
        danger: [
          "bg-gradient-to-r from-red-600 to-red-700 text-white shadow-md",
          "hover:from-red-700 hover:to-red-800 hover:shadow-lg hover:shadow-red-500/25",
          "active:from-red-800 active:to-red-900",
          "focus-visible:ring-red-500",
          "border border-red-500/20",
        ],
        outline: [
          "border-2 border-slate-600 text-slate-300 bg-transparent",
          "hover:border-slate-500 hover:text-white hover:bg-slate-800/50",
          "active:border-slate-400 active:bg-slate-700/50",
          "focus-visible:ring-slate-400",
        ],
        ghost: [
          "text-slate-300 bg-transparent",
          "hover:text-white hover:bg-slate-800/50",
          "active:bg-slate-700/50",
          "focus-visible:ring-slate-400",
        ],
        glass: [
          "bg-white/10 text-white backdrop-blur-sm border border-white/20 shadow-lg",
          "hover:bg-white/15 hover:border-white/30",
          "active:bg-white/20",
          "focus-visible:ring-white/50",
        ]
      },
      size: {
        sm: "h-8 px-3 text-xs",
        md: "h-10 px-4 text-sm",
        lg: "h-12 px-6 text-base",
        xl: "h-14 px-8 text-lg",
        icon: "h-10 w-10 p-0",
        "icon-sm": "h-8 w-8 p-0 text-xs",
        "icon-lg": "h-12 w-12 p-0 text-base",
      },
      fullWidth: {
        true: "w-full",
        false: "w-auto"
      }
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
      fullWidth: false,
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ 
    className, 
    variant, 
    size, 
    fullWidth,
    loading = false, 
    leftIcon, 
    rightIcon, 
    children, 
    disabled,
    ...props 
  }, ref) => {
    const isDisabled = disabled || loading;

    return (
      <button
        className={cn(
          buttonVariants({ variant, size, fullWidth }),
          className
        )}
        ref={ref}
        disabled={isDisabled}
        {...props}
      >
        {/* Loading spinner */}
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          </div>
        )}
        
        {/* Content wrapper - hidden when loading */}
        <div className={cn(
          "flex items-center justify-center gap-2",
          loading && "opacity-0"
        )}>
          {leftIcon && (
            <span className="flex-shrink-0">
              {leftIcon}
            </span>
          )}
          
          {children && (
            <span className="truncate">
              {children}
            </span>
          )}
          
          {rightIcon && (
            <span className="flex-shrink-0">
              {rightIcon}
            </span>
          )}
        </div>

        {/* Ripple effect overlay */}
        <div className="absolute inset-0 -z-10 bg-gradient-to-r from-white/0 via-white/20 to-white/0 translate-x-[-100%] hover:translate-x-[100%] transition-transform duration-700 ease-out" />
      </button>
    );
  }
);

Button.displayName = "Button";

export { Button, buttonVariants };