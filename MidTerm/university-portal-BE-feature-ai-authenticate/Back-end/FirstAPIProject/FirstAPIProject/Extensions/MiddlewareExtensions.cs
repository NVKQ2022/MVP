using FirstAPIProject.API.Middlewares;

namespace FirstAPIProject.API.Extensions
{
    public static class MiddlewareExtensions
    {
        public static IApplicationBuilder UsePerformanceLogging(this IApplicationBuilder app)
        {
            return app.UseMiddleware<PerformanceLoggingMiddleware>();
        }
    }
}
