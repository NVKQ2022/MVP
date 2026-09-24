using FirstAPIProject.Application.Modules.Announcement.DTOs;
using FirstAPIProject.Application.Modules.Announcement.Interfaces;
using FirstAPIProject.Application.Modules.Announcement.Services;
using FirstAPIProject.Application.Modules.Announcement.Validators;
using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Application.Modules.Auth.Services;
using FirstAPIProject.Application.Modules.User.DTOs;
using FirstAPIProject.Application.Modules.User.Interfaces;
using FirstAPIProject.Application.Modules.User.Services;
using FirstAPIProject.Application.Modules.User.Validators;
using FirstAPIProject.Application.Modules.Whitelist.DTOs;
using FirstAPIProject.Application.Modules.Whitelist.Interfaces;
using FirstAPIProject.Application.Modules.Whitelist.Services;
using FirstAPIProject.Application.Modules.Whitelist.Validators;
using FluentValidation;
using Microsoft.Extensions.DependencyInjection;

namespace FirstAPIProject.Application
{
    public static class DependencyInjection
    {
        public static IServiceCollection AddApplication( this IServiceCollection services )
        {
            // FluentValidation
            services.AddScoped<IValidator<UpdateProfileRequest>, UpdateProfileRequestValidator>();
            services.AddScoped<IValidator<AdminUserFilterRequest>, AdminUserFilterRequestValidator>();
            services.AddScoped<IValidator<AdminUpdateUserRequest>, AdminUpdateUserRequestValidator>();
            services.AddScoped<IValidator<WhitelistFilterRequest>, WhitelistFilterRequestValidator>();
            services.AddScoped<IValidator<CreateWhitelistRequest>, CreateWhitelistRequestValidator>();
            services.AddScoped<IValidator<UpdateWhitelistRequest>, UpdateWhitelistRequestValidator>();

            // Announcement validators
            services.AddScoped<IValidator<AnnouncementQueryRequest>, AnnouncementQueryRequestValidator>();

            services.AddScoped<IValidator<CreateAnnouncementRequest>, CreateAnnouncementRequestValidator>();

            services.AddScoped<IValidator<UpdateAnnouncementRequest>, UpdateAnnouncementRequestValidator>();

            // Application Services
            services.AddScoped<IAuthService, AuthService>();
            services.AddScoped<IUserProfileService, UserProfileService>();
            services.AddScoped<IAdminUserService, AdminUserService>();
            services.AddScoped<IAnnouncementManagementService, AnnouncementManagementService>();
            services.AddScoped<IAnnouncementQueryService, AnnouncementQueryService>();
            services.AddScoped<IEmailWhitelistService, EmailWhitelistService>();
            //services.AddScoped<IFaceEmbeddingRepository, FaceEmbeddingRepository>();
            services.AddScoped<IFaceRegistrationService, FaceRegistrationService>();
            services.AddScoped<IFaceAuthenticateService, FaceAuthenticateService>();
            services.AddScoped<IAnnouncementReadService, AnnouncementReadService>();
            return services;
        }
    }
}
