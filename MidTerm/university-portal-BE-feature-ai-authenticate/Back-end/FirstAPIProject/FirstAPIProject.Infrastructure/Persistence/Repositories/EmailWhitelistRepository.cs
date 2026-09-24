using FirstAPIProject.Application.Common.Models;
using FirstAPIProject.Application.Modules.Whitelist.Interfaces;
using FirstAPIProject.Application.Modules.Whitelist.Models;
using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;

namespace FirstAPIProject.Infrastructure.Persistence.Repositories;

public sealed class EmailWhitelistRepository : GenericRepository<EmailWhitelist>, IEmailWhitelistRepository
{
    public EmailWhitelistRepository( AppDbContext context ) : base(context)
    {
    }
    public async Task<PagedResult<EmailWhitelist>> GetPagedAsync(
        WhitelistFilter filter,
        CancellationToken cancellationToken = default )
    {
        var page = filter.Page < 1 ? 1 : filter.Page;
        var pageSize = filter.PageSize switch
        {
            < 1 => 20,
            > 100 => 100,
            _ => filter.PageSize
        };

        IQueryable<EmailWhitelist> query = _dbSet.AsNoTracking();

        if (!string.IsNullOrWhiteSpace(filter.Search))
        {
            var search = filter.Search.Trim().ToLowerInvariant();
            query = query.Where(x =>
                (x.Email != null && x.Email.Contains(search)) ||
                (x.Domain != null && x.Domain.Contains(search)));
        }

        if (filter.IsActive.HasValue)
        {
            query = query.Where(x => x.IsActive == filter.IsActive.Value);
        }

        var totalCount = await query.CountAsync(cancellationToken);

        var items = await query
            .OrderByDescending(x => x.CreatedAt)
            .Skip((page - 1) * pageSize)
            .Take(pageSize)
            .ToListAsync(cancellationToken);

        return new PagedResult<EmailWhitelist>
        {
            Items = items,
            TotalCount = totalCount,
            PageNumber = page,
            PageSize = pageSize
        };
    }
    public Task<bool> EmailExistsAsync(
        string normalizedEmail,
        Guid? excludingId = null,
        CancellationToken cancellationToken = default )
    {
        return _dbSet.AnyAsync(
            x => x.Email == normalizedEmail &&
                 (!excludingId.HasValue || x.Id != excludingId.Value),
            cancellationToken);
    }
    public Task<bool> DomainExistsAsync(
        string normalizedDomain,
        Guid? excludingId = null,
        CancellationToken cancellationToken = default )
    {
        return _dbSet.AnyAsync(
            x => x.Domain == normalizedDomain &&
                 (!excludingId.HasValue || x.Id != excludingId.Value),
            cancellationToken);
    }

    public async Task<bool> IsEmailAllowedAsync(
        string email,
        CancellationToken cancellationToken = default
        )
    {
        if (string.IsNullOrWhiteSpace(email))
        {
            return false;
        }

        var normalizedEmail = email.Trim().ToLowerInvariant();
        var atIndex = normalizedEmail.LastIndexOf("@");
        var domain = atIndex >= 0 && atIndex < normalizedEmail.Length - 1
            ? normalizedEmail[(atIndex + 1)..] : string.Empty;

        return await _dbSet.AnyAsync(
            x => x.IsActive && ((x.Email != null && x.Email == normalizedEmail) ||
                            (x.Domain != null && x.Domain == domain)),
            cancellationToken);

    }
}