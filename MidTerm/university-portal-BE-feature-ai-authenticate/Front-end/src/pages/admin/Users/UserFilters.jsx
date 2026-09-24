import { Input } from '@/components/ui/input/input';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select/select';

export default function UserFilters({
    search,
    setSearch,
    statusFilter,
    setStatusFilter }) {
    return (
        <div className="admin_userfilter_seachbar">

            <input
                className="admin_userfilter_dropdown"
                placeholder="Search by name or email..."
                onChange={(event) => setSearch(event.target.value)}
            />

            <Select
                value={statusFilter}
                onValueChange={setStatusFilter}
            >
                <SelectTrigger className="admin_userfilter_dropdown">
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