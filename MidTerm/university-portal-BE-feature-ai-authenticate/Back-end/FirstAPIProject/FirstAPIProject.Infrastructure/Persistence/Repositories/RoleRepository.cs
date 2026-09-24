using FirstAPIProject.Application.Modules.User.Interfaces;
using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace FirstAPIProject.Infrastructure.Persistence.Repositories;

public sealed class RoleRepository : GenericRepository<Role>, IRoleRepository
{
    public RoleRepository( AppDbContext context ) : base(context)
    {
    }

    public Task<Role?> GetByNameAsync( string name, CancellationToken cancellationToken = default )
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            throw new ArgumentException(
                "Role name is required.",
                nameof(name));
        }

        var normalizedName = name.Trim();

        return _dbSet
            .AsNoTracking()
            .FirstOrDefaultAsync(
                role => role.Name == normalizedName,
                cancellationToken);
    }
}
