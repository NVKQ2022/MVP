using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Modules.Announcement.Interfaces;
using FirstAPIProject.Application.Modules.AnnouncementRead.Interfaces;

using AnnouncementReadEntity = FirstAPIProject.Domain.Entities.AnnouncementRead;

namespace FirstAPIProject.Application.Modules.Announcement.Services;

public sealed class AnnouncementReadService
    : IAnnouncementReadService
{
    private readonly IAnnouncementReadRepository _repository;
    private readonly IUnitOfWork _unitOfWork;

    public AnnouncementReadService(
        IAnnouncementReadRepository repository,
        IUnitOfWork unitOfWork )
    {
        _repository = repository;
        _unitOfWork = unitOfWork;
    }

    public async Task MarkAsReadAsync(
        Guid announcementId,
        Guid userId,
        CancellationToken cancellationToken = default )
    {
        var existingRecord =
            await _repository.GetByUserAndAnnouncementAsync(
                userId,
                announcementId,
                cancellationToken);

        if (existingRecord is not null)
        {
            return;
        }

        var readRecord =
            AnnouncementReadEntity.Create(
                userId,
                announcementId);

        await _repository.AddAsync(
            readRecord,
            cancellationToken);

        await _unitOfWork.SaveChangesAsync(
            cancellationToken);
    }

    public async Task<bool> IsReadAsync(
        Guid announcementId,
        Guid userId,
        CancellationToken cancellationToken = default )
    {
        var record =
            await _repository.GetByUserAndAnnouncementAsync(
                userId,
                announcementId,
                cancellationToken);

        return record is not null;
    }

    public async Task<DateTimeOffset?> GetReadAtAsync(
        Guid announcementId,
        Guid userId,
        CancellationToken cancellationToken = default )
    {
        var record =
            await _repository.GetByUserAndAnnouncementAsync(
                userId,
                announcementId,
                cancellationToken);

        return record?.ReadAt;
    }
}