using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.User.Models;
using UserEntity = FirstAPIProject.Domain.Entities.User;


namespace FirstAPIProject.Application.Modules.User.Interfaces;

public interface IUserRepository : IGenericRepository<UserEntity>
{
    Task<UserEntity?> GetByEmailAsync(
        string email,
        CancellationToken cancellationToken = default );

    Task<UserEntity?> GetByIdWithRoleAsync(
        Guid id,
        CancellationToken cancellationToken = default );

    Task<PagedResultUserRepo<UserEntity>> GetPagedAsync(
        UserFilter filter,
        CancellationToken cancellationToken = default );

    Task<bool> EmailExistsAsync(
        string email,
        Guid? excludingUserId = null,
        CancellationToken cancellationToken = default );
}