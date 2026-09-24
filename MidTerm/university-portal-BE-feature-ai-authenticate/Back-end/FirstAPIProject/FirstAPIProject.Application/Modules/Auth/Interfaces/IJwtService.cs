using FirstAPIProject.Application.Modules.Auth.DTOs;
using FirstAPIProject.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.Interfaces
{
    public interface IJwtService
    {
        AccessTokenResponse GenerateToken(FirstAPIProject.Domain.Entities.User user);
    }
}
