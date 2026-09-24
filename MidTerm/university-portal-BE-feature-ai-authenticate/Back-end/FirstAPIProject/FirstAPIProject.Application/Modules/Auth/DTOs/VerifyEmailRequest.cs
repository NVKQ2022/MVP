using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.DTOs
{
    public sealed record VerifyEmailRequest
    {
        public string Email { get; init; } = null!;

        public string Otp { get; init; } = null!;
    }
}
