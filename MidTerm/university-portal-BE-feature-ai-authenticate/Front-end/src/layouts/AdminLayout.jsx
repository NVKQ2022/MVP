import { Outlet } from 'react-router-dom';
import { AdminSidebar } from '@/components/layout/admin/AdminSidebar';
import { AdminHeader } from '@/components/layout/admin/AdminHeader';
import styles from './AdminLayout.module.scss';

export default function AdminLayout() {
  return (
    <div className={styles.adminLayout}>
      <div className={styles.adminLayout__sidebar}>
        <AdminSidebar />
      </div>
      <div className={styles.adminLayout__body}>
        <AdminHeader />
        <main className={styles.adminLayout__main}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}