namespace FirstAPIProject.Application.Modules.Whitelist.Models;

public sealed record WhitelistFilter(
    string? Search,
    bool? IsActive,
    int Page = 1,
    int PageSize = 20 );