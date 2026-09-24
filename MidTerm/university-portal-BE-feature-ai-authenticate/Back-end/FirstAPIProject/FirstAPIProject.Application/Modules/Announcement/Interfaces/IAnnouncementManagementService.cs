using FirstAPIProject.Application.Modules.Announcement.DTOs;

namespace FirstAPIProject.Application.Modules.Announcement.Interfaces
{
    public interface IAnnouncementManagementService
    {
        Task<Guid> CreateAsync(
            CreateAnnouncementRequest request,
            Guid createdBy );

        Task UpdateAsync(
            Guid id,
            UpdateAnnouncementRequest request );

        Task PublishAsync( Guid id );

        Task ArchiveAsync( Guid id );

        Task DeleteAsync( Guid id );
    }
}