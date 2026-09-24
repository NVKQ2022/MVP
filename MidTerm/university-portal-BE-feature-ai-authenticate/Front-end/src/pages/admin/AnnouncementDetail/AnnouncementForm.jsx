import * as React from 'react';
import { zodResolver } from '@hookform/resolvers/zod';
import { Controller, useForm } from 'react-hook-form';
import * as z from 'zod';

import { Button } from '@/components/ui/button/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card/card';
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from '@/components/ui/field/field';
import { Input } from '@/components/ui/input/input';
import { Textarea } from '@/components/ui/textarea/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';

const formSchema = z.object({
  title: z.string().min(1, 'Title is required'),
  content: z.string().min(1, 'Content is required'),
  audience: z.enum(['PUBLIC', 'STUDENT']),
});

/**
 * @param announcement  Existing announcement object (edit mode) — { id, title, content, audience }. Omit/undefined for create mode.
 * @param onSubmit       (values) => void — values include `id` when editing
 * @param onCancel       optional () => void — renders a Cancel button when provided
 * @param submitting     boolean — disables the submit button while a save is in flight
 */
const AnnouncementForm = ({ announcement, onSubmit, onCancel, submitting = false }) => {
  const isEditMode = Boolean(announcement);
  const formId = 'announcement-form';

  const form = useForm({
    resolver: zodResolver(formSchema),
    defaultValues: {
      title: announcement?.title ?? '',
      content: announcement?.content ?? '',
      audience: announcement?.audience ?? 'PUBLIC',
    },
  });

  const handleSubmit = (values) => {
    const payload = isEditMode ? { id: announcement.id, ...values } : values;
    if (onSubmit) {
      onSubmit(payload);
    } else {
      console.log(isEditMode ? 'update announcement' : 'create announcement', payload);
    }
  };

  return (
    <Card className="announcement-form">
      <CardHeader>
        <CardTitle>{isEditMode ? 'Update Announcement' : 'Create Announcement'}</CardTitle>
        <CardDescription>
          {isEditMode
            ? 'Edit the fields below and save your changes.'
            : 'Fill in the fields below to publish a new announcement.'}
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form id={formId} onSubmit={form.handleSubmit(handleSubmit)}>
          <FieldGroup>
            <Controller
              name="title"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor={`${formId}-title`}>Title</FieldLabel>
                  <Input
                    {...field}
                    id={`${formId}-title`}
                    aria-invalid={fieldState.invalid}
                    placeholder="Announcement title"
                    autoComplete="off"
                  />
                  {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                </Field>
              )}
            />

            <Controller
              name="audience"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor={`${formId}-audience`}>Audience</FieldLabel>
                  <Select value={field.value} onValueChange={field.onChange}>
                    <SelectTrigger
                      id={`${formId}-audience`}
                      aria-invalid={fieldState.invalid}
                      className="announcement-form__audience-trigger"
                    >
                      <SelectValue placeholder="Select audience" />
                    </SelectTrigger>
                    <SelectContent className="announcement-form__audience-content">
                      <SelectItem value="PUBLIC">Public</SelectItem>
                      <SelectItem value="STUDENT">Student</SelectItem>
                    </SelectContent>
                  </Select>
                  {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                </Field>
              )}
            />

            <Controller
              name="content"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor={`${formId}-content`}>Content</FieldLabel>
                  <Textarea
                    {...field}
                    id={`${formId}-content`}
                    aria-invalid={fieldState.invalid}
                    placeholder="Full announcement content..."
                    className="announcement-form__details-textarea"
                  />
                  <FieldDescription>
                    This is the full body of the announcement. It is not shown as a table column.
                  </FieldDescription>
                  {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                </Field>
              )}
            />
          </FieldGroup>
        </form>
      </CardContent>

      <CardFooter>
        <Field orientation="horizontal">
          {onCancel && (
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          )}
          <Button type="button" variant="outline" onClick={() => form.reset()}>
            Reset
          </Button>
          <Button type="submit" form={formId} disabled={submitting}>
            {isEditMode ? 'Update' : 'Create'}
          </Button>
        </Field>
      </CardFooter>
    </Card>
  );
};

export default AnnouncementForm;