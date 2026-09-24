import { Outlet } from 'react-router-dom';
import { StudentHeader } from '@/components/layout/student/StudentHeader';
import { StudentFooter } from '@/components/layout/student/StudentFooter';
import styles from './StudentLayout.module.scss';

export default function StudentLayout() {
  return (
    <div className={styles.studentLayout}>
      <StudentHeader />
      <main className={styles.studentLayout__main}>
        <div className={styles.studentLayout__container}>
          <Outlet />
        </div>
      </main>
      <StudentFooter />
    </div>
  );
}
