using FirstAPIProject.Application.Modules.Auth.DTOs;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.Interfaces
{
    public interface IFaceAuthenticateService
    {
        Task<AuthResponse> FaceAuthenticateAsync(
        FaceAuthenticateLoginRequest request,
        CancellationToken cancellationToken = default);
    }
}
