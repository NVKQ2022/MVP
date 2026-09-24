using FirstAPIProject.Application.Modules.AnnouncementRead.Interfaces;
using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace FirstAPIProject.Infrastructure.Persistence.Repositories;

public sealed class AnnouncementReadRepository : IAnnouncementReadRepository
{
    private readonly AppDbContext _context;

    public AnnouncementReadRepository(
        AppDbContext context )
    {
        _context = context;
    }

    public Task<AnnouncementRead?>
        GetByUserAndAnnouncementAsync(
            Guid userId,
            Guid announcementId,
            CancellationToken cancellationToken = default )
    {
        return _context.AnnouncementReads
            .FirstOrDefaultAsync(
                x =>
                    x.UserId == userId &&
                    x.AnnouncementId == announcementId,
                cancellationToken);
    }

    public async Task AddAsync(
        AnnouncementRead announcementRead,
        CancellationToken cancellationToken = default )
    {
        await _context.AnnouncementReads.AddAsync(
            announcementRead,
            cancellationToken);
    }
}