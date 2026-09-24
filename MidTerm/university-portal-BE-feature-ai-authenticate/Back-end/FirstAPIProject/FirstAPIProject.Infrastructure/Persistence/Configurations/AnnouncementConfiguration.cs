using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace FirstAPIProject.Infrastructure.Persistence.Configurations
{
    public class AnnouncementConfiguration
        : IEntityTypeConfiguration<Announcement>
    {
        public void Configure(
            EntityTypeBuilder<Announcement> builder)
        {
            builder.ToTable("Announcements");

            // Primary Key
            builder.HasKey(x => x.Id);

            // Title
            builder.Property(x => x.Title)
                .IsRequired()
                .HasMaxLength(200);

            // Content
            builder.Property(x => x.Content)
                .IsRequired();

            // PublicationStatus
            builder.Property(x => x.PublicationStatus)
                .IsRequired();

            // Audience
            builder.Property(x => x.Audience)
                .IsRequired();

            // CreatedBy
            builder.Property(x => x.CreatedBy)
                .IsRequired();

            // PublishedAt
            builder.Property(x => x.PublishedAt)
                .IsRequired(false);

            // Announcement -> User
            builder.HasOne(x => x.Creator)
                .WithMany()
                .HasForeignKey(x => x.CreatedBy)
                .OnDelete(DeleteBehavior.Restrict);

            // Index for FK
            builder.HasIndex(x => x.CreatedBy);

            // Useful for filtering announcements
            builder.HasIndex(x => x.PublicationStatus);

            builder.HasIndex(x => x.Audience);
        }
    }
}
