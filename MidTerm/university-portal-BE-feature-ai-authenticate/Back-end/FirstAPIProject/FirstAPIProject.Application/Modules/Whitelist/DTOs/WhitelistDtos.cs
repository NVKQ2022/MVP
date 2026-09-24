namespace FirstAPIProject.Application.Modules.Whitelist.DTOs;

public sealed record WhitelistFilterRequest(
    string? Search,
    bool? IsActive,
    int Page = 1,
    int PageSize = 20 );

public sealed record CreateWhitelistRequest(
    string? Email,
    string? Domain );

public sealed record UpdateWhitelistRequest(
    string? Email,
    string? Domain );

public sealed record WhitelistResponse(
    Guid Id,
    string? Email,
    string? Domain,
    bool IsActive,
    Guid CreatedBy,
    DateTimeOffset CreatedAt,
    DateTimeOffset UpdatedAt );