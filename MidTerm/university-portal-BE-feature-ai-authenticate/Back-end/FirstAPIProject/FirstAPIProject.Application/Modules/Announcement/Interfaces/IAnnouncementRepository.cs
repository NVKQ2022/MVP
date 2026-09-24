using System;
using System.Collections.Generic;
using System.Text;
using FirstAPIProject.Domain.Entities;
namespace FirstAPIProject.Application.Modules.Announcement.Interfaces
{
    public interface IAnnouncementRepository
    {
        Task<Domain.Entities.Announcement?> GetByIdAsync(Guid id);
        IQueryable<Domain.Entities.Announcement> GetQueryable();    
        

        Task AddAsync(Domain.Entities.Announcement announcement);

        Task UpdateAsync(Domain.Entities.Announcement announcement);

        void Remove(Domain.Entities.Announcement announcement);
    }
}
