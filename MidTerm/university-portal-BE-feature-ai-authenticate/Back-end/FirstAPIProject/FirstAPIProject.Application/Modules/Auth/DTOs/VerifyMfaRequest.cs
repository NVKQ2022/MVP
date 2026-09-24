using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.DTOs
{
    public sealed record VerifyMfaRequest
    (
        Guid ChallengeId,

        string Otp
    );
}
