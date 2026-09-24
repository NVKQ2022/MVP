using System.Diagnostics;

namespace FirstAPIProject.API.Middlewares
{
    public sealed class PerformanceLoggingMiddleware
    {
        private readonly RequestDelegate _next;
        private readonly ILogger<PerformanceLoggingMiddleware> _logger;

        public PerformanceLoggingMiddleware(RequestDelegate next, ILogger<PerformanceLoggingMiddleware> logger)
        {
            _next = next;
            _logger = logger;
        }

        public async Task InvokeAsync(HttpContext context)
        {
            // Start measuring the request processing time.
            var stopwatch = Stopwatch.StartNew();

            context.Response.OnStarting(() =>
            {
                stopwatch.Stop();

                var elapsedMilliseconds = stopwatch.Elapsed.TotalMilliseconds;

                // Add performance information to response header
                context.Response.Headers["X-Response-Time-ms"] = elapsedMilliseconds.ToString("F2");

                // Log performance information
                _logger.LogInformation(
                    "HTTP {Method} {Path} responded {StatusCode} in {ElapsedMilliseconds} ms",
                    context.Request.Method,
                    context.Request.Path,
                    context.Response.StatusCode,
                    elapsedMilliseconds);

                return Task.CompletedTask;
            });

            await _next(context);
        }
    }
}
