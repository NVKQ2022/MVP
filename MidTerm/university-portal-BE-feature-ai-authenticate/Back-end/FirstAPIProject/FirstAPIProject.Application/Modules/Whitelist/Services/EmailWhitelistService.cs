using FirstAPIProject.Application.Common.Exceptions;
using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.Whitelist.DTOs;
using FirstAPIProject.Application.Modules.Whitelist.Interfaces;
using FirstAPIProject.Application.Modules.Whitelist.Models;
using FirstAPIProject.Domain.Entities;
using Microsoft.Extensions.Logging;

namespace FirstAPIProject.Application.Modules.Whitelist.Services;

public sealed class EmailWhitelistService : IEmailWhitelistService
{
    private readonly IEmailWhitelistRepository _whitelistRepository;
    private readonly ICurrentUserService _currentUser;
    private readonly IUnitOfWork _unitOfWork;
    private readonly ILogger<EmailWhitelistService> _logger;

    public EmailWhitelistService(
        IEmailWhitelistRepository whitelistRepository,
        ICurrentUserService currentUser,
        IUnitOfWork unitOfWork,
        ILogger<EmailWhitelistService> logger )
    {
        _whitelistRepository = whitelistRepository;
        _currentUser = currentUser;
        _unitOfWork = unitOfWork;
        _logger = logger;
    }

    public async Task<PagedResult<WhitelistResponse>> GetWhitelistsAsync(
            WhitelistFilterRequest request,
            CancellationToken cancellationToken = default )
    {
        var filter = new WhitelistFilter(
            request.Search,
            request.IsActive,
            request.Page,
            request.PageSize);

        var paged = await _whitelistRepository.GetPagedAsync(filter, cancellationToken);

        var mappedItems = paged.Items
            .Select(MapToResponse)
            .ToList();

        return new PagedResult<WhitelistResponse>
        {
            Items = mappedItems,
            TotalCount = paged.TotalCount,
            PageNumber = paged.PageNumber,
            PageSize = paged.PageSize
        };
    }

    public async Task<WhitelistResponse> GetByIdAsync( Guid id, CancellationToken cancellationToken = default )
    {
        var entry = await _whitelistRepository.GetByIdAsync(id, cancellationToken);

        if (entry is null)
        {
            throw new NotFoundException("Whitelist entry was not found.");
        }

        return MapToResponse(entry);
    }

    public async Task<WhitelistResponse> CreateAsync( CreateWhitelistRequest request, CancellationToken cancellationToken = default )
    {
        EnsureExclusiveEntry(request.Email, request.Domain);

        var adminId = RequireCurrentUserId();

        EmailWhitelist entry;

        if (!string.IsNullOrWhiteSpace(request.Email))
        {
            var normalizedEmail = NormalizeEmail(request.Email);

            var emailExists = await _whitelistRepository.EmailExistsAsync(normalizedEmail, excludingId: null, cancellationToken);

            if (emailExists)
            {
                throw new ConflictException("A whitelist entry with this email already exists.");
            }

            entry = EmailWhitelist.ForEmail(normalizedEmail, adminId);
        }
        else
        {
            var normalizedDomain = NormalizeDomain(request.Domain!);

            var domainExists = await _whitelistRepository.DomainExistsAsync(normalizedDomain, excludingId: null, cancellationToken);

            if (domainExists)
            {
                throw new ConflictException("A whitelist entry with this domain already exists.");
            }

            entry = EmailWhitelist.ForDomain(normalizedDomain, adminId);
        }

        await _whitelistRepository.AddAsync(entry, cancellationToken);

        await _unitOfWork.SaveChangesAsync(cancellationToken);

        _logger.LogInformation(
            "Whitelist entry created. " +
            "EntryId: {EntryId}, " +
            "EntryType: {EntryType}, " +
            "PerformedBy: {AdminId}",
            entry.Id,
            GetEntryType(entry),
            adminId);

        return MapToResponse(entry);
    }

