using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.User.DTOs;

namespace FirstAPIProject.Application.Modules.User.Interfaces;

public interface IUserProfileService
{
    Task<UserProfileResponse> GetMyProfileAsync(
        CancellationToken cancellationToken = default );

    Task<UserProfileResponse> UpdateMyProfileAsync(
        UpdateProfileRequest request,
        CancellationToken cancellationToken = default );

    Task<string> UpdateMyAvatarAsync(
        FileUploadInput file,
        CancellationToken cancellationToken = default );
}
