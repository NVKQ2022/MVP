import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table/table';
import { Checkbox } from '@/components/ui/checkbox/checkbox';
import { LoadingState } from '@/components/common/LoadingState';
import { EmptyState } from '@/components/common/EmptyState';
import styles from './DataTable.module.scss';

export function DataTable({
  columns,
  data,
  rowKey = (row) => row.id,
  loading = false,
  actions,
  selectable = false,
  selectedRows,
  onSelectRow,
  onSelectAll,
  emptyMessage = 'No records found',
}) {
  if (loading) return <LoadingState rows={6} />;
  if (!data || data.length === 0) return <EmptyState title={emptyMessage} />;

  const allSelected =
    selectable && data.length > 0 && data.every((row) => selectedRows?.has(rowKey(row)));

  return (
    <div className={styles.dataTable}>
      <Table>
        <TableHeader>
          <TableRow>
            {selectable && (
              <TableHead className={styles.dataTable__checkboxCell}>
                <Checkbox
                  checked={allSelected}
                  onCheckedChange={(checked) => onSelectAll?.(checked)}
                  aria-label="Select all rows"
                />
              </TableHead>
            )}
            {columns.map((col) => (
              <TableHead key={col.key} className={col.className}>
                {col.header}
              </TableHead>
            ))}
            {actions && <TableHead className={styles.dataTable__actionsCell}>Actions</TableHead>}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((row) => {
            const key = rowKey(row);
            return (
              <TableRow key={key}>
                {selectable && (
                  <TableCell>
                    <Checkbox
                      checked={selectedRows?.has(key)}
                      onCheckedChange={(checked) => onSelectRow?.(key, checked)}
                      aria-label="Select row"
                    />
                  </TableCell>
                )}
                {columns.map((col) => (
                  <TableCell key={col.key} className={col.className}>
                    {col.render ? col.render(row) : row[col.key]}
                  </TableCell>
                ))}
                {actions && (
                  <TableCell className={styles.dataTable__actionsCellRight}>
                    {actions(row)}
                  </TableCell>
                )}
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
    </div>
  );
}
