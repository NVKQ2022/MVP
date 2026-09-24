using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Domain.Common.Enums;
using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace FirstAPIProject.Infrastructure.Persistence.Repositories;

public sealed class OtpVerificationRepository : GenericRepository<OtpVerification>, IOtpVerificationRepository
{
    public OtpVerificationRepository(AppDbContext context) : base(context)
    {
    }

    public async Task<OtpVerification?> GetLatestAsync(Guid userId, CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(x => x.UserId == userId)
            .OrderByDescending(x => x.CreatedAt)
            .FirstOrDefaultAsync(cancellationToken);
    }

    public async Task<OtpVerification?> GetLatestByPurposeAsync(
        Guid userId,
        OtpPurpose purpose,
        CancellationToken cancellationToken = default)
    {
        return await _dbSet
            .Where(x =>
                x.UserId == userId &&
                x.Purpose == purpose)
            .OrderByDescending(x => x.CreatedAt)
            .FirstOrDefaultAsync(cancellationToken);
    }
}