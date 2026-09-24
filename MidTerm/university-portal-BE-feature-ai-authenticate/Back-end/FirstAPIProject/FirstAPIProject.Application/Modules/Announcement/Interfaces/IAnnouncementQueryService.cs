using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.Announcement.DTOs;

namespace FirstAPIProject.Application.Modules.Announcement.Interfaces
{
    public interface IAnnouncementQueryService
    {
        // Student
        Task<PagedResult<AnnouncementSummaryResponse>>
            GetAnnouncementsAsync(
                AnnouncementQueryRequest query,
                Guid currentUserId );

        Task<AnnouncementDetailResponse>
            GetByIdAsync(
                Guid id,
                Guid currentUserId );

        // Admin
        Task<PagedResult<AnnouncementSummaryResponse>>
            GetAdminAnnouncementsAsync(
                AnnouncementQueryRequest query );

        Task<AnnouncementDetailResponse>
            GetAdminAnnouncementByIdAsync(
                Guid id );
    }
}
