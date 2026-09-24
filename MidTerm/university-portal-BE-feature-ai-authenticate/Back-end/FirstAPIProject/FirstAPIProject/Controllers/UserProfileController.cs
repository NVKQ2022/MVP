using Asp.Versioning;
using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.User.DTOs;
using FirstAPIProject.Application.Modules.User.Interfaces;
using FluentValidation;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace FirstAPIProject.API.Controllers;

[ApiController]
[ApiVersion(1.0)]
[Route("api/v{version:apiVersion}/users/me")]
[Authorize]
public sealed class UserProfileController : ControllerBase
{
    private readonly IUserProfileService _service;
    private readonly IValidator<UpdateProfileRequest> _validator;
    public UserProfileController(
        IUserProfileService service,
        IValidator<UpdateProfileRequest> validator )
    {
        _service = service;
        _validator = validator;
    }

    [HttpGet]
    public async Task<ActionResult<UserProfileResponse>> Get(
        CancellationToken cancellationToken )
    {
        return Ok(await _service.GetMyProfileAsync(cancellationToken));
    }

    [HttpPut]
    public async Task<ActionResult<UserProfileResponse>> Update(
        UpdateProfileRequest request,
        CancellationToken cancellationToken )
    {
        var validationResult = await _validator.ValidateAsync(request, cancellationToken);
        if (!validationResult.IsValid)
        {
            throw new ValidationException(validationResult.Errors);
        }

        return Ok(await _service.UpdateMyProfileAsync(request, cancellationToken));
    }

    [HttpPatch("avatar")]
    [Consumes("multipart/form-data")]
    [RequestSizeLimit(2 * 1024 * 1024)]
    public async Task<IActionResult> UpdateAvatar(
        [FromForm] AvatarUploadRequest request,
        CancellationToken cancellationToken )
    {
        if (request.File is null || request.File.Length == 0)
        {
            return BadRequest(new
            {
                message = "An avatar file is required."
            });
        }

        await using var stream = request.File.OpenReadStream();

        var avatarUrl = await _service.UpdateMyAvatarAsync(
            new FileUploadInput(
                stream,
                request.File.FileName,
                request.File.Length),
            cancellationToken);

        return Ok(new { avatarUrl });
    }
}
public sealed class AvatarUploadRequest
{
    public IFormFile? File { get; init; }
}