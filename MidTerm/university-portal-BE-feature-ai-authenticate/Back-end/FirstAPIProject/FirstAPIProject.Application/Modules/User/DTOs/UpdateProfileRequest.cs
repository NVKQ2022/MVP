using FirstAPIProject.Domain.Common.Enums;

namespace FirstAPIProject.Application.Modules.User.DTOs;

public sealed record UpdateProfileRequest(
    string? UserName,
    string? PhoneNumber,
    string? Address,
    Gender? Gender,
    DateOnly? DateOfBirth );
