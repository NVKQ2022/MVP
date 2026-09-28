import { useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import { AdminSidebar } from '@/components/layout/admin/AdminSidebar';
import { AdminHeader } from '@/components/layout/admin/AdminHeader';
import styles from './AdminLayout.module.scss';

export default function AdminLayout() {
  useEffect(() => {
    document.body.classList.add('body--locked');
    return () => document.body.classList.remove('body--locked');
  }, []);

  return (
    <div className={styles.adminLayout}>
      <AdminSidebar className={styles.adminLayout__sidebar} />
      <div className={styles.adminLayout__body}>
        <AdminHeader />
        <main className={styles.adminLayout__main}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}