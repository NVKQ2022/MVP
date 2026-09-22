import * as React from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/utils/cn';
import './badge.scss';

const badgeVariants = cva('badge', {
  variants: {
    variant: {
      default: 'badge--default',
      secondary: 'badge--secondary',
      destructive: 'badge--destructive',
      outline: 'badge--outline',
    },
  },
  defaultVariants: { variant: 'default' },
});

function Badge({ className, variant, ...props }) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
