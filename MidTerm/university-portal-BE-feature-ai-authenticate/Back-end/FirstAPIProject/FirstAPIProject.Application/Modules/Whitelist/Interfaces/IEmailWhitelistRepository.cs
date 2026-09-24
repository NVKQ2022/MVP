using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.Whitelist.Models;
using FirstAPIProject.Domain.Entities;

namespace FirstAPIProject.Application.Modules.Whitelist.Interfaces;

public interface IEmailWhitelistRepository : IGenericRepository<EmailWhitelist>
{
    Task<PagedResult<EmailWhitelist>> GetPagedAsync(
        WhitelistFilter filter,
        CancellationToken cancellationToken = default );

    Task<bool> EmailExistsAsync(
        string normalizedEmail,
        Guid? excludingId = null,
        CancellationToken cancellationToken = default );

    Task<bool> DomainExistsAsync(
        string normalizedDomain,
        Guid? excludingId = null,
        CancellationToken cancellationToken = default );

    Task<bool> IsEmailAllowedAsync(
        string email,
        CancellationToken cancellationToken = default );
}