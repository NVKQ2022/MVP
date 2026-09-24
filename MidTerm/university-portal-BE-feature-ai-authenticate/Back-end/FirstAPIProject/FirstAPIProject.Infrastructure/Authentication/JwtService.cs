using FirstAPIProject.Application.Modules.Auth.DTOs;
using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Domain.Entities;
using Microsoft.Extensions.Options;
using Microsoft.IdentityModel.Tokens;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;

namespace FirstAPIProject.Infrastructure.Authentication
{
    public sealed class JwtService : IJwtService
    {
        private readonly JwtSettings _jwtSettings;

        public JwtService( IOptions<JwtSettings> jwtOptions )
        {
            _jwtSettings = jwtOptions.Value;
        }

        public AccessTokenResponse GenerateToken( User user )
        {
            var expiration = DateTime.UtcNow.AddMinutes(
                _jwtSettings.ExpirationMinutes);

            var claims = new List<Claim>
            {
                new(JwtRegisteredClaimNames.Sub, user.Id.ToString()),

                new(JwtRegisteredClaimNames.Email, user.Email),

                new(ClaimTypes.NameIdentifier, user.Id.ToString()),

                new(ClaimTypes.Email, user.Email),

                new Claim(ClaimTypes.Role, user.Role?.Name ?? string.Empty)
            };

            var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_jwtSettings.SecretKey));

            var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

            var tokenDescriptor = new SecurityTokenDescriptor
            {
                Subject = new ClaimsIdentity(claims),

                Expires = expiration,

                Issuer = _jwtSettings.Issuer,

                Audience = _jwtSettings.Audience,

                SigningCredentials = credentials
            };

            var tokenHandler = new JwtSecurityTokenHandler();

            var token = tokenHandler.CreateToken(tokenDescriptor);

            var accessToken = tokenHandler.WriteToken(token);

            return new AccessTokenResponse(accessToken, expiration);
        }
    }
}
