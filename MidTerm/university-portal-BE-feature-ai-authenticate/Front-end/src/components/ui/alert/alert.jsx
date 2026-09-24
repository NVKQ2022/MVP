import * as React from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/utils/cn';
import './alert.scss';

const alertVariants = cva('alert', {
  variants: {
    variant: {
      default: 'alert--default',
      destructive: 'alert--destructive',
    },
  },
  defaultVariants: { variant: 'default' },
});

const Alert = React.forwardRef(({ className, variant, ...props }, ref) => (
  <div ref={ref} role="alert" className={cn(alertVariants({ variant }), className)} {...props} />
));
Alert.displayName = 'Alert';

const AlertTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h5 ref={ref} className={cn('alert__title', className)} {...props} />
));
AlertTitle.displayName = 'AlertTitle';

const AlertDescription = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('alert__description', className)} {...props} />
));
AlertDescription.displayName = 'AlertDescription';

export { Alert, AlertTitle, AlertDescription };
