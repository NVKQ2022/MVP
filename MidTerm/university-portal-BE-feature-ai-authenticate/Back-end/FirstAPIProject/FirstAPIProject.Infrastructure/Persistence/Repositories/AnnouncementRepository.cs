using FirstAPIProject.Application.Modules.Announcement.Interfaces;
using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace FirstAPIProject.Infrastructure.Persistence.Repositories
{
    internal class AnnouncementRepository : IAnnouncementRepository
    {
        private readonly AppDbContext _dbContext;

        public AnnouncementRepository( AppDbContext dbContext )
        {
            _dbContext = dbContext;
        }

        public async Task<Announcement?> GetByIdAsync( Guid id )
        {
            return await _dbContext.Announcements
                .FirstOrDefaultAsync(x => x.Id == id);
        }

        public IQueryable<Announcement> GetQueryable()
        {
            return _dbContext.Announcements.AsQueryable();
        }

        public async Task AddAsync( Announcement announcement )
        {
            await _dbContext.Announcements.AddAsync(announcement);
        }

        public Task UpdateAsync( Announcement announcement )
        {
            _dbContext.Announcements.Update(announcement);

            return Task.CompletedTask;
        }

        public void Remove( Announcement announcement )
        {
            _dbContext.Announcements.Remove(announcement);
        }
    }
}
