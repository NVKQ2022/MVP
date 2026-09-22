import { Outlet } from 'react-router-dom';
import { AdminSidebar } from '@/components/layout/admin/AdminSidebar';
import { AdminHeader } from '@/components/layout/admin/AdminHeader';
import styles from './AdminLayout.module.scss';

export default function AdminLayout() {
  return (
    <div className="flex min-h-screen">
      <AdminSidebar className="hidden lg:flex h-auto" />
      <div className="flex flex-1 flex-col">
        <AdminHeader />
        <main className={styles.adminLayout__main}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
