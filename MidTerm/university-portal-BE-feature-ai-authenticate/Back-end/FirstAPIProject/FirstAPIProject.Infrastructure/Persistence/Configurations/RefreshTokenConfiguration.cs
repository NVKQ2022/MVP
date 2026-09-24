using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Infrastructure.Persistence.Configurations
{
    public class RefreshTokenConfiguration : IEntityTypeConfiguration<RefreshToken>
    {
        public void Configure(EntityTypeBuilder<RefreshToken> builder)
        {
            builder.ToTable("RefreshTokens");

            // Primary Key
            builder.HasKey(x => x.Id);

            builder.Property(x => x.UserId)
                .IsRequired();

            builder.Property(x => x.TokenHash)
                .IsRequired()
                .HasMaxLength(500);

            builder.Property(x => x.ExpiresAt)
                .IsRequired();

            builder.Property(x => x.RevokedAt)
                .IsRequired(false);

            builder.Property(x => x.ReplacedByTokenHash)
                .IsRequired(false)
                .HasMaxLength(500);

            // Relationship:
            // User 1 ---- N RefreshToken
            builder.HasOne(x => x.User)
                .WithMany(x => x.RefreshTokens)
                .HasForeignKey(x => x.UserId)
                .OnDelete(DeleteBehavior.Cascade);

            // A refresh token hash must be unique.
            builder.HasIndex(x => x.TokenHash)
                .IsUnique();

            // Useful for finding all tokens belonging to a user.
            builder.HasIndex(x => x.UserId);
        }
    }
}