    public async Task<WhitelistResponse> UpdateAsync(
        Guid id,
        UpdateWhitelistRequest request,
        CancellationToken cancellationToken = default )
    {
        EnsureExclusiveEntry(request.Email, request.Domain);

        var adminId = RequireCurrentUserId();

        var entry = await _whitelistRepository.GetByIdAsync(id, cancellationToken);

        if (entry is null)
        {
            throw new NotFoundException("Whitelist entry was not found.");
        }

        if (!string.IsNullOrWhiteSpace(request.Email))
        {
            var normalizedEmail = NormalizeEmail(request.Email);

            var emailExists = await _whitelistRepository.EmailExistsAsync(
                    normalizedEmail,
                    excludingId: id,
                    cancellationToken);

            if (emailExists)
            {
                throw new ConflictException("A whitelist entry with this email already exists.");
            }

            entry.UpdateEmail(normalizedEmail);
        }
        else
        {
            var normalizedDomain = NormalizeDomain(request.Domain!);

            var domainExists = await _whitelistRepository.DomainExistsAsync(
                    normalizedDomain,
                    excludingId: id,
                    cancellationToken);

            if (domainExists)
            {
                throw new ConflictException("A whitelist entry with this domain already exists.");
            }

            entry.UpdateDomain(normalizedDomain);
        }

        await _unitOfWork.SaveChangesAsync(cancellationToken);

        _logger.LogInformation(
            "Whitelist entry updated. " +
            "EntryId: {EntryId}, " +
            "EntryType: {EntryType}, " +
            "PerformedBy: {AdminId}",
            entry.Id,
            GetEntryType(entry),
            adminId);

        return MapToResponse(entry);
    }

    public async Task ActivateAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        var adminId = RequireCurrentUserId();

        var entry = await _whitelistRepository.GetByIdAsync(id, cancellationToken);

        if (entry is null)
        {
            throw new NotFoundException("Whitelist entry was not found.");
        }

        entry.Activate();

        await _unitOfWork.SaveChangesAsync(cancellationToken);

        _logger.LogInformation(
            "Whitelist entry activated. " +
            "EntryId: {EntryId}, " +
            "PerformedBy: {AdminId}",
            entry.Id,
            adminId);
    }

    public async Task DeactivateAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        var adminId = RequireCurrentUserId();

        var entry = await _whitelistRepository.GetByIdAsync(id, cancellationToken);

        if (entry is null)
        {
            throw new NotFoundException("Whitelist entry was not found.");
        }

        entry.Deactivate();

        await _unitOfWork.SaveChangesAsync(cancellationToken);

        _logger.LogInformation(
            "Whitelist entry deactivated. " +
            "EntryId: {EntryId}, " +
            "PerformedBy: {AdminId}",
            entry.Id,
            adminId);
    }

    public async Task DeleteAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        var adminId = RequireCurrentUserId();

        var entry = await _whitelistRepository.GetByIdAsync(id, cancellationToken);

        if (entry is null)
        {
            throw new NotFoundException("Whitelist entry was not found.");
        }

        _whitelistRepository.Delete(entry);

        await _unitOfWork.SaveChangesAsync(cancellationToken);

        _logger.LogInformation(
            "Whitelist entry deleted. " +
            "EntryId: {EntryId}, " +
            "PerformedBy: {AdminId}",
            entry.Id,
            adminId);
    }

    private Guid RequireCurrentUserId()
    {
        if (!_currentUser.IsAuthenticated ||
            _currentUser.UserId == Guid.Empty)
        {
            throw new UnauthorizedAccessException("Authentication is required.");
        }

        return _currentUser.UserId;
    }

    private static void EnsureExclusiveEntry(
        string? email,
        string? domain )
    {
        var hasEmail = !string.IsNullOrWhiteSpace(email);

        var hasDomain = !string.IsNullOrWhiteSpace(domain);

        if (hasEmail == hasDomain)
        {
            throw new ArgumentException("Exactly one of Email or Domain must be provided.");
        }
    }

    private static string NormalizeEmail( string email )
    {
        return email
            .Trim()
            .ToLowerInvariant();
    }

    private static string NormalizeDomain( string domain )
    {
        return domain
            .Trim()
            .TrimStart('@')
            .ToLowerInvariant();
    }

    private static string GetEntryType( EmailWhitelist entry )
    {
        return entry.Email is not null
            ? "Email"
            : "Domain";
    }

    private static WhitelistResponse MapToResponse( EmailWhitelist entry )
        => new(
            entry.Id,
            entry.Email,
            entry.Domain,
            entry.IsActive,
            entry.CreatedBy,
            entry.CreatedAt,
            entry.UpdatedAt);
}