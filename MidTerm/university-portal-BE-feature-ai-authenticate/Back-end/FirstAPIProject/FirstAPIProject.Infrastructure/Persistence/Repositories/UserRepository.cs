using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.User.Interfaces;
using FirstAPIProject.Application.Modules.User.Models;
using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace FirstAPIProject.Infrastructure.Persistence.Repositories;

public sealed class UserRepository
    : GenericRepository<User>, IUserRepository
{
    public UserRepository( AppDbContext context ) : base(context)
    {
    }

    public Task<User?> GetByEmailAsync(
        string email,
        CancellationToken cancellationToken = default )
    {
        var normalizedEmail = NormalizeEmail(email);

        return _dbSet
            .Include(user => user.Role)
            .FirstOrDefaultAsync(
                user => user.Email == normalizedEmail,
                cancellationToken);
    }

    public Task<bool> EmailExistsAsync(
        string email,
        Guid? excludingUserId = null,
        CancellationToken cancellationToken = default )
    {
        var normalizedEmail = NormalizeEmail(email);

        return _dbSet.AnyAsync(
            user =>
                user.Email == normalizedEmail &&
                (!excludingUserId.HasValue ||
                 user.Id != excludingUserId.Value),
            cancellationToken);
    }

    public Task<User?> GetByIdWithRoleAsync(
        Guid id,
        CancellationToken cancellationToken = default )
    {
        return _dbSet
            .Include(user => user.Role)
            .FirstOrDefaultAsync(
                user => user.Id == id,
                cancellationToken);
    }

    public async Task<PagedResultUserRepo<User>> GetPagedAsync(
        UserFilter filter,
        CancellationToken cancellationToken = default )
    {
        var page = filter.Page < 1
            ? 1
            : filter.Page;

        var pageSize = filter.PageSize switch
        {
            < 1 => 20,
            > 100 => 100,
            _ => filter.PageSize
        };

        IQueryable<User> query = _dbSet
            .AsNoTracking()
            .Include(user => user.Role);

        query = ApplyFilters(query, filter);

        var totalCount = await query.CountAsync(
            cancellationToken);

        var users = await query
            .OrderByDescending(user => user.CreatedAt)
            .ThenBy(user => user.Id)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync(cancellationToken);

        return new PagedResultUserRepo<User>(
            users,
            totalCount,
            page,
            pageSize);
    }

    private static IQueryable<User> ApplyFilters(
        IQueryable<User> query,
        UserFilter filter )
    {
        if (!string.IsNullOrWhiteSpace(filter.Search))
        {
            var search = filter.Search.Trim();

            query = query.Where(user =>
                user.Email.Contains(search) ||
                (user.UserName != null &&
                 user.UserName.Contains(search)) ||
                (user.PhoneNumber != null &&
                 user.PhoneNumber.Contains(search)));
        }

        if (filter.RoleId.HasValue)
        {
            query = query.Where(
                user => user.RoleId == filter.RoleId.Value);
        }

        if (filter.Status.HasValue)
        {
            query = query.Where(
                user => user.Status == filter.Status.Value);
        }

        if (filter.IsActive.HasValue)
        {
            query = query.Where(
                user => user.IsActive == filter.IsActive.Value);
        }

        return query;
    }

    private static string NormalizeEmail( string email )
    {
        if (string.IsNullOrWhiteSpace(email))
        {
            throw new ArgumentException(
                "Email is required.",
                nameof(email));
        }

        return email
            .Trim()
            .ToLowerInvariant();
    }
}
