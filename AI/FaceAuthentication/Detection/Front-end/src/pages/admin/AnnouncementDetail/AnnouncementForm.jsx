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
  category: z.string().min(1, 'Category is required'),
  author: z.string().min(1, 'Author is required'),
  postedDate: z.string().min(1, 'Posted date is required'),
  priority: z.enum(['low', 'medium', 'high']),
  status: z.enum(['draft', 'published', 'archived']),
  details: z.string().min(1, 'Details are required'),
});

/**
 * @param announcement  Existing announcement object (edit mode). Omit/undefined for create mode.
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
      category: announcement?.category ?? '',
      author: announcement?.author ?? '',
      postedDate: announcement?.postedDate ?? '',
      priority: announcement?.priority ?? 'medium',
      status: announcement?.status ?? 'draft',
      details: announcement?.details ?? '',
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

            <div className="announcement-form__grid-2">
              <Controller
                name="category"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor={`${formId}-category`}>Category</FieldLabel>
                    <Input
                      {...field}
                      id={`${formId}-category`}
                      aria-invalid={fieldState.invalid}
                      placeholder="e.g. Exam, Finance, Event"
                    />
                    {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                  </Field>
                )}
              />

              <Controller
                name="author"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor={`${formId}-author`}>Posted by</FieldLabel>
                    <Input
                      {...field}
                      id={`${formId}-author`}
                      aria-invalid={fieldState.invalid}
                      placeholder="e.g. Academic Affairs Office"
                    />
                    {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                  </Field>
                )}
              />
            </div>

            <div className="announcement-form__grid-3">
              <Controller
                name="postedDate"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor={`${formId}-postedDate`}>Posted date</FieldLabel>
                    <Input
                      {...field}
                      id={`${formId}-postedDate`}
                      type="date"
                      aria-invalid={fieldState.invalid}
                    />
                    {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                  </Field>
                )}
              />

              <Controller
                name="priority"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor={`${formId}-priority`}>Priority</FieldLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <SelectTrigger id={`${formId}-priority`} aria-invalid={fieldState.invalid}>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                    {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                  </Field>
                )}
              />

              <Controller
                name="status"
                control={form.control}
                render={({ field, fieldState }) => (
                  <Field data-invalid={fieldState.invalid}>
                    <FieldLabel htmlFor={`${formId}-status`}>Status</FieldLabel>
                    <Select value={field.value} onValueChange={field.onChange}>
                      <SelectTrigger id={`${formId}-status`} aria-invalid={fieldState.invalid}>
                        <SelectValue placeholder="Select status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="published">Published</SelectItem>
                        <SelectItem value="archived">Archived</SelectItem>
                      </SelectContent>
                    </Select>
                    {fieldState.invalid && <FieldError errors={[fieldState.error]} />}
                  </Field>
                )}
              />
            </div>

            <Controller
              name="details"
              control={form.control}
              render={({ field, fieldState }) => (
                <Field data-invalid={fieldState.invalid}>
                  <FieldLabel htmlFor={`${formId}-details`}>Details</FieldLabel>
                  <Textarea
                    {...field}
                    id={`${formId}-details`}
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
