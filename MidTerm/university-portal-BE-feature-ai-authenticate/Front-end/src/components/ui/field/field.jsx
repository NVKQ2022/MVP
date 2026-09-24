import * as React from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/utils/cn';
import { Label } from '@/components/ui/label/label';
import './field.scss';
function FieldGroup({ className, ...props }) {
  return <div data-slot="field-group" className={cn('field-group', className)} {...props} />;
}
const fieldVariants = cva('field', {
  variants: { orientation: { vertical: 'field--vertical', horizontal: 'field--horizontal' } },
  defaultVariants: { orientation: 'vertical' },
});
function Field({ className, orientation = 'vertical', ...props }) {
  return (
    <div
      role="group"
      data-slot="field"
      data-orientation={orientation}
      className={cn(fieldVariants({ orientation }), className)}
      {...props}
    />
  );
}
function FieldLabel({ className, ...props }) {
  return <Label data-slot="field-label" className={cn('field-label', className)} {...props} />;
}
function FieldDescription({ className, ...props }) {
  return (
    <p data-slot="field-description" className={cn('field-description', className)} {...props} />
  );
}
function FieldError({ className, children, errors, ...props }) {
  const content = React.useMemo(() => {
    if (children) {
      return children;
    }
    if (!errors) {
      return null;
    }
    if (errors?.length === 1 && errors[0]?.message) {
      return errors[0].message;
    }
    return (
      <ul className="field-error__list">
        {' '}
        {errors.map((error, index) => error?.message && <li key={index}>{error.message}</li>)}{' '}
      </ul>
    );
  }, [children, errors]);
  if (!content) {
    return null;
  }
  return (
    <div role="alert" data-slot="field-error" className={cn('field-error', className)} {...props}>
      {' '}
      {content}{' '}
    </div>
  );
}
export { Field, FieldGroup, FieldLabel, FieldDescription, FieldError };
