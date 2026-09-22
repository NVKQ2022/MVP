import styles from './PageHeader.module.scss';

export function PageHeader({ title, description, breadcrumb, actions }) {
  return (
    <div className={styles.pageHeader}>
      <div className={styles.pageHeader__content}>
        {breadcrumb && <div className={styles.pageHeader__breadcrumb}>{breadcrumb}</div>}
        <h2 className={styles.pageHeader__title}>{title}</h2>
        {description && <p className={styles.pageHeader__description}>{description}</p>}
      </div>
      {actions && <div className={styles.pageHeader__actions}>{actions}</div>}
    </div>
  );
}
