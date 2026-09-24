using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.DTOs
{
    public sealed class FaceAuthenticateLoginRequest
    {
        public required string DeviceId { get; init; }
        public required IFormFile Capture { get; init; }
    }
}
