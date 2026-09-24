namespace FirstAPIProject.Application.Modules.Announcement.Interfaces;

public interface IAnnouncementReadService
{
    Task MarkAsReadAsync(
        Guid announcementId,
        Guid userId,
        CancellationToken cancellationToken = default );

    Task<bool> IsReadAsync(
        Guid announcementId,
        Guid userId,
        CancellationToken cancellationToken = default );

    Task<DateTimeOffset?> GetReadAtAsync(
        Guid announcementId,
        Guid userId,
        CancellationToken cancellationToken = default );
}
