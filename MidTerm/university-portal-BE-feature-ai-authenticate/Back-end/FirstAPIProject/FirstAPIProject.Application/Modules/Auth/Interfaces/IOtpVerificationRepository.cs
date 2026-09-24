using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Domain.Entities;

namespace FirstAPIProject.Application.Modules.Auth.Interfaces;

public interface IOtpVerificationRepository : IGenericRepository<OtpVerification>
{
    Task<OtpVerification?> GetLatestAsync(Guid userId, CancellationToken cancellationToken = default);

    Task<OtpVerification?> GetLatestByPurposeAsync(Guid userId, Domain.Common.Enums.OtpPurpose purpose, CancellationToken cancellationToken = default);
}
