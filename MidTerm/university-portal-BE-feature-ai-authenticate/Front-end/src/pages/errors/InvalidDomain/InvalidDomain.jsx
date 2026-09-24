export default function InvalidDomain() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-2 bg-background text-center">
      <h1 className="text-xl font-semibold">Invalid Domain</h1>
      <p className="text-sm text-muted-foreground">
        This host is not recognized by the application.
      </p>
    </div>
  );
}
