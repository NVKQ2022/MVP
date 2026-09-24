namespace FirstAPIProject.Domain.Entities;

public sealed class EmailWhitelist : BaseEntity
{
    public string? Email { get; private set; }
    public string? Domain { get; private set; }
    public bool IsActive { get; private set; }
    public Guid CreatedBy { get; private set; }
    public User Creator { get; private set; } = null!;

    private EmailWhitelist()
    {
    }

    public static EmailWhitelist ForEmail( string email, Guid createdBy )
    {
        EnsureCreator(createdBy);

        return new EmailWhitelist
        {
            Email = NormalizeEmail(email),
            Domain = null,
            IsActive = true,
            CreatedBy = createdBy
        };
    }

    public static EmailWhitelist ForDomain( string domain, Guid createdBy )
    {
        EnsureCreator(createdBy);

        return new EmailWhitelist
        {
            Email = null,
            Domain = NormalizeDomain(domain),
            IsActive = true,
            CreatedBy = createdBy
        };
    }

    public void UpdateEmail( string email )
    {
        Email = NormalizeEmail(email);
        Domain = null;
    }

    public void UpdateDomain( string domain )
    {
        Domain = NormalizeDomain(domain);
        Email = null;
    }

    public void Activate() => IsActive = true;
    public void Deactivate() => IsActive = false;

    private static void EnsureCreator( Guid createdBy )
    {
        if (createdBy == Guid.Empty)
        {
            throw new ArgumentException("Creator is required.", nameof(createdBy));
        }
    }

    private static string NormalizeEmail( string email )
    {
        if (string.IsNullOrWhiteSpace(email))
        {
            throw new ArgumentException("Email is required.", nameof(email));
        }

        return email.Trim().ToLowerInvariant();
    }

    private static string NormalizeDomain( string domain )
    {
        if (string.IsNullOrWhiteSpace(domain))
        {
            throw new ArgumentException("Domain is required.", nameof(domain));
        }

        return domain.Trim().TrimStart('@').ToLowerInvariant();
    }
}