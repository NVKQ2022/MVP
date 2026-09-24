using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.Whitelist.DTOs;

namespace FirstAPIProject.Application.Modules.Whitelist.Interfaces;

public interface IEmailWhitelistService
{
    Task<PagedResult<WhitelistResponse>> GetWhitelistsAsync(
        WhitelistFilterRequest request,
        CancellationToken cancellationToken = default );

    Task<WhitelistResponse> GetByIdAsync(
        Guid id,
        CancellationToken cancellationToken = default );

    Task<WhitelistResponse> CreateAsync(
        CreateWhitelistRequest request,
        CancellationToken cancellationToken = default );

    Task<WhitelistResponse> UpdateAsync(
        Guid id,
        UpdateWhitelistRequest request,
        CancellationToken cancellationToken = default );

    Task ActivateAsync(
        Guid id,
        CancellationToken cancellationToken = default );

    Task DeactivateAsync(
        Guid id,
        CancellationToken cancellationToken = default );

    Task DeleteAsync(
        Guid id,
        CancellationToken cancellationToken = default );
}