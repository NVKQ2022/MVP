using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Infrastructure.Persistence
{
    public class AppDbContext : DbContext
    {
        public AppDbContext(DbContextOptions<AppDbContext> options) : base(options)
        {
        }

        public DbSet<User> Users => Set<User>();

        public DbSet<Role> Roles => Set<Role>();
        public DbSet<EmailWhitelist> EmailWhitelists => Set<EmailWhitelist>();
        public DbSet<Announcement> Announcements => Set<Announcement>();
        public DbSet<AnnouncementRead> AnnouncementReads => Set<AnnouncementRead>();
        public DbSet<OtpVerification> OtpVerifications => Set<OtpVerification>();

        public DbSet<RefreshToken> RefreshTokens => Set<RefreshToken>();

        protected override void OnModelCreating(
        ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);

            modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
        }
    }
}
