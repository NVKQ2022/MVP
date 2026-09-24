using FirstAPIProject.Domain.Common.Enums;

namespace FirstAPIProject.Application.Modules.User.DTOs;

public sealed record AdminUserResponse(
    Guid Id,
    string? UserName,
    string Email,
    string? PhoneNumber,
    string? Address,
    Gender? Gender,
    DateOnly? DateOfBirth,
    string? AvatarUrl,
    Guid RoleId,
    string RoleName,
    UserStatus Status,
    bool IsActive,
    bool IsDeleted,
    DateTimeOffset? LastLoginAt,
    DateTimeOffset CreatedAt,
    DateTimeOffset UpdatedAt );

public sealed record AdminUserFilterRequest(
    string? Search,
    Guid? RoleId,
    UserStatus? Status,
    bool? IsActive,
    int Page = 1,
    int PageSize = 20 );

public sealed record AdminUpdateUserRequest( Guid RoleId );