using FirstAPIProject.Application.Common.Exceptions;
using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.User.DTOs;
using FirstAPIProject.Application.Modules.User.Interfaces;
using FirstAPIProject.Application.Modules.User.Models;
using UserEntity = FirstAPIProject.Domain.Entities.User;

namespace FirstAPIProject.Application.Modules.User.Services;

public sealed class AdminUserService : IAdminUserService
{
    private readonly IUserRepository _userRepository;
    private readonly IRoleRepository _roleRepository;
    private readonly ICurrentUserService _currentUser;
    private readonly IUnitOfWork _unitOfWork;

    public AdminUserService(
        IUserRepository userRepository,
        IRoleRepository roleRepository,
        ICurrentUserService currentUser,
        IUnitOfWork unitOfWork )
    {
        _userRepository = userRepository;
        _roleRepository = roleRepository;
        _currentUser = currentUser;
        _unitOfWork = unitOfWork;
    }

    public async Task<PagedResult<AdminUserResponse>> GetUsersAsync(
        AdminUserFilterRequest request,
        CancellationToken cancellationToken = default )
    {
        var filter = new UserFilter(
            request.Search,
            request.RoleId,
            request.Status,
            request.IsActive,
            request.Page,
            request.PageSize);

        var pagedUsers = await _userRepository.GetPagedAsync(filter, cancellationToken);

        var mappedItems = pagedUsers.Items.Select(MapToResponse).ToList();

        return new PagedResult<AdminUserResponse>
        {
            Items = mappedItems,
            TotalCount = pagedUsers.TotalCount,
            PageNumber = pagedUsers.Page,
            PageSize = pagedUsers.PageSize
        };
    }

    public async Task<AdminUserResponse> GetUserByIdAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        var user = await _userRepository.GetByIdWithRoleAsync(id, cancellationToken);
        if (user is null)
        {
            throw new NotFoundException($"User with ID '{id}' was not found.");
        }

        return MapToResponse(user);
    }
    public async Task<AdminUserResponse> UpdateUserAsync(
    Guid id,
    AdminUpdateUserRequest request,
    CancellationToken cancellationToken = default )
    {
        var user = await _userRepository.GetByIdWithRoleAsync(id, cancellationToken);
        if (user is null)
        {
            throw new NotFoundException($"User with ID '{id}' was not found.");
        }

        var roleExists = await _roleRepository.ExistsAsync(request.RoleId, cancellationToken);
        if (!roleExists)
        {
            throw new NotFoundException($"Role with ID '{request.RoleId}' does not exist.");
        }

        user.AssignRole(request.RoleId);

        await _unitOfWork.SaveChangesAsync(cancellationToken);

        var updatedUser = await _userRepository.GetByIdWithRoleAsync(id, cancellationToken);
        return MapToResponse(updatedUser ?? user);
    }

    public async Task LockUserAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        EnsureNotSelfAction(id, "lock");

        var user = await _userRepository.GetByIdAsync(id, cancellationToken);
        if (user is null)
        {
            throw new NotFoundException($"User with ID '{id}' was not found.");
        }

        user.Lock();
        await _unitOfWork.SaveChangesAsync(cancellationToken);
    }

    public async Task UnlockUserAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        var user = await _userRepository.GetByIdAsync(id, cancellationToken);
        if (user is null)
        {
            throw new NotFoundException($"User with ID '{id}' was not found.");
        }

        user.Unlock();
        await _unitOfWork.SaveChangesAsync(cancellationToken);
    }

    public async Task ActivateUserAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        var user = await _userRepository.GetByIdAsync(id, cancellationToken);
        if (user is null)
        {
            throw new NotFoundException($"User with ID '{id}' was not found.");
        }

        user.Activate();
        await _unitOfWork.SaveChangesAsync(cancellationToken);
    }

    public async Task SoftDeleteUserAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        EnsureNotSelfAction(id, "delete");

        var user = await _userRepository.GetByIdAsync(id, cancellationToken);
        if (user is null)
        {
            throw new NotFoundException($"User with ID '{id}' was not found.");
        }

        user.SoftDelete(DateTimeOffset.UtcNow);
        await _unitOfWork.SaveChangesAsync(cancellationToken);
    }

    private void EnsureNotSelfAction( Guid targetUserId, string action )
    {
        if (_currentUser.IsAuthenticated && _currentUser.UserId == targetUserId)
        {
            throw new ConflictException($"Administrators cannot {action} their own account.");
        }
    }
    private static AdminUserResponse MapToResponse( UserEntity user ) => new(
        user.Id,
        user.UserName,
        user.Email,
        user.PhoneNumber,
        user.Address,
        user.Gender,
        user.DateOfBirth,
        user.AvatarUrl,
        user.RoleId,
        user.Role?.Name ?? string.Empty,
        user.Status,
        user.IsActive,
        user.IsDeleted,
        user.LastLoginAt,
        user.CreatedAt,
        user.UpdatedAt);
}

