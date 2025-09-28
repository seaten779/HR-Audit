"use client";

import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

const cardVariants = cva(
  // Base styles
  "rounded-lg border transition-all duration-200 relative overflow-hidden",
  {
    variants: {
      variant: {
        default: [
          "bg-slate-800/90 border-slate-700 shadow-lg backdrop-blur-sm",
          "hover:bg-slate-800 hover:border-slate-600 hover:shadow-xl",
          "hover:shadow-blue-500/5"
        ],
        glass: [
          "bg-white/5 border-white/10 shadow-2xl backdrop-blur-md",
          "hover:bg-white/10 hover:border-white/20",
          "hover:shadow-2xl hover:shadow-blue-500/10"
        ],
        gradient: [
          "bg-gradient-to-br from-slate-800 to-slate-900 border-slate-700",
          "shadow-xl hover:shadow-2xl hover:shadow-blue-500/10",
          "hover:from-slate-700 hover:to-slate-800"
        ],
        outline: [
          "bg-transparent border-slate-600 shadow-sm",
          "hover:bg-slate-900/50 hover:border-slate-500",
          "hover:shadow-md"
        ],
        elevated: [
          "bg-slate-800 border-slate-600 shadow-xl shadow-black/20",
          "hover:shadow-2xl hover:shadow-blue-500/10 hover:border-slate-500",
          "hover:-translate-y-0.5"
        ]
      },
      size: {
        sm: "p-4",
        md: "p-6", 
        lg: "p-8",
        xl: "p-10"
      },
      interactive: {
        true: "cursor-pointer select-none",
        false: ""
      }
    },
    defaultVariants: {
      variant: "default",
      size: "md",
      interactive: false
    }
  }
);

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {
  loading?: boolean;
  hover?: boolean;
  glow?: boolean;
}

const Card = forwardRef<HTMLDivElement, CardProps>(
  ({ 
    className, 
    variant, 
    size, 
    interactive, 
    loading = false,
    hover = false,
    glow = false,
    children, 
    ...props 
  }, ref) => {
    return (
      <div
        className={cn(
          cardVariants({ variant, size, interactive }),
          hover && "hover:scale-105",
          glow && "hover:shadow-blue-500/20 hover:shadow-2xl",
          loading && "animate-pulse pointer-events-none",
          className
        )}
        ref={ref}
        {...props}
      >
        {/* Subtle gradient overlay for depth */}
        <div className="absolute inset-0 bg-gradient-to-br from-white/[0.02] to-transparent pointer-events-none" />
        
        {/* Border gradient overlay */}
        <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-blue-500/5 via-transparent to-cyan-500/5 pointer-events-none opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
        
        {/* Loading overlay */}
        {loading && (
          <div className="absolute inset-0 bg-slate-800/80 rounded-lg flex items-center justify-center backdrop-blur-sm">
            <div className="flex items-center gap-3 text-slate-300">
              <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <span className="text-sm font-medium">Loading...</span>
            </div>
          </div>
        )}
        
        <div className="relative z-10">
          {children}
        </div>
      </div>
    );
  }
);

Card.displayName = "Card";

// Card sub-components
const CardHeader = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex flex-col space-y-1.5 pb-6",
      className
    )}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, children, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-xl font-semibold leading-none tracking-tight text-white",
      className
    )}
    {...props}
  >
    {children}
  </h3>
));
CardTitle.displayName = "CardTitle";

const CardDescription = forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-slate-400 leading-relaxed", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div 
    ref={ref} 
    className={cn("space-y-4", className)} 
    {...props} 
  />
));
CardContent.displayName = "CardContent";

const CardFooter = forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "flex items-center justify-between pt-6 border-t border-slate-700/50",
      className
    )}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

// Metric Card - specialized for dashboard stats
interface MetricCardProps extends Omit<CardProps, 'children'> {
  title: string;
  value: string | number;
  description?: string;
  icon?: React.ReactNode;
  trend?: {
    direction: 'up' | 'down' | 'neutral';
    value: string;
    label?: string;
  };
  color?: 'blue' | 'green' | 'red' | 'yellow' | 'purple' | 'cyan';
}

const MetricCard = forwardRef<HTMLDivElement, MetricCardProps>(
  ({ 
    title, 
    value, 
    description, 
    icon, 
    trend, 
    color = 'blue',
    className,
    ...props 
  }, ref) => {
    const colorClasses = {
      blue: {
        icon: 'bg-gradient-to-br from-blue-500 to-blue-600 text-white',
        value: 'text-blue-400',
        trend: {
          up: 'text-green-400',
          down: 'text-red-400',
          neutral: 'text-slate-400'
        }
      },
      green: {
        icon: 'bg-gradient-to-br from-green-500 to-emerald-600 text-white',
        value: 'text-green-400',
        trend: {
          up: 'text-green-400',
          down: 'text-red-400', 
          neutral: 'text-slate-400'
        }
      },
      red: {
        icon: 'bg-gradient-to-br from-red-500 to-red-600 text-white',
        value: 'text-red-400',
        trend: {
          up: 'text-green-400',
          down: 'text-red-400',
          neutral: 'text-slate-400'
        }
      },
      yellow: {
        icon: 'bg-gradient-to-br from-yellow-500 to-orange-500 text-white',
        value: 'text-yellow-400',
        trend: {
          up: 'text-green-400',
          down: 'text-red-400',
          neutral: 'text-slate-400'
        }
      },
      purple: {
        icon: 'bg-gradient-to-br from-purple-500 to-purple-600 text-white',
        value: 'text-purple-400',
        trend: {
          up: 'text-green-400',
          down: 'text-red-400',
          neutral: 'text-slate-400'
        }
      },
      cyan: {
        icon: 'bg-gradient-to-br from-cyan-500 to-teal-500 text-white',
        value: 'text-cyan-400',
        trend: {
          up: 'text-green-400',
          down: 'text-red-400',
          neutral: 'text-slate-400'
        }
      }
    };

    const colors = colorClasses[color];

    return (
      <Card
        ref={ref}
        className={cn("text-center hover:scale-105", className)}
        hover
        {...props}
      >
        {/* Icon */}
        {icon && (
          <div className={cn(
            "w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg",
            colors.icon
          )}>
            {icon}
          </div>
        )}

        {/* Title */}
        <h3 className="text-xl font-semibold text-white mb-3">
          {title}
        </h3>

        {/* Value with trend */}
        <div className="flex items-center justify-center gap-3 mb-2">
          <span className={cn("text-3xl font-bold", colors.value)}>
            {typeof value === 'number' ? value.toLocaleString() : value}
          </span>
          
          {trend && (
            <div className="flex items-center text-sm">
              <span className={colors.trend[trend.direction]}>
                {trend.direction === 'up' && '↗'}
                {trend.direction === 'down' && '↘'}
                {trend.direction === 'neutral' && '→'}
              </span>
            </div>
          )}
        </div>

        {/* Description */}
        {description && (
          <p className="text-base text-slate-300 mb-2">
            {description}
          </p>
        )}

        {/* Trend label */}
        {trend?.label && (
          <p className="text-xs text-slate-400">
            {trend.label}
          </p>
        )}
      </Card>
    );
  }
);

MetricCard.displayName = "MetricCard";

export {
  Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
  MetricCard,
  cardVariants
};