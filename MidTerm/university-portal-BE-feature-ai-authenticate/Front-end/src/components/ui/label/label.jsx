import * as React from 'react';
import * as LabelPrimitive from '@radix-ui/react-label';
import { cn } from '@/utils/cn';
import './label.scss';

const Label = React.forwardRef(({ className, ...props }, ref) => (
  <LabelPrimitive.Root ref={ref} className={cn('label', className)} {...props} />
));
Label.displayName = LabelPrimitive.Root.displayName;

export { Label };
