import { Badge } from '@/components/ui/badge/badge';
import { Card, CardContent } from '@/components/ui/card/card';

export default function UserHeader({ user }) {
    return (
        <Card>
            <CardContent className="admin_userdetail_header_wrapper">
                <div className="admin_userdetail_header_first_row">
                    <div>
                        <h1 className="admin_userdetail_header_first_row_name">
                            {user.name}
                        </h1>

                        <p className="admin_userdetail_header_first_row_email">
                            {user.email}
                        </p>
                    </div>

                    <Badge
                        variant={
                            user.status === 'Active'
                                ? 'default'
                                : 'secondary'
                        }
                    >
                        {user.status}
                    </Badge>
                </div>

                <p className="admin_userdetail_header_first_row_userid">
                    User ID: {user.id}
                </p>
            </CardContent>
        </Card>
    );
}