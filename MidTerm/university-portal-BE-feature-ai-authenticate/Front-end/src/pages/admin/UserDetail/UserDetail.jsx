import {
  useParams,
  useNavigate,
} from 'react-router-dom';

import { Badge } from '@/components/ui/badge/badge';
import { Button } from '@/components/ui/button/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card/card';
import { mockUsers, checkUserPassword, getUserByEmail, getUserById } from '@/features/users/mock-data';
import AdminActions from './UserActions';
import UserHeader from './UserHeader';
import DetailInformation from './UserInformation';

function BackButton() {
  const navigate = useNavigate();

  return (
    <button className='admin_userdetail_back_button'
      onClick={() => navigate(-1)}>
      ← Back
    </button>
  );
}

export default function AdminUserDetail() {
  const { id: userId } = useParams();
  const navigate = useNavigate();

  const user = getUserById(userId);

  if (!user) {
    return (
      <div className="admin_userdetail_wrapper">
        <BackButton />

        <Card>
          <CardContent className="admin_userdetail_header_wrapper">
            <div className="admin_userdetail_header_first_row">
              <div>
                <h1 className="admin_userdetail_header_first_row_name">
                  Invalid name
                </h1>

                <p className="admin_userdetail_header_first_row_email">
                  invalid.email@example.com
                </p>
              </div>
            </div>
            <p className="admin_userdetail_header_first_row_userid">
              No user with ID: {userId}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="admin_userdetail_wrapper">
      <BackButton />

      <UserHeader user={user} />
      <DetailInformation user={user} />
      <AdminActions user={user} />
    </div>
  );
}