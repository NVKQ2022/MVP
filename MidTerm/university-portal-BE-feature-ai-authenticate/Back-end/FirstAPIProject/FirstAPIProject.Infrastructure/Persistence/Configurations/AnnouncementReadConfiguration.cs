using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace FirstAPIProject.Infrastructure.Persistence.Configurations
{
    public class AnnouncementReadConfiguration
        : IEntityTypeConfiguration<AnnouncementRead>
    {
        public void Configure(
            EntityTypeBuilder<AnnouncementRead> builder)
        {
            // Table
            builder.ToTable("AnnouncementReads");

            // Composite primary key
            // A user can read an announcement only once.
            builder.HasKey(x => new
            {
                x.UserId,
                x.AnnouncementId
            });

            // ReadAt
            builder.Property(x => x.ReadAt)
                .IsRequired();

            // AnnouncementRead -> User
            builder.HasOne(x => x.User)
                .WithMany(x => x.AnnouncementReads)
                .HasForeignKey(x => x.UserId)
                .OnDelete(DeleteBehavior.Cascade);

            // AnnouncementRead -> Announcement
            builder.HasOne(x => x.Announcement)
                .WithMany(x => x.ReadRecords)
                .HasForeignKey(x => x.AnnouncementId)
                .OnDelete(DeleteBehavior.Cascade);
        }
    }
}
