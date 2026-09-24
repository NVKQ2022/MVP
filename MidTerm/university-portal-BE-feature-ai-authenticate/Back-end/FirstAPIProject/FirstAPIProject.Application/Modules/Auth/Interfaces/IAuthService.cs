using FirstAPIProject.Application.Modules.Auth.DTOs;
using FirstAPIProject.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.Interfaces
{
    public interface IAuthService
    {
        Task<RegisterResponse> RegisterAsync(RegisterRequest request, CancellationToken cancellationToken = default);

        Task<LoginResponse> LoginAsync(LoginRequest request, CancellationToken cancellationToken = default);

        Task<AuthResponse> RefreshTokenAsync(RefreshTokenRequest request, CancellationToken cancellationToken = default);

        Task LogoutAsync(Guid userId, RefreshTokenRequest request, CancellationToken cancellationToken = default);

        Task VerifyEmailAsync(VerifyEmailRequest request, CancellationToken cancellationToken = default);

        Task<EnableMfaResponse> EnableMfaAsync(Guid userId, CancellationToken cancellationToken = default);

        Task<AuthResponse> VerifyMfaAsync(Guid challengeId, string otp, CancellationToken cancellationToken = default);
    }
}
