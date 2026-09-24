using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.Interfaces
{
    public interface IFaceRegistrationService
    {
        Task RegisterAsync(
            Guid userId,
            IFormFile image,
            CancellationToken cancellationToken = default);
    }
}
