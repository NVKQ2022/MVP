using Asp.Versioning;
using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.User.DTOs;
using FirstAPIProject.Application.Modules.User.Interfaces;
using FirstAPIProject.Domain.Constants;
using FluentValidation;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace FirstAPIProject.API.Controllers;

[ApiController]
[ApiVersion(1.0)]
[Route("api/v{version:apiVersion}/admin/users")]
[Authorize(Roles = SystemRoleNames.Admin)]
public sealed class AdminUsersController : ControllerBase
{
    private readonly IAdminUserService _adminUserService;
    private readonly IValidator<AdminUserFilterRequest> _filterValidator;
    private readonly IValidator<AdminUpdateUserRequest> _updateValidator;

    public AdminUsersController(
        IAdminUserService adminUserService,
        IValidator<AdminUserFilterRequest> filterValidator,
        IValidator<AdminUpdateUserRequest> updateValidator )
    {
        _adminUserService = adminUserService;
        _filterValidator = filterValidator;
        _updateValidator = updateValidator;
    }

    [HttpGet]
    public async Task<ActionResult<PagedResult<AdminUserResponse>>> GetUsers(
        [FromQuery] AdminUserFilterRequest request,
        CancellationToken cancellationToken )
    {
        var validationResult = await _filterValidator.ValidateAsync(request, cancellationToken);
        if (!validationResult.IsValid)
        {
            throw new ValidationException(validationResult.Errors);
        }

        var result = await _adminUserService.GetUsersAsync(request, cancellationToken);
        return Ok(result);
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<AdminUserResponse>> GetUserById(
        Guid id,
        CancellationToken cancellationToken )
    {
        var result = await _adminUserService.GetUserByIdAsync(id, cancellationToken);
        return Ok(result);
    }

    [HttpPut("{id:guid}")]
    public async Task<ActionResult<AdminUserResponse>> UpdateUser(
        Guid id,
        [FromBody] AdminUpdateUserRequest request,
        CancellationToken cancellationToken )
    {
        var validationResult = await _updateValidator.ValidateAsync(request, cancellationToken);
        if (!validationResult.IsValid)
        {
            throw new ValidationException(validationResult.Errors);
        }

        var result = await _adminUserService.UpdateUserAsync(id, request, cancellationToken);
        return Ok(result);
    }


    [HttpPatch("{id:guid}/lock")]
    public async Task<IActionResult> LockUser(
        Guid id,
        CancellationToken cancellationToken )
    {
        await _adminUserService.LockUserAsync(id, cancellationToken);
        return NoContent();
    }

    [HttpPatch("{id:guid}/unlock")]
    public async Task<IActionResult> UnlockUser(
        Guid id,
        CancellationToken cancellationToken )
    {
        await _adminUserService.UnlockUserAsync(id, cancellationToken);
        return NoContent();
    }

    [HttpPatch("{id:guid}/activate")]
    public async Task<IActionResult> ActivateUser(
        Guid id,
        CancellationToken cancellationToken )
    {
        await _adminUserService.ActivateUserAsync(id, cancellationToken);
        return NoContent();
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> SoftDeleteUser(
        Guid id,
        CancellationToken cancellationToken )
    {
        await _adminUserService.SoftDeleteUserAsync(id, cancellationToken);
        return NoContent();
    }
}