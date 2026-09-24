import { Badge } from '@/components/ui/badge/badge';
import {
    Card,
    CardContent,
    CardHeader,
    CardTitle,
} from '@/components/ui/card/card';

export default function DetailInformation({ user }) {
    return (
        <Card>
            <CardHeader>
                <CardTitle>Detail information</CardTitle>
            </CardHeader>

            <CardContent>
                <div className="admin_userdetail_wrapper">

                    <div>
                        <p className="admin_userdetail_label">
                            User ID
                        </p>
                        <p className="admin_userdetail_value">
                            {user.id}
                        </p>
                    </div>

                    <div>
                        <p className="admin_userdetail_label">
                            Name
                        </p>
                        <p className="admin_userdetail_value">
                            {user.name}
                        </p>
                    </div>

                    <div>
                        <p className="admin_userdetail_label">
                            Email
                        </p>
                        <p className="admin_userdetail_value">
                            {user.email}
                        </p>
                    </div>



                    <div>
                        <p className="admin_userdetail_label">
                            Status
                        </p>

                        <div className="admin_userdetail_value_badge">
                            <Badge
                                variant={
                                    user.status === 'active'
                                        ? 'default'
                                        : 'secondary'
                                }
                            >
                                {user.status}
                            </Badge>
                        </div>
                    </div>

                    <div>
                        <p className="admin_userdetail_label">
                            Created at
                        </p>
                        <p className="admin_userdetail_value">
                            {user.createdAt}
                        </p>
                    </div>

                    <div>
                        <p className="admin_userdetail_label">
                            Role
                        </p>
                        <p className="admin_userdetail_value">
                            {user.role}
                        </p>
                    </div>

                </div>
            </CardContent>
        </Card>
    );
}