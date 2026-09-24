using FirstAPIProject.Domain.Common.Enums;

namespace FirstAPIProject.Application.Modules.User.Models;

public sealed record UserFilter(
    string? Search,
    Guid? RoleId,
    UserStatus? Status,
    bool? IsActive,
    int Page,
    int PageSize );