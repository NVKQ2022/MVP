using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.DTOs;

public sealed record LoginResponse
(
    bool RequiresMfa,

    string? AccessToken,

    DateTime? ExpiresAt,

    string? RefreshToken,

    Guid? ChallengeId
);

