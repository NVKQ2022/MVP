using FirstAPIProject.Application.Common.Exceptions;
using FluentValidation;
using Microsoft.AspNetCore.Diagnostics;
using Microsoft.AspNetCore.Mvc;

namespace FirstAPIProject.API.Middlewares
{
    public sealed class GlobalExceptionHandler : IExceptionHandler
    {
        private readonly ILogger<GlobalExceptionHandler> _logger;

        public GlobalExceptionHandler( ILogger<GlobalExceptionHandler> logger )
        {
            _logger = logger;
        }

        public async ValueTask<bool> TryHandleAsync(
            HttpContext httpContext,
            Exception exception,
            CancellationToken cancellationToken )
        {
            _logger.LogError(exception, "An unhandled exception occurred.");

            var (statusCode, title) = exception switch
            {
                UserAlreadyExistsException => (StatusCodes.Status409Conflict, "User already exists"),

                InvalidCredentialsException => (StatusCodes.Status401Unauthorized, "Invalid credentials"),

                InvalidRefreshTokenException => (StatusCodes.Status401Unauthorized, "Invalid refresh token"),

                EmailNotVerifiedException => (StatusCodes.Status403Forbidden, "Email is not verified"),

                EmailNotWhitelistedException => (StatusCodes.Status403Forbidden, "Email not allowed"),

                ValidationException => (StatusCodes.Status400BadRequest, "Validation failed"),

                ArgumentException => (StatusCodes.Status400BadRequest, "Invalid request"),

                ConflictException => (StatusCodes.Status409Conflict, "Conflict"),

                UnauthorizedAccessException => (StatusCodes.Status401Unauthorized, "Unauthorized"),

                NotFoundException => (StatusCodes.Status404NotFound, "Resource not found"),

                _ => (StatusCodes.Status500InternalServerError, "Internal server error")
            };

            var problemDetails = new ProblemDetails
            {
                Status = statusCode,
                Title = title,
                Detail = statusCode == StatusCodes.Status500InternalServerError
                    ? "An unexpected error occurred."
                    : exception.Message,
                Instance = httpContext.Request.Path
            };

            httpContext.Response.StatusCode = statusCode;

            await httpContext.Response.WriteAsJsonAsync(problemDetails, cancellationToken);

            return true;
        }
    }
}
