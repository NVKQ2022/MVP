using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Metadata.Builders;


namespace FirstAPIProject.Infrastructure.Persistence.Configurations;


public sealed class OtpVerificationConfiguration
    : IEntityTypeConfiguration<OtpVerification>
{

    public void Configure(
        EntityTypeBuilder<OtpVerification> builder)
    {

        builder.HasKey(x => x.Id);


        builder.Property(x => x.CodeHash)
            .IsRequired();


        builder.HasOne(x => x.User)
            .WithMany()
            .HasForeignKey(x => x.UserId)
            .OnDelete(DeleteBehavior.Cascade);

    }
}
