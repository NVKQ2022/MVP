using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Modules.Announcement.Interfaces;
using FirstAPIProject.Application.Modules.AnnouncementRead.Interfaces;
using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Application.Modules.User.Interfaces;
using FirstAPIProject.Application.Modules.Whitelist.Interfaces;
using FirstAPIProject.Infrastructure.Authentication;
using FirstAPIProject.Infrastructure.FaceRecognition.Clients;
using FirstAPIProject.Infrastructure.Persistence;
using FirstAPIProject.Infrastructure.Persistence.Interceptors;
using FirstAPIProject.Infrastructure.Persistence.Repositories;
using FirstAPIProject.Infrastructure.Services;
using FirstAPIProject.Infrastructure.VectorDb.Clients;
using FirstAPIProject.Infrastructure.VectorDb.Models;
using FirstAPIProject.Infrastructure.VectorDb.Repositories;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace FirstAPIProject.Infrastructure
{
    public static class DependencyInjection
    {
        public static IServiceCollection AddInfrastructure( this IServiceCollection services, IConfiguration configuration )
        {
            services.AddScoped<AuditableEntityInterceptor>();
            services.AddDbContext<AppDbContext>(
                ( provider, options ) =>
                {
                    options.UseSqlServer(configuration.GetConnectionString("DefaultConnection"));
                    options.AddInterceptors(provider.GetRequiredService<AuditableEntityInterceptor>());
                });

            // Generic Repository
            services.AddScoped(typeof(IGenericRepository<>), typeof(GenericRepository<>));

            // Repositories
            services.AddScoped<IUserRepository, UserRepository>();
            services.AddScoped<IRoleRepository, RoleRepository>();
            services.AddScoped<IRefreshTokenRepository, RefreshTokenRepository>();
            services.AddScoped<IAnnouncementRepository, AnnouncementRepository>();
            services.AddScoped<IOtpVerificationRepository, OtpVerificationRepository>();
            services.AddScoped<IEmailWhitelistRepository, EmailWhitelistRepository>();
            services.AddScoped<IAnnouncementReadRepository, AnnouncementReadRepository>();

            // Repository (VectorDb)
            services.AddScoped<IFaceEmbeddingRepository, FaceEmbeddingRepository>();
            services.AddScoped<IVectorSearchClient, QdrantVectorSearchClient>();
            services.Configure<VectorDbOptions>(configuration.GetSection("VectorDb"));
            services.AddSingleton<Qdrant.Client.QdrantClient>(sp =>
            {
                var options =
                    sp.GetRequiredService<
                        IOptions<VectorDbOptions>>();

                return new Qdrant.Client.QdrantClient(
                    host: options.Value.Host,
                    port: options.Value.Port);
            });
            // Face recognition client
            services.AddScoped<IFaceRecognitionClient, FaceRecognitionClient>();

            // Authentication services
            services.AddScoped<IJwtService, JwtService>();
            services.AddScoped<IPasswordService, PasswordService>();
            services.AddScoped<IRefreshTokenService, RefreshTokenService>();


            //User profile services
            services.AddScoped<IFileStorageService, LocalFileStorageService>();

            // Email services
            services.AddScoped<IEmailService, FakeEmailService>();
            services.AddScoped<IOtpService, OtpService>();

            // Unit of Work
            services.AddScoped<IUnitOfWork, UnitOfWork>();

            return services;
        }
    }
}
