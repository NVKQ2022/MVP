using Asp.Versioning;
using FirstAPIProject.Application.Modules.Announcement.DTOs;
using FirstAPIProject.Application.Modules.Announcement.Interfaces;
using FluentValidation;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
namespace FirstAPIProject.API.Controllers;

[ApiController]
[ApiVersion(1.0)]
[Route("api/v{version:apiVersion}")]
[EnableRateLimiting("announcement")]
public class AnnouncementController : ControllerBase
{

    private readonly IAnnouncementReadService _announcementReadService;
    private readonly IAnnouncementQueryService _queryService;
    private readonly IAnnouncementManagementService _managementService;
    private readonly IValidator<AnnouncementQueryRequest> _queryValidator;

    private readonly IValidator<CreateAnnouncementRequest> _createValidator;

    private readonly IValidator<UpdateAnnouncementRequest> _updateValidator;

    public AnnouncementController( IAnnouncementReadService announcementReadService,
        IAnnouncementQueryService queryService,
        IAnnouncementManagementService managementService,
        IValidator<AnnouncementQueryRequest> queryValidator,
        IValidator<CreateAnnouncementRequest> createValidator,
        IValidator<UpdateAnnouncementRequest> updateValidator )
    {
        _announcementReadService = announcementReadService;
        _queryService = queryService;
        _managementService = managementService;
        _queryValidator = queryValidator;
        _createValidator = createValidator;
        _updateValidator = updateValidator;
    }


    #region Student Endpoints

    /// <summary>
    /// GET /api/v1/announcements
    /// </summary>
    [HttpGet("announcements")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> GetAnnouncements(
        [FromQuery] AnnouncementQueryRequest query,
        CancellationToken cancellationToken )
    {
        var validationResult =
            await _queryValidator.ValidateAsync(
                query,
                cancellationToken);

        if (!validationResult.IsValid)
        {
            throw new ValidationException(
                validationResult.Errors);
        }

        var currentUserId = GetCurrentUserId();

        var result =
            await _queryService.GetAnnouncementsAsync(
                query,
                currentUserId);

        return Ok(result);
    }

    [HttpGet("announcements/{id:guid}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetAnnouncement(
    Guid id,
    CancellationToken cancellationToken )
    {
        var currentUserId = GetCurrentUserId();

        var result =
            await _queryService.GetByIdAsync(
                id,
                currentUserId);

        await _announcementReadService.MarkAsReadAsync(
            id,
            currentUserId,
            cancellationToken);

        return Ok(result);
    }

    #endregion

    #region Admin Endpoints

    /// <summary>
    /// GET /api/v1/admin/announcements
    /// </summary>
    [HttpGet("admin/announcements")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> GetAdminAnnouncements(
        [FromQuery] AnnouncementQueryRequest query,
        CancellationToken cancellationToken )
    {
        var validationResult =
            await _queryValidator.ValidateAsync(
                query,
                cancellationToken);

        if (!validationResult.IsValid)
        {
            throw new ValidationException(
                validationResult.Errors);
        }

        var result =
            await _queryService
                .GetAdminAnnouncementsAsync(query);

        return Ok(result);
    }

    /// <summary>
    /// GET /api/v1/admin/announcements/{id}
    /// </summary>
    [HttpGet("admin/announcements/{id:guid}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<IActionResult> GetAdminAnnouncement(
        Guid id )
    {
        var result = await _queryService
            .GetAdminAnnouncementByIdAsync(id);

        return Ok(result);
    }

    /// <summary>
    /// POST /api/v1/admin/announcements
    /// </summary>
    [HttpPost("admin/announcements")]
    [ProducesResponseType(StatusCodes.Status201Created)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> CreateAnnouncement(
        [FromBody] CreateAnnouncementRequest request,
        CancellationToken cancellationToken )
    {
        var validationResult =
            await _createValidator.ValidateAsync(
                request,
                cancellationToken);

        if (!validationResult.IsValid)
        {
            throw new ValidationException(
                validationResult.Errors);
        }

        var currentUserId = GetCurrentUserId();

        var id =
            await _managementService.CreateAsync(
                request,
                currentUserId);

        return CreatedAtAction(
            nameof(GetAdminAnnouncement),
            new
            {
                version = "1",
                id
            },
            new { id });
    }

    /// <summary>
    /// PUT /api/v1/admin/announcements/{id}
    /// </summary>
    [HttpPut("admin/announcements/{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    [ProducesResponseType(StatusCodes.Status400BadRequest)]
    public async Task<IActionResult> UpdateAnnouncement(
        Guid id,
        [FromBody] UpdateAnnouncementRequest request,
        CancellationToken cancellationToken )
    {
        var validationResult =
            await _updateValidator.ValidateAsync(
                request,
                cancellationToken);

        if (!validationResult.IsValid)
        {
            throw new ValidationException(
                validationResult.Errors);
        }

        await _managementService.UpdateAsync(
            id,
            request);

        return NoContent();
    }

    /// <summary>
    /// PATCH /api/v1/admin/announcements/{id}/publish
    /// </summary>
    [HttpPatch("admin/announcements/{id:guid}/publish")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    public async Task<IActionResult> PublishAnnouncement(
        Guid id )
    {
        await _managementService.PublishAsync(id);

        return NoContent();
    }

    /// <summary>
    /// PATCH /api/v1/admin/announcements/{id}/archive
    /// </summary>
    [HttpPatch("admin/announcements/{id:guid}/archive")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    public async Task<IActionResult> ArchiveAnnouncement(
        Guid id )
    {
        await _managementService.ArchiveAsync(id);

        return NoContent();
    }

    /// <summary>
    /// DELETE /api/v1/admin/announcements/{id}
    /// </summary>
    [HttpDelete("admin/announcements/{id:guid}")]
    [ProducesResponseType(StatusCodes.Status204NoContent)]
    public async Task<IActionResult> DeleteAnnouncement(
        Guid id )
    {
        await _managementService.DeleteAsync(id);

        return NoContent();
    }


    #endregion

    private Guid GetCurrentUserId()
    {
        var userIdClaim = User.FindFirst("sub")
            ?? User.FindFirst("UserId")
            ?? User.FindFirst(System.Security.Claims.ClaimTypes.NameIdentifier);

        if (userIdClaim is null)
        {
            throw new UnauthorizedAccessException(
                "User ID not found in claims.");
        }

        return Guid.Parse(userIdClaim.Value);
    }
}