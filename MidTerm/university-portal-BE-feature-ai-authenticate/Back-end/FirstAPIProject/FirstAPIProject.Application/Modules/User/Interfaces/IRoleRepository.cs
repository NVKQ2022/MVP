using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Domain.Entities;

namespace FirstAPIProject.Application.Modules.User.Interfaces;

public interface IRoleRepository : IGenericRepository<Role>
{
    Task<Role?> GetByNameAsync(
        string name,
        CancellationToken cancellationToken = default );
}
