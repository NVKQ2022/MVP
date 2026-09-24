using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Infrastructure.FaceRecognition.Clients;
using FirstAPIProject.Infrastructure.FaceRecognition.Models;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Options;

namespace FirstAPIProject.Infrastructure.FaceRecognition.Configurations
{
    public static class FaceRecognitionConfiguration
    {
        public static IServiceCollection AddFaceRecognition(
            this IServiceCollection services,
            IConfiguration configuration)
        {
            services.Configure<FaceRecognitionOptions>(
                configuration.GetSection("FaceRecognition"));

            services.AddHttpClient<
                IFaceRecognitionClient,
                FaceRecognitionClient>((sp, client) =>
                {
                    var options =
                        sp.GetRequiredService<
                            IOptions<FaceRecognitionOptions>>();

                    var baseUrl = string.IsNullOrWhiteSpace(options.Value.BaseUrl)
                        ? "http://localhost:8000"
                        : options.Value.BaseUrl;

                    client.BaseAddress = new Uri(baseUrl);
                });

            return services;
        }
    }
}