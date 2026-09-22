import * as React from 'react';
import { cn } from '@/utils/cn';
import './textarea.scss';

const Textarea = React.forwardRef(({ className, ...props }, ref) => (
  <textarea className={cn('textarea', className)} ref={ref} {...props} />
));
Textarea.displayName = 'Textarea';

export { Textarea };
