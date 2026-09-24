using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using System;
using System.Collections.Generic;
using System.Text;
using FirstAPIProject.Infrastructure.VectorDb.Models;

namespace FirstAPIProject.Infrastructure.VectorDb.Configurations
{
    public static class VectorDbConfiguration
    {
        public static IServiceCollection AddVectorDb(
            this IServiceCollection services,
            IConfiguration configuration)
        {
            services.Configure<VectorDbOptions>(
                configuration.GetSection("VectorDb"));

            return services;
        }
    }
}