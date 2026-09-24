namespace FirstAPIProject.Domain.Entities;

public sealed class Role : BaseEntity
{
    public string Name { get; private set; } = null!;
    public string? Description { get; private set; }

    public ICollection<User> Users { get; private set; } = new List<User>();

    private Role()
    {
    }

    public Role( string name, string? description = null )
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            throw new ArgumentException("Role name is required.", nameof(name));
        }

        Name = name.Trim();
        Description = NormalizeNullable(description);
    }

    public void Update( string name, string? description )
    {
        if (string.IsNullOrWhiteSpace(name))
        {
            throw new ArgumentException("Role name is required.", nameof(name));
        }

        Name = name.Trim();
        Description = NormalizeNullable(description);
    }

    private static string? NormalizeNullable( string? value ) =>
        string.IsNullOrWhiteSpace(value) ? null : value.Trim();
}