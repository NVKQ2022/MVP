using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;

namespace FirstAPIProject.Infrastructure.Persistence.Configurations;

public sealed class EmailWhitelistConfiguration
    : IEntityTypeConfiguration<EmailWhitelist>
{
    public void Configure( EntityTypeBuilder<EmailWhitelist> builder )
    {
        builder.ToTable(
            "EmailWhitelists",
            table => table.HasCheckConstraint(
                "CK_EmailWhitelists_Email_Xor_Domain",
                "([Email] IS NOT NULL AND [Domain] IS NULL) OR " +
                "([Email] IS NULL AND [Domain] IS NOT NULL)"));

        builder.HasKey(x => x.Id);

        builder.Property(x => x.Email)
            .HasMaxLength(255);

        builder.Property(x => x.Domain)
            .HasMaxLength(255);

        builder.Property(x => x.IsActive)
            .IsRequired();

        builder.Property(x => x.CreatedBy)
            .IsRequired();

        builder.Property(x => x.CreatedAt).IsRequired();
        builder.Property(x => x.UpdatedAt).IsRequired();

        builder.HasIndex(x => x.Email)
            .IsUnique()
            .HasFilter("[Email] IS NOT NULL");

        builder.HasIndex(x => x.Domain)
            .IsUnique()
            .HasFilter("[Domain] IS NOT NULL");

        builder.HasIndex(x => x.IsActive);
        builder.HasIndex(x => x.CreatedBy);

        builder.HasOne(x => x.Creator)
            .WithMany()
            .HasForeignKey(x => x.CreatedBy)
            .OnDelete(DeleteBehavior.Restrict);
    }
}
