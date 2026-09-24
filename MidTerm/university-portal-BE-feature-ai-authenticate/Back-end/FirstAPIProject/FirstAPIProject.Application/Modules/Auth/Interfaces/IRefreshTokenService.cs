using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.Interfaces
{
    public interface IRefreshTokenService
    {
        string GenerateToken();

        string HashToken(string token);

        DateTime GetExpiration();
    }
}
