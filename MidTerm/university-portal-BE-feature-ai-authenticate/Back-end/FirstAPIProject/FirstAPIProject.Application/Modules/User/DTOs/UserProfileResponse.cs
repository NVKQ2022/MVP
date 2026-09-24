using FirstAPIProject.Domain.Common.Enums;

namespace FirstAPIProject.Application.Modules.User.DTOs;

public sealed record UserProfileResponse(
    Guid Id,
    string? UserName,
    string Email,
    string? PhoneNumber,
    string? Address,
    Gender? Gender,
    DateOnly? DateOfBirth,
    string? AvatarUrl,
    string Role,
    UserStatus Status,
    bool IsActive,
    DateTimeOffset? LastLoginAt,
    DateTimeOffset CreatedAt,
    DateTimeOffset UpdatedAt );