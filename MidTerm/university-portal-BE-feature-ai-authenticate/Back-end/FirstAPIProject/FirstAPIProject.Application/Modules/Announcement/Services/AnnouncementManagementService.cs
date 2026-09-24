using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Modules.Announcement.DTOs;
using FirstAPIProject.Application.Modules.Announcement.Interfaces;
//using FirstAPIProject.Infrastructure.Persistence.Repositories;

namespace FirstAPIProject.Application.Modules.Announcement.Services;

public sealed class AnnouncementManagementService
    : IAnnouncementManagementService
{
    private readonly IAnnouncementRepository _announcementRepository;
    private readonly IUnitOfWork _unitOfWork;

    public AnnouncementManagementService(
        IAnnouncementRepository announcementRepository,
        IUnitOfWork unitOfWork )
    {
        _announcementRepository = announcementRepository;
        _unitOfWork = unitOfWork;
    }

    public async Task<Guid> CreateAsync(
        CreateAnnouncementRequest request,
        Guid createdBy )
    {

        var announcement = Domain.Entities.Announcement.Create(
            request.Title,
            request.Content,
            request.Audience,
            createdBy);

        await _announcementRepository.AddAsync(announcement);

        await _unitOfWork.SaveChangesAsync();

        return announcement.Id;
    }

    public async Task UpdateAsync(
        Guid id,
        UpdateAnnouncementRequest request )
    {
        var announcement =
            await _announcementRepository.GetByIdAsync(id);

        if (announcement is null)
        {
            throw new KeyNotFoundException(
                $"Announcement {id} was not found.");
        }

        announcement.Update(
            request.Title,
            request.Content,
            request.Audience);

        await _unitOfWork.SaveChangesAsync();
    }

    public async Task PublishAsync( Guid id )
    {
        var announcement =
            await _announcementRepository.GetByIdAsync(id);

        if (announcement is null)
        {
            throw new KeyNotFoundException(
                $"Announcement {id} was not found.");
        }

        announcement.Publish();

        await _unitOfWork.SaveChangesAsync();
    }

    public async Task ArchiveAsync( Guid id )
    {
        var announcement =
            await _announcementRepository.GetByIdAsync(id);

        if (announcement is null)
        {
            throw new KeyNotFoundException(
                $"Announcement {id} was not found.");
        }

        announcement.Archive();

        await _unitOfWork.SaveChangesAsync();
    }

    public async Task DeleteAsync( Guid id )
    {
        var announcement =
            await _announcementRepository.GetByIdAsync(id);

        if (announcement is null)
        {
            throw new KeyNotFoundException(
                $"Announcement {id} was not found.");
        }

        announcement.SoftDelete(DateTimeOffset.UtcNow);

        await _unitOfWork.SaveChangesAsync();
    }
}