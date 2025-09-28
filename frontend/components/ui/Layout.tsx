"use client";

import React, { forwardRef } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';

// Container Component
const containerVariants = cva(
  "w-full mx-auto px-4 sm:px-6",
  {
    variants: {
      size: {
        sm: "max-w-3xl",
        md: "max-w-5xl", 
        lg: "max-w-7xl",
        xl: "max-w-screen-2xl",
        full: "max-w-full",
        none: ""
      },
      padding: {
        none: "px-0",
        sm: "px-4 sm:px-6",
        md: "px-4 sm:px-6 lg:px-8",
        lg: "px-6 sm:px-8 lg:px-12",
      }
    },
    defaultVariants: {
      size: "lg",
      padding: "md"
    }
  }
);

export interface ContainerProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof containerVariants> {}

const Container = forwardRef<HTMLDivElement, ContainerProps>(
  ({ className, size, padding, ...props }, ref) => {
    return (
      <div
        className={cn(containerVariants({ size, padding }), className)}
        ref={ref}
        {...props}
      />
    );
  }
);

Container.displayName = "Container";

// Grid Component
const gridVariants = cva(
  "grid",
  {
    variants: {
      cols: {
        1: "grid-cols-1",
        2: "grid-cols-1 md:grid-cols-2",
        3: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3",
        4: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4",
        5: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5",
        6: "grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6",
        auto: "grid-cols-[repeat(auto-fit,minmax(280px,1fr))]"
      },
      gap: {
        none: "gap-0",
        sm: "gap-2 sm:gap-3",
        md: "gap-4 sm:gap-6", 
        lg: "gap-6 sm:gap-8",
        xl: "gap-8 sm:gap-10",
      }
    },
    defaultVariants: {
      cols: "auto",
      gap: "md"
    }
  }
);

export interface GridProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof gridVariants> {}

const Grid = forwardRef<HTMLDivElement, GridProps>(
  ({ className, cols, gap, ...props }, ref) => {
    return (
      <div
        className={cn(gridVariants({ cols, gap }), className)}
        ref={ref}
        {...props}
      />
    );
  }
);

Grid.displayName = "Grid";

// Flex Component
const flexVariants = cva(
  "flex",
  {
    variants: {
      direction: {
        row: "flex-row",
        column: "flex-col",
        "row-reverse": "flex-row-reverse",
        "column-reverse": "flex-col-reverse"
      },
      align: {
        start: "items-start",
        center: "items-center",
        end: "items-end",
        stretch: "items-stretch",
        baseline: "items-baseline"
      },
      justify: {
        start: "justify-start",
        center: "justify-center",
        end: "justify-end",
        between: "justify-between",
        around: "justify-around",
        evenly: "justify-evenly"
      },
      wrap: {
        true: "flex-wrap",
        false: "flex-nowrap",
        reverse: "flex-wrap-reverse"
      },
      gap: {
        none: "gap-0",
        sm: "gap-2",
        md: "gap-4",
        lg: "gap-6",
        xl: "gap-8"
      }
    },
    defaultVariants: {
      direction: "row",
      align: "center",
      justify: "start",
      wrap: false,
      gap: "md"
    }
  }
);

export interface FlexProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof flexVariants> {}

const Flex = forwardRef<HTMLDivElement, FlexProps>(
  ({ className, direction, align, justify, wrap, gap, ...props }, ref) => {
    return (
      <div
        className={cn(flexVariants({ direction, align, justify, wrap, gap }), className)}
        ref={ref}
        {...props}
      />
    );
  }
);

Flex.displayName = "Flex";

// Stack Component (vertical Flex)
export interface StackProps extends Omit<FlexProps, 'direction'> {
  spacing?: 'sm' | 'md' | 'lg' | 'xl';
}

const Stack = forwardRef<HTMLDivElement, StackProps>(
  ({ spacing = 'md', gap, ...props }, ref) => {
    const stackGap = gap || spacing;
    return (
      <Flex
        direction="column"
        gap={stackGap}
        ref={ref}
        {...props}
      />
    );
  }
);

Stack.displayName = "Stack";

// Center Component
export interface CenterProps extends React.HTMLAttributes<HTMLDivElement> {
  inline?: boolean;
}

