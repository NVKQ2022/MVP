using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.User.DTOs;

namespace FirstAPIProject.Application.Modules.User.Interfaces;

public interface IAdminUserService
{
    Task<PagedResult<AdminUserResponse>> GetUsersAsync(
        AdminUserFilterRequest request,
        CancellationToken cancellationToken = default );

    Task<AdminUserResponse> GetUserByIdAsync(
        Guid id,
        CancellationToken cancellationToken = default );

    Task<AdminUserResponse> UpdateUserAsync(
        Guid id,
        AdminUpdateUserRequest request,
        CancellationToken cancellationToken = default );

    Task LockUserAsync(
        Guid id,
        CancellationToken cancellationToken = default );

    Task UnlockUserAsync(
        Guid id,
        CancellationToken cancellationToken = default );

    Task ActivateUserAsync(
        Guid id,
        CancellationToken cancellationToken = default );

    Task SoftDeleteUserAsync(
        Guid id,
        CancellationToken cancellationToken = default );
}

