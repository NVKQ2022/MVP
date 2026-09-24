using FirstAPIProject.Application.Modules.Auth.Interfaces;
using Microsoft.Extensions.Options;
using System;
using System.Collections.Generic;
using System.Security.Cryptography;
using System.Text;

namespace FirstAPIProject.Infrastructure.Authentication
{
    public sealed class RefreshTokenService : IRefreshTokenService
    {
        private readonly RefreshTokenSettings _settings;

        public RefreshTokenService(IOptions<RefreshTokenSettings> options)
        {
            _settings = options.Value;
        }

        public string GenerateToken()
        {
            var randomBytes = RandomNumberGenerator.GetBytes(64);

            return Convert.ToBase64String(randomBytes);
        }

        public string HashToken(string token)
        {
            var bytes = Encoding.UTF8.GetBytes(token);

            var hash = SHA256.HashData(bytes);

            return Convert.ToHexString(hash);
        }

        public DateTime GetExpiration()
        {
            return DateTime.UtcNow.AddDays(_settings.ExpirationDays);
        }
    }
}
