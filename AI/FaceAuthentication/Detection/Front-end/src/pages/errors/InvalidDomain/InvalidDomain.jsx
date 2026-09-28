import styles from './InvalidDomain.module.scss';

export default function InvalidDomain() {
  return (
    <div className={styles.invalidDomain}>
      <h1 className={styles.invalidDomain__title}>Invalid Domain</h1>
      <p className={styles.invalidDomain__description}>
        This host is not recognized by the application.
      </p>
    </div>
  );
}