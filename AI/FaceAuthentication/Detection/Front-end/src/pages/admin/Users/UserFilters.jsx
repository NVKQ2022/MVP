import { Input } from '@/components/ui/input/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select/select';

export default function UserFilters({ search, setSearch, statusFilter, setStatusFilter }) {
  return (
    <div className="flex items-center gap-4">
      <Input
        placeholder="Search by name or email..."
        value={search}
        onChange={(event) => setSearch(event.target.value)}
        className="max-w-sm"
      />

      <Select value={statusFilter} onValueChange={setStatusFilter}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Filter by status" />
        </SelectTrigger>

        <SelectContent>
          <SelectItem value="All">All</SelectItem>
          <SelectItem value="active">Active</SelectItem>
          <SelectItem value="locked">Locked</SelectItem>
          <SelectItem value="pending">Pending</SelectItem>
          <SelectItem value="non-active">Non-active</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
}
