using Asp.Versioning;
using DotNetEnv;
using FirstAPIProject.API.Extensions;
using FirstAPIProject.API.Middlewares;
using FirstAPIProject.API.Services;
using FirstAPIProject.Application;
using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Infrastructure;
using FirstAPIProject.Infrastructure.Authentication;
using FirstAPIProject.Infrastructure.FaceRecognition.Configurations;
using FirstAPIProject.Infrastructure.Persistence;
using FirstAPIProject.Infrastructure.VectorDb.Configurations;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.RateLimiting;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi;
using System.Text;
using System.Threading.RateLimiting;
using Microsoft.Data.SqlClient;


namespace FirstAPIProject
{
    public class Program
    {
        public static async Task Main( string[] args )
        {
            // DOCKER MIGRATION: REMOVE DotNetEnv.Env.Load()
            var environment = Environment.GetEnvironmentVariable("ASPNETCORE_ENVIRONMENT") ?? "Development";

            var envFile = environment switch
            {
                "Production" => ".env.production",
                _ => ".env.development"
            };

            Env.Load(envFile);

            // This initializes the application configuration, logging, dependency injection (DI) container, and web server settings.
            var builder = WebApplication.CreateBuilder(args);

            // Apply CORS
            var allowedOrigins = builder.Configuration
                .GetSection("Cors:AllowedOrigins")
                .Get<string[]>() ?? [];

            builder.Services.AddCors(options =>
            {
                options.AddPolicy("FrontendPolicy", policy =>
                {
                    policy
                        .WithOrigins(allowedOrigins)
                        .AllowAnyHeader()
                        .AllowAnyMethod()
                        .AllowCredentials();
                });
            });

            // Configure ASP.NET Core rate limiting.
            builder.Services.AddRateLimiter(options =>
            {
                // Global rate limit
                options.GlobalLimiter =
                    PartitionedRateLimiter.Create<HttpContext, string>(
                        context =>
                        {
                            var ip =
                                context.Connection.RemoteIpAddress?.ToString()
                                ?? "unknown";

                            return RateLimitPartition
                                .GetFixedWindowLimiter(
                                    ip,
                                    _ => new FixedWindowRateLimiterOptions
                                    {
                                        PermitLimit = 100,
                                        Window = TimeSpan.FromMinutes(1),
                                        QueueLimit = 0
                                    });
                        });

                // Return HTTP 429 when the request is rejected.
                options.OnRejected = async ( context, cancellationToken ) =>
                {
                    context.HttpContext.Response.StatusCode =
                        StatusCodes.Status429TooManyRequests;

                    await context.HttpContext.Response.WriteAsJsonAsync(
                        new
                        {
                            status = 429,
                            title = "Too Many Requests",
                            detail = "Too many requests. Please try again later."
                        },
                        cancellationToken);
                };

                // Authentication policy.
                options.AddFixedWindowLimiter("auth", limiterOptions =>
                {
                    limiterOptions.PermitLimit = 5;
                    limiterOptions.Window = TimeSpan.FromMinutes(1);
                    limiterOptions.QueueLimit = 0;
                });

                options.AddFixedWindowLimiter("announcement", limiterOptions =>
                {
                    limiterOptions.PermitLimit = 100;
                    limiterOptions.Window = TimeSpan.FromMinutes(1);
                    limiterOptions.QueueLimit = 0;
                });
            });

            // Read JWT configuration from appsettings.json.
            var jwtSettings = builder.Configuration
                .GetSection(JwtSettings.SectionName)
                .Get<JwtSettings>()
                ?? throw new InvalidOperationException("JWT settings are not configured.");

            // Register JwtSettings with the DI container.
            builder.Services
                .AddOptions<JwtSettings>()
                .Bind(builder.Configuration.GetSection(
                    JwtSettings.SectionName))
                .Validate(
                    settings => !string.IsNullOrWhiteSpace(settings.SecretKey), "JWT SecretKey must be configured.")
                .ValidateOnStart();

            // Register RefreshTokenSettings with th DI container
            builder.Services
                .AddOptions<RefreshTokenSettings>()
                .Bind(builder.Configuration.GetSection(
                    RefreshTokenSettings.SectionName))
                .Validate(
                    settings => settings.ExpirationDays > 0,
                    "Refresh token expiration must be greater than 0.")
                .ValidateOnStart();

            // Register MVC Controllers into the DI container.
            builder.Services
                .AddControllers()
                .AddJsonOptions(options =>
                {
                    options.JsonSerializerOptions.Converters.Add(new System.Text.Json.Serialization.JsonStringEnumConverter());
                });

            // Register API Version
            builder.Services
                .AddApiVersioning(options =>
                {
                    options.DefaultApiVersion = new ApiVersion(1, 0);

                    options.AssumeDefaultVersionWhenUnspecified = true;

                    options.ReportApiVersions = true;

                    options.ApiVersionReader =
                        new UrlSegmentApiVersionReader();
                })
                .AddApiExplorer(options =>
                {
                    options.GroupNameFormat = "'v'VVV";

                    options.SubstituteApiVersionInUrl = true;
                });

            // Register API Explorer services.
            builder.Services.AddEndpointsApiExplorer();

            // Register Swagger/OpenAPI document generation.
            builder.Services.AddSwaggerGen(options =>
            {
                options.AddSecurityDefinition(
                    "Bearer",
                    new OpenApiSecurityScheme
                    {
                        Name = "Authorization",
                        Type = SecuritySchemeType.Http,
                        Scheme = "bearer",
                        BearerFormat = "JWT",
                        In = ParameterLocation.Header,
                        Description =
                            "Enter your JWT token.\r\n\r\n" +
                            "Example: Bearer eyJhbGciOiJIUzI1NiIs..."
                    });

                options.AddSecurityRequirement(document =>
                    new Microsoft.OpenApi.OpenApiSecurityRequirement
                    {
                        {
                            new Microsoft.OpenApi.OpenApiSecuritySchemeReference(
                                "Bearer",
                                document),
                            []
                        }
                    });

                options.SwaggerDoc(
                    "v1",
                    new OpenApiInfo
                    {
                        Title = "First API Project",
                        Version = "v1"
                    });
            });

            // Register the global exception handler.
            builder.Services.AddExceptionHandler<GlobalExceptionHandler>();

            // Enable RFC 7807 ProblemDetails responses.
            builder.Services.AddProblemDetails();

            // Add Infrastructure and Application
            builder.Services.AddApplication();

            builder.Services.AddInfrastructure(builder.Configuration);

            // Add FaceRecognition 3rd configuration
            builder.Services.AddFaceRecognition(builder.Configuration);
            // Add VectorDb configuration
            builder.Services.AddVectorDb(builder.Configuration);


            // Register JWT Bearer authentication.
            builder.Services
                .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
                .AddJwtBearer(options =>
                {
                    options.TokenValidationParameters =
                        new TokenValidationParameters
                        {
                            // Validate the issuer inside the JWT.
                            ValidateIssuer = true,

                            // Validate the audience inside the JWT.
                            ValidateAudience = true,

                            // Validate token expiration.
                            ValidateLifetime = true,

                            // Validate the signature using the secret key.
                            ValidateIssuerSigningKey = true,


                            // Expected issuer.
                            ValidIssuer = jwtSettings.Issuer,

                            // Expected audience.
                            ValidAudience = jwtSettings.Audience,


                            // Secret key used to verify the JWT signature.
                            IssuerSigningKey =
                                new SymmetricSecurityKey(
                                    Encoding.UTF8.GetBytes(
                                        jwtSettings.SecretKey))
                        };
                });

            builder.Services.AddHttpContextAccessor();

            builder.Services.AddScoped<ICurrentUserService, CurrentUserService>();

            // Build the WebApplication using all registered services and application configuration.
            var app = builder.Build();

            app.Logger.LogInformation("Current environment: {Environment}", app.Environment.EnvironmentName);


            // DEVELOPMENT ONLY
            // TODO: Replace EnsureDeletedAsync + EnsureCreatedAsync
            // with EF Core Migrations before Production/Docker deployment.
            if (app.Environment.IsDevelopment())
            {
                using var scope = app.Services.CreateScope();

                var dbContext = scope.ServiceProvider.GetRequiredService<AppDbContext>();

                await dbContext.Database.MigrateAsync();

                app.Logger.LogInformation("Database migrations applied.");
            }


            // Global exception handler.
            app.UseExceptionHandler();

            // Apply CORS early before rate limiting, redirection, or auth
            app.UseCors("FrontendPolicy");

            // Rate limiting.
            app.UseRateLimiter();

            // Performance logging middleware.
            app.UsePerformanceLogging();

            // app.UseMiddleware<PerformanceLoggingMiddleware>

            if (app.Environment.IsDevelopment())
            {
                // Enable Swagger middleware.
                app.UseSwagger();

                // Enable Swagger UI.
                app.UseSwaggerUI();
            }

            if (!app.Environment.IsDevelopment())
            {
                // Redirect HTTP requests to HTTPS only in production
                app.UseHttpsRedirection();
            }

            // Authenticate the current request.
            app.UseAuthentication();

            // Enable authorization middleware.
            app.UseAuthorization();

            // Map Controller routes to the HTTP request pipeline.
            app.MapControllers();

            //seed admin

            using (var scope = app.Services.CreateScope())
            {
                var dbContext = scope.ServiceProvider.GetRequiredService<AppDbContext>();

                var passwordService =
                    scope.ServiceProvider.GetRequiredService<IPasswordService>();

                await DatabaseSeeder.SeedAsync(
                    dbContext,
                    passwordService);
            }

            // Start the ASP.NET Core application and begin listening for HTTP requests.
            app.Run();
        }
    }
}
