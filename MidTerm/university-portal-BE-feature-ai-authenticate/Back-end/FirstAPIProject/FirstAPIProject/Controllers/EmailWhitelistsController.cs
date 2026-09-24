using Asp.Versioning;
using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.Whitelist.DTOs;
using FirstAPIProject.Application.Modules.Whitelist.Interfaces;
using FirstAPIProject.Domain.Constants;
using FluentValidation;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace FirstAPIProject.API.Controllers;

[ApiController]
[ApiVersion(1.0)]
[Route("api/v{version:apiVersion}/admin/whitelist")]
[Authorize(Roles = SystemRoleNames.Admin)]
public sealed class EmailWhitelistsController : ControllerBase
{
    private readonly IEmailWhitelistService _service;

    public EmailWhitelistsController( IEmailWhitelistService service )
    {
        _service = service;
    }

    [HttpGet]
    public async Task<ActionResult<PagedResult<WhitelistResponse>>> GetWhitelists(
        [FromQuery] WhitelistFilterRequest request,
        [FromServices] IValidator<WhitelistFilterRequest> validator,
        CancellationToken cancellationToken )
    {
        var validationResult = await validator.ValidateAsync(request, cancellationToken);
        if (!validationResult.IsValid)
        {
            throw new ValidationException(validationResult.Errors);
        }

        var result = await _service.GetWhitelistsAsync(request, cancellationToken);
        return Ok(result);
    }

    [HttpGet("{id:guid}")]
    public async Task<ActionResult<WhitelistResponse>> GetById(
        Guid id,
        CancellationToken cancellationToken )
    {
        var result = await _service.GetByIdAsync(id, cancellationToken);
        return Ok(result);
    }

    [HttpPost]
    public async Task<ActionResult<WhitelistResponse>> Create(
        [FromBody] CreateWhitelistRequest request,
        [FromServices] IValidator<CreateWhitelistRequest> validator,
        CancellationToken cancellationToken )
    {
        var validationResult = await validator.ValidateAsync(request, cancellationToken);
        if (!validationResult.IsValid)
        {
            throw new ValidationException(validationResult.Errors);
        }

        var result = await _service.CreateAsync(request, cancellationToken);
        return CreatedAtAction(nameof(GetById), new { id = result.Id }, result);
    }

    [HttpPut("{id:guid}")]
    public async Task<ActionResult<WhitelistResponse>> Update(
        Guid id,
        [FromBody] UpdateWhitelistRequest request,
        [FromServices] IValidator<UpdateWhitelistRequest> validator,
        CancellationToken cancellationToken )
    {
        var validationResult = await validator.ValidateAsync(request, cancellationToken);
        if (!validationResult.IsValid)
        {
            throw new ValidationException(validationResult.Errors);
        }

        var result = await _service.UpdateAsync(id, request, cancellationToken);
        return Ok(result);
    }

    [HttpPatch("{id:guid}/activate")]
    public async Task<IActionResult> Activate(
        Guid id,
        CancellationToken cancellationToken )
    {
        await _service.ActivateAsync(id, cancellationToken);
        return NoContent();
    }

    [HttpPatch("{id:guid}/deactivate")]
    public async Task<IActionResult> Deactivate(
        Guid id,
        CancellationToken cancellationToken )
    {
        await _service.DeactivateAsync(id, cancellationToken);
        return NoContent();
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(
        Guid id,
        CancellationToken cancellationToken )
    {
        await _service.DeleteAsync(id, cancellationToken);
        return NoContent();
    }
}