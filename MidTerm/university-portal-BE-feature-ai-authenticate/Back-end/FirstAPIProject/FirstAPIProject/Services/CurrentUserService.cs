using FirstAPIProject.Application.Common.Interfaces;
using System.Security.Claims;

namespace FirstAPIProject.API.Services;

public sealed class CurrentUserService : ICurrentUserService
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CurrentUserService( IHttpContextAccessor httpContextAccessor )
    {
        _httpContextAccessor = httpContextAccessor;
    }

    public bool IsAuthenticated =>
        _httpContextAccessor.HttpContext?
            .User.Identity?.IsAuthenticated == true;

    public Guid UserId
    {
        get
        {
            var principal = _httpContextAccessor.HttpContext?.User;

            var raw = principal?.FindFirstValue(ClaimTypes.NameIdentifier)
                ?? principal?.FindFirstValue("sub");

            return Guid.TryParse(raw, out var id) ? id : Guid.Empty;
        }
    }

    public bool IsInRole( string role ) =>
        _httpContextAccessor.HttpContext?
            .User.IsInRole(role) == true;
}
