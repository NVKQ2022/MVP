using FirstAPIProject.Application.Common.Exceptions;
using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.User.DTOs;
using FirstAPIProject.Application.Modules.User.Interfaces;
using UserEntity = FirstAPIProject.Domain.Entities.User;


namespace FirstAPIProject.Application.Modules.User.Services;

public sealed class UserProfileService : IUserProfileService
{
    private readonly IUserRepository _users;
    private readonly IFileStorageService _fileStorage;
    private readonly ICurrentUserService _currentUser;
    private readonly IUnitOfWork _unitOfWork;
    public UserProfileService(
        IUserRepository users,
        IFileStorageService fileStorage,
        ICurrentUserService currentUser,
        IUnitOfWork unitOfWork )
    {
        _users = users;
        _fileStorage = fileStorage;
        _currentUser = currentUser;
        _unitOfWork = unitOfWork;
    }

    public async Task<UserProfileResponse> GetMyProfileAsync(
        CancellationToken cancellationToken = default )
    {
        var user = await GetCurrentUserAsync(cancellationToken);
        return Map(user);
    }

    public async Task<UserProfileResponse> UpdateMyProfileAsync(
        UpdateProfileRequest request,
        CancellationToken cancellationToken = default )
    {
        var user = await GetCurrentUserAsync(cancellationToken);

        user.UpdateProfile(
            request.UserName,
            request.PhoneNumber,
            request.Address,
            request.Gender,
            request.DateOfBirth);

        await _unitOfWork.SaveChangesAsync(cancellationToken);
        return Map(user);
    }

    public async Task<string> UpdateMyAvatarAsync(
        FileUploadInput file,
        CancellationToken cancellationToken = default )
    {
        var user = await GetCurrentUserAsync(cancellationToken);
        var oldAvatar = user.AvatarUrl;

        var newAvatar = await _fileStorage.SaveAvatarAsync(
            file,
            cancellationToken);

        user.UpdateAvatar(newAvatar);

        try
        {
            await _unitOfWork.SaveChangesAsync(cancellationToken);
        }
        catch
        {
            await _fileStorage.DeleteIfExistsAsync(
                newAvatar,
                CancellationToken.None);


            throw;
        }

        try
        {
            await _fileStorage.DeleteIfExistsAsync(
                oldAvatar,
                CancellationToken.None);
        }
        catch
        {
            // Cleanup failure should be logged by a shared operational
            // logging strategy. Do not fail the already committed update.
        }


        return newAvatar;
    }


    private async Task<UserEntity> GetCurrentUserAsync(
        CancellationToken cancellationToken )
    {
        if (!_currentUser.IsAuthenticated ||
            _currentUser.UserId == Guid.Empty)
        {
            throw new UnauthorizedAccessException(
                "Authentication is required.");
        }

        var user = await _users.GetByIdWithRoleAsync(
            _currentUser.UserId,
            cancellationToken);


        return user
            ?? throw new NotFoundException(
                "User was not found.");
    }

    private static UserProfileResponse Map( UserEntity user ) => new(
        user.Id,
        user.UserName,
        user.Email,
        user.PhoneNumber,
        user.Address,
        user.Gender,
        user.DateOfBirth,
        user.AvatarUrl,
        user.Role.Name,
        user.Status,
        user.IsActive,
        user.LastLoginAt,
        user.CreatedAt,
        user.UpdatedAt);
}