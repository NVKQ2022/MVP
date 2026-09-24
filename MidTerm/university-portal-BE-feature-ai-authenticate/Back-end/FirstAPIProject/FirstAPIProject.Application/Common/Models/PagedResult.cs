namespace FirstAPIProject.Application.Common.Models;

public sealed record PagedResultUserRepo<T>(
    IReadOnlyList<T> Items,
    int TotalCount,
    int Page,
    int PageSize );


public sealed class PagedResult<T>
{
    public IReadOnlyCollection<T> Items { get; set; }
        = [];

    public int TotalCount { get; set; }

    public int PageNumber { get; set; }

    public int PageSize { get; set; }

    public int TotalPages =>
    PageSize <= 0 ? 0 : (int)Math.Ceiling(TotalCount / (double)PageSize);
}
