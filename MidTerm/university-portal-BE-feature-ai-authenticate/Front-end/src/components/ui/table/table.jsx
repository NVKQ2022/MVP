import * as React from 'react';
import { cn } from '@/utils/cn';
import './table.scss';

const Table = React.forwardRef(({ className, ...props }, ref) => (
  <div className="table-wrapper">
    <table ref={ref} className={cn('table', className)} {...props} />
  </div>
));
Table.displayName = 'Table';

const TableHeader = React.forwardRef(({ className, ...props }, ref) => (
  <thead ref={ref} className={cn('table__header', className)} {...props} />
));
const TableBody = React.forwardRef(({ className, ...props }, ref) => (
  <tbody ref={ref} className={cn('table__body', className)} {...props} />
));
const TableFooter = React.forwardRef(({ className, ...props }, ref) => (
  <tfoot ref={ref} className={cn('table__footer', className)} {...props} />
));
const TableRow = React.forwardRef(({ className, ...props }, ref) => (
  <tr ref={ref} className={cn('table__row', className)} {...props} />
));
const TableHead = React.forwardRef(({ className, ...props }, ref) => (
  <th ref={ref} className={cn('table__head', className)} {...props} />
));
const TableCell = React.forwardRef(({ className, ...props }, ref) => (
  <td ref={ref} className={cn('table__cell', className)} {...props} />
));
const TableCaption = React.forwardRef(({ className, ...props }, ref) => (
  <caption ref={ref} className={cn('table__caption', className)} {...props} />
));

export { Table, TableHeader, TableBody, TableFooter, TableHead, TableRow, TableCell, TableCaption };
