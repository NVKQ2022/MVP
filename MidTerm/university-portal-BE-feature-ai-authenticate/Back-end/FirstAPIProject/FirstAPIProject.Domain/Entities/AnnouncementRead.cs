namespace FirstAPIProject.Domain.Entities;

public sealed class AnnouncementRead
{
    public Guid UserId { get; private set; }

    public Guid AnnouncementId { get; private set; }

    public DateTimeOffset ReadAt { get; private set; }

    public User User { get; private set; } = null!;

    public Announcement Announcement { get; private set; } = null!;

    private AnnouncementRead()
    {
    }

    private AnnouncementRead(
        Guid userId,
        Guid announcementId,
        DateTimeOffset readAt )
    {
        UserId = userId;
        AnnouncementId = announcementId;
        ReadAt = readAt;
    }

    public static AnnouncementRead Create(
        Guid userId,
        Guid announcementId )
    {
        return new AnnouncementRead(
            userId,
            announcementId,
            DateTimeOffset.UtcNow);
    }
}