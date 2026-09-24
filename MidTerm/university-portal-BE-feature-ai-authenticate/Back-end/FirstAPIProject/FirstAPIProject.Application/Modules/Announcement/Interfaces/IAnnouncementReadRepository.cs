using AnnouncementReadEntity = FirstAPIProject.Domain.Entities.AnnouncementRead;
namespace FirstAPIProject.Application.Modules.AnnouncementRead.Interfaces;

public interface IAnnouncementReadRepository
{
    Task<AnnouncementReadEntity?>
        GetByUserAndAnnouncementAsync(
            Guid userId,
            Guid announcementId,
            CancellationToken cancellationToken = default );

    Task AddAsync(
        AnnouncementReadEntity announcementRead,
        CancellationToken cancellationToken = default );
}