const Center = forwardRef<HTMLDivElement, CenterProps>(
  ({ className, inline = false, children, ...props }, ref) => {
    const Component = inline ? 'span' : 'div';
    
    return (
      <Component
        className={cn(
          "flex items-center justify-center",
          inline && "inline-flex",
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </Component>
    );
  }
);

Center.displayName = "Center";

// Spacer Component
export interface SpacerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl' | number;
  axis?: 'horizontal' | 'vertical' | 'both';
}

const Spacer: React.FC<SpacerProps> = ({ 
  size = 'md', 
  axis = 'both' 
}) => {
  const sizeMap = {
    sm: '0.5rem',
    md: '1rem', 
    lg: '2rem',
    xl: '3rem'
  };

  const spacing = typeof size === 'number' ? `${size}px` : sizeMap[size];
  
  const styles: React.CSSProperties = {};
  
  if (axis === 'horizontal' || axis === 'both') {
    styles.width = spacing;
  }
  if (axis === 'vertical' || axis === 'both') {
    styles.height = spacing;
  }
  
  return <div style={styles} />;
};

Spacer.displayName = "Spacer";

// Divider Component
export interface DividerProps extends React.HTMLAttributes<HTMLDivElement> {
  orientation?: 'horizontal' | 'vertical';
  variant?: 'solid' | 'dashed' | 'dotted';
  spacing?: 'sm' | 'md' | 'lg';
  color?: 'default' | 'muted' | 'accent';
}

const Divider = forwardRef<HTMLDivElement, DividerProps>(
  ({ 
    className,
    orientation = 'horizontal',
    variant = 'solid',
    spacing = 'md',
    color = 'default',
    ...props 
  }, ref) => {
    const baseStyles = cn(
      "flex-shrink-0",
      // Orientation
      orientation === 'horizontal' 
        ? "w-full h-px" 
        : "h-full w-px",
      // Spacing
      orientation === 'horizontal' 
        ? {
            'my-2': spacing === 'sm',
            'my-4': spacing === 'md', 
            'my-6': spacing === 'lg'
          }
        : {
            'mx-2': spacing === 'sm',
            'mx-4': spacing === 'md',
            'mx-6': spacing === 'lg'
          },
      // Color
      {
        'bg-slate-700': color === 'default',
        'bg-slate-600': color === 'muted',
        'bg-blue-500': color === 'accent'
      },
      // Variant
      {
        'border-none': variant === 'solid',
        'border-dashed border-t border-current bg-transparent': variant === 'dashed' && orientation === 'horizontal',
        'border-dashed border-l border-current bg-transparent': variant === 'dashed' && orientation === 'vertical',
        'border-dotted border-t border-current bg-transparent': variant === 'dotted' && orientation === 'horizontal',
        'border-dotted border-l border-current bg-transparent': variant === 'dotted' && orientation === 'vertical'
      }
    );

    return (
      <div
        className={cn(baseStyles, className)}
        role="separator"
        aria-orientation={orientation}
        ref={ref}
        {...props}
      />
    );
  }
);

Divider.displayName = "Divider";

// Page Layout Components
export interface PageHeaderProps extends React.HTMLAttributes<HTMLDivElement> {
  title: string;
  description?: string;
  action?: React.ReactNode;
  breadcrumb?: React.ReactNode;
}

const PageHeader = forwardRef<HTMLDivElement, PageHeaderProps>(
  ({ className, title, description, action, breadcrumb, ...props }, ref) => {
    return (
      <div
        className={cn("space-y-6 pb-8 border-b border-slate-700/50", className)}
        ref={ref}
        {...props}
      >
        {breadcrumb && (
          <div className="text-sm text-slate-400">
            {breadcrumb}
          </div>
        )}
        
        <div className="flex items-start justify-between gap-6">
          <div className="space-y-2">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-blue-100 to-cyan-200 bg-clip-text text-transparent">
              {title}
            </h1>
            {description && (
              <p className="text-lg text-slate-300 max-w-3xl">
                {description}
              </p>
            )}
          </div>
          
          {action && (
            <div className="flex-shrink-0">
              {action}
            </div>
          )}
        </div>
      </div>
    );
  }
);

PageHeader.displayName = "PageHeader";

export interface PageContentProps extends React.HTMLAttributes<HTMLDivElement> {
  spacing?: 'sm' | 'md' | 'lg' | 'xl';
}

const PageContent = forwardRef<HTMLDivElement, PageContentProps>(
  ({ className, spacing = 'lg', children, ...props }, ref) => {
    const spacingMap = {
      sm: 'py-6 space-y-6',
      md: 'py-8 space-y-8', 
      lg: 'py-12 space-y-12',
      xl: 'py-16 space-y-16'
    };

    return (
      <div
        className={cn(spacingMap[spacing], className)}
        ref={ref}
        {...props}
      >
        {children}
      </div>
    );
  }
);

PageContent.displayName = "PageContent";

export {
  Container,
  Grid,
  Flex,
  Stack,
  Center,
  Spacer,
  Divider,
  PageHeader,
  PageContent,
  containerVariants,
  gridVariants,
  flexVariants
};