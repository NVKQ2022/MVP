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
        <div className="admin_users_pagination_wrapper">
            <Select
                value={String(usersPerPage)}
                onValueChange={(value) => {
                    setUsersPerPage(Number(value));
                    setCurrentPage(1);
                }}
            >
                <SelectTrigger className="admin_users_pagination_trigger">
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

            <button
                className="admin_userdetail_back_button"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((page) => page - 1)}
            >
                Prev
            </button>

            <p className="admin_users_pagecount">
                Page {currentPage} / {totalPages}
            </p>

            <button
                className="admin_userdetail_back_button"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((page) => page + 1)}
            >
                Next
            </button>
        </div>
    );
}