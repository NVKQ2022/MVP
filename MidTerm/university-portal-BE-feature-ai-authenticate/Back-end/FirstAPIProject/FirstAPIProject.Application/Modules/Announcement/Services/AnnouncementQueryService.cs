using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.Announcement.DTOs;
using FirstAPIProject.Application.Modules.Announcement.Interfaces;
using Microsoft.EntityFrameworkCore;

namespace FirstAPIProject.Application.Modules.Announcement.Services;

public sealed class AnnouncementQueryService
    : IAnnouncementQueryService
{
    private readonly IAnnouncementRepository _announcementRepository;

    public AnnouncementQueryService(
        IAnnouncementRepository announcementRepository )
    {
        _announcementRepository = announcementRepository;
    }

    public async Task<PagedResult<AnnouncementSummaryResponse>>
        GetAnnouncementsAsync(
            AnnouncementQueryRequest query,
            Guid currentUserId )
    {
        var announcements = _announcementRepository
            .GetQueryable()
            .Include(x => x.Creator)
            .Include(x => x.ReadRecords)
            .Where(x => !x.IsDeleted);

        // Keyword Filter
        if (!string.IsNullOrWhiteSpace(query.Keyword))
        {
            announcements = announcements.Where(x =>
                x.Title.Contains(query.Keyword) ||
                x.Content.Contains(query.Keyword));
        }

        // Audience Filter
        if (query.Audience.HasValue)
        {
            announcements = announcements.Where(x =>
                x.Audience == query.Audience.Value);
        }

        // Publication Status Filter
        if (query.PublicationStatus.HasValue)
        {
            announcements = announcements.Where(x =>
                x.PublicationStatus ==
                query.PublicationStatus.Value);
        }

        var totalCount = await announcements.CountAsync();

        var items = await announcements
            .OrderByDescending(x => x.CreatedAt)
            .Skip((query.PageNumber - 1) * query.PageSize)
            .Take(query.PageSize)
            .Select(x => new AnnouncementSummaryResponse
            {
                Id = x.Id,
                Title = x.Title,

                CreatorName =
                    x.Creator.UserName ?? x.Creator.Email,

                PublicationStatus =
                    x.PublicationStatus,

                PublishedAt =
                    x.PublishedAt,

                IsRead = x.ReadRecords
                    .Any(r => r.UserId == currentUserId)
            })
            .ToListAsync();

        return new PagedResult<AnnouncementSummaryResponse>
        {
            Items = items,
            TotalCount = totalCount,
            PageNumber = query.PageNumber,
            PageSize = query.PageSize
        };
    }

    public async Task<AnnouncementDetailResponse>
        GetByIdAsync(
            Guid id,
            Guid currentUserId )
    {
        var announcement = await _announcementRepository
            .GetQueryable()
            .Include(x => x.Creator)
            .FirstOrDefaultAsync(x =>
                x.Id == id &&
                !x.IsDeleted);

        if (announcement is null)
        {
            throw new KeyNotFoundException(
                $"Announcement '{id}' was not found.");
        }

        return new AnnouncementDetailResponse
        {
            Id = announcement.Id,
            Title = announcement.Title,
            Content = announcement.Content,
            Audience = announcement.Audience,
            PublicationStatus = announcement.PublicationStatus,
            CreatedBy = announcement.CreatedBy,
            CreatorName = announcement.Creator.UserName ?? announcement.Creator.Email,
            PublishedAt = announcement.PublishedAt,
            CreatedAt = announcement.CreatedAt,
            UpdatedAt = announcement.UpdatedAt
        };
    }

    public async Task<PagedResult<AnnouncementSummaryResponse>>
    GetAdminAnnouncementsAsync(
        AnnouncementQueryRequest query )
    {
        var announcements = _announcementRepository
            .GetQueryable()
            .Include(x => x.Creator)
            .Include(x => x.ReadRecords)
            .Where(x => !x.IsDeleted);

        if (!string.IsNullOrWhiteSpace(query.Keyword))
        {
            announcements = announcements.Where(x =>
                x.Title.Contains(query.Keyword) ||
                x.Content.Contains(query.Keyword));
        }

        if (query.Audience.HasValue)
        {
            announcements = announcements.Where(x =>
                x.Audience == query.Audience.Value);
        }

        if (query.PublicationStatus.HasValue)
        {
            announcements = announcements.Where(x =>
                x.PublicationStatus ==
                query.PublicationStatus.Value);
        }

        var totalCount = await announcements.CountAsync();

        var items = await announcements
            .OrderByDescending(x => x.CreatedAt)
            .Skip((query.PageNumber - 1) * query.PageSize)
            .Take(query.PageSize)
            .Select(x => new AnnouncementSummaryResponse
            {
                Id = x.Id,
                Title = x.Title,
                CreatorName = x.Creator.UserName ?? x.Creator.Email,
                PublicationStatus = x.PublicationStatus,
                PublishedAt = x.PublishedAt,

                // Admin can still see read status
                IsRead = x.ReadRecords.Any()
            })
            .ToListAsync();

        return new PagedResult<AnnouncementSummaryResponse>
        {
            Items = items,
            TotalCount = totalCount,
            PageNumber = query.PageNumber,
            PageSize = query.PageSize
        };
    }

    public async Task<AnnouncementDetailResponse>
    GetAdminAnnouncementByIdAsync( Guid id )
    {
        var announcement = await _announcementRepository
            .GetQueryable()
            .Include(x => x.Creator)
            .FirstOrDefaultAsync(x =>
                x.Id == id &&
                !x.IsDeleted);

        if (announcement is null)
        {
            throw new KeyNotFoundException(
                $"Announcement '{id}' was not found.");
        }

        return new AnnouncementDetailResponse
        {
            Id = announcement.Id,
            Title = announcement.Title,
            Content = announcement.Content,
            Audience = announcement.Audience,
            PublicationStatus = announcement.PublicationStatus,
            CreatedBy = announcement.CreatedBy,
            CreatorName = announcement.Creator.UserName ?? announcement.Creator.Email,
            PublishedAt = announcement.PublishedAt,
            CreatedAt = announcement.CreatedAt,
            UpdatedAt = announcement.UpdatedAt
        };
    }
}