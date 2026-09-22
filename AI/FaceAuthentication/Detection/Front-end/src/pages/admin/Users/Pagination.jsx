import { Button } from '@/components/ui/button/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';

export default function Pagination({
  currentPage,
  totalPages,
  usersPerPage,
  setCurrentPage,
  setUsersPerPage,
}) {
  return (
    <div className="flex items-center justify-center gap-4">
      <Select
        value={String(usersPerPage)}
        onValueChange={(value) => {
          setUsersPerPage(Number(value));
          setCurrentPage(1);
        }}
      >
        <SelectTrigger className="w-[100px]">
          <SelectValue />
        </SelectTrigger>

        <SelectContent>
          <SelectItem value="5">5</SelectItem>
          <SelectItem value="10">10</SelectItem>
          <SelectItem value="25">25</SelectItem>
          <SelectItem value="50">50</SelectItem>
          <SelectItem value="100">100</SelectItem>
        </SelectContent>
      </Select>

      <Button
        variant="outline"
        size="sm"
        disabled={currentPage === 1}
        onClick={() => setCurrentPage((page) => page - 1)}
      >
        Prev
      </Button>

      <p className="text-sm text-muted-foreground">
        Page {currentPage} / {totalPages}
      </p>

      <Button
        variant="outline"
        size="sm"
        disabled={currentPage === totalPages}
        onClick={() => setCurrentPage((page) => page + 1)}
      >
        Next
      </Button>
    </div>
  );
}
