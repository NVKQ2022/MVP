import * as React from 'react';
import { ChevronLeft, ChevronRight, MoreHorizontal } from 'lucide-react';
import { cn } from '@/utils/cn';
import { Button, buttonVariants } from '@/components/ui/button/button';
import './pagination.scss';

const Pagination = ({ className, ...props }) => (
  <nav
    role="navigation"
    aria-label="pagination"
    className={cn('pagination', className)}
    {...props}
  />
);

const PaginationContent = React.forwardRef(({ className, ...props }, ref) => (
  <ul ref={ref} className={cn('pagination__list', className)} {...props} />
));

const PaginationItem = React.forwardRef(({ className, ...props }, ref) => (
  <li ref={ref} className={className} {...props} />
));

const PaginationLink = ({ className, isActive, size = 'icon', ...props }) => (
  <Button
    aria-current={isActive ? 'page' : undefined}
    className={cn(
      buttonVariants({ variant: isActive ? 'outline' : 'ghost', size }),
      'pagination__link',
      className,
    )}
    {...props}
  />
);

const PaginationPrevious = ({ className, ...props }) => (
  <PaginationLink
    aria-label="Go to previous page"
    size="default"
    className={cn('pagination__nav', className)}
    {...props}
  >
    <ChevronLeft size={16} />
    <span>Previous</span>
  </PaginationLink>
);

const PaginationNext = ({ className, ...props }) => (
  <PaginationLink
    aria-label="Go to next page"
    size="default"
    className={cn('pagination__nav', className)}
    {...props}
  >
    <span>Next</span>
    <ChevronRight size={16} />
  </PaginationLink>
);

const PaginationEllipsis = ({ className, ...props }) => (
  <span aria-hidden className={cn('pagination__ellipsis', className)} {...props}>
    <MoreHorizontal size={16} />
    <span className="visually-hidden">More pages</span>
  </span>
);

export {
  Pagination,
  PaginationContent,
  PaginationLink,
  PaginationItem,
  PaginationPrevious,
  PaginationNext,
  PaginationEllipsis,
};
