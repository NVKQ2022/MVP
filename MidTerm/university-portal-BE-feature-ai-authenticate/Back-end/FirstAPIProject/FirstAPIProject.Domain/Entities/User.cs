using FirstAPIProject.Domain.Common.Enums;

namespace FirstAPIProject.Domain.Entities;

public sealed class User : LifecycleEntity
{
    public string? UserName { get; private set; }
    public string Email { get; private set; } = null!;
    public string? PhoneNumber { get; private set; }
    public string? Address { get; private set; }
    public Gender? Gender { get; private set; }
    public DateOnly? DateOfBirth { get; private set; }
    public string? AvatarUrl { get; private set; }
    public DateTimeOffset? LastLoginAt { get; private set; }
    public string PasswordHash { get; private set; } = null!;
    public UserStatus Status { get; private set; }

    public bool IsEmailVerified { get; private set; }
    public DateTimeOffset EmailVerifiedAt { get; private set; }

    public bool IsMfaEnabled { get; private set; }
    public MfaMethod? MfaMethod { get; private set; }

    public Guid RoleId { get; private set; }
    public Role Role { get; private set; } = null!;

    public ICollection<RefreshToken> RefreshTokens { get; private set; }
        = new List<RefreshToken>();
    public ICollection<AnnouncementRead> AnnouncementReads { get; private set; }

        = new List<AnnouncementRead>();

    private User()
    {
    }

    private User(
        string email,
        string passwordHash,
        Guid roleId,
        string? userName,
        string? phoneNumber )
    {
        Email = NormalizeEmail(email);
        PasswordHash = RequireValue(passwordHash, nameof(passwordHash));
        RoleId = roleId;
        UserName = NormalizeNullable(userName);
        PhoneNumber = NormalizeNullable(phoneNumber);
        Status = UserStatus.Normal;
        IsEmailVerified = false;
        IsMfaEnabled = false;
    }

    private static readonly Guid DefaultRoleId = Constants.SystemRoleIds.Student;

    public static User Create(
        string email,
        string passwordHash,
        Guid? roleId = null,
        string? userName = null,
        string? phoneNumber = null )
    {
        roleId ??= DefaultRoleId;

        return new User(
            email,
            passwordHash,
            roleId.Value,
            userName,
            phoneNumber);
    }

    public void UpdateProfile(
        string? userName,
        string? phoneNumber,
        string? address,
        Gender? gender,
        DateOnly? dateOfBirth )
    {
        EnsureNotDeleted();

        if (dateOfBirth.HasValue && dateOfBirth.Value > DateOnly.FromDateTime(DateTime.UtcNow))
        {
            throw new ArgumentException("Date of birth cannot be in the future.");
        }

        UserName = NormalizeNullable(userName);
        PhoneNumber = NormalizeNullable(phoneNumber);
        Address = NormalizeNullable(address);
        Gender = gender;
        DateOfBirth = dateOfBirth;
    }

    public void UpdateAvatar( string? avatarUrl )
    {
        EnsureNotDeleted();
        AvatarUrl = NormalizeNullable(avatarUrl);
    }

    public void AssignRole( Guid roleId )
    {
        EnsureNotDeleted();

        if (roleId == Guid.Empty)
        {
            throw new ArgumentException("Role is required.", nameof(roleId));
        }

        RoleId = roleId;
    }

    public void Lock()
    {
        EnsureNotDeleted();
        Status = UserStatus.Locked;
    }

    public void Unlock()
    {
        EnsureNotDeleted();
        Status = UserStatus.Normal;
    }

    public void ChangePassword( string passwordHash )
    {
        EnsureNotDeleted();
        PasswordHash = RequireValue(passwordHash, nameof(passwordHash));
    }

    public void ChangeEmail( string email )
    {
        EnsureNotDeleted();
        Email = NormalizeEmail(email);
    }

    public void RecordLogin( DateTimeOffset? loginTime = null )
    {
        EnsureNotDeleted();
        LastLoginAt = loginTime ?? DateTimeOffset.UtcNow;
    }

    public void VerifyEmail()
    {
        EnsureNotDeleted();

        IsEmailVerified = true; 

        EmailVerifiedAt = DateTimeOffset.UtcNow;
    }

    public void EnableMfa(MfaMethod method)
    {
        EnsureNotDeleted();

        IsMfaEnabled = true;
        MfaMethod = method;
    }

    public void DisableMfa()
    {
        EnsureNotDeleted();

        IsMfaEnabled = false;
        MfaMethod = null;
    }

    private static string NormalizeEmail( string email )
    {
        if (string.IsNullOrWhiteSpace(email))
        {
            throw new ArgumentException("Email is required.", nameof(email));
        }

        return email.Trim().ToLowerInvariant();
    }

    private static string RequireValue( string value, string parameterName )
    {
        if (string.IsNullOrWhiteSpace(value))
        {
            throw new ArgumentException("Value is required.", parameterName);
        }

        return value;
    }

    private static string? NormalizeNullable( string? value ) =>
        string.IsNullOrWhiteSpace(value) ? null : value.Trim();
}
