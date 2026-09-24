using System;
using System.Collections.Generic;
using System.Text;
using FirstAPIProject.Domain.Common.Enums;

namespace FirstAPIProject.Domain.Entities;

public sealed class OtpVerification : BaseEntity
{
    public Guid UserId { get; private set; }

    public string CodeHash { get; private set; } = null!;

    public OtpPurpose Purpose { get; private set; }

    public DateTimeOffset ExpiresAt { get; private set; }

    public DateTimeOffset? VerifiedAt { get; private set; }

    public int AttemptCount { get; private set; }

    public User User { get; private set; } = null!;

    private OtpVerification()
    {

    }

    private OtpVerification(
        Guid userId,
        string codeHash,
        OtpPurpose purpose,
        DateTimeOffset expiresAt)
    {
        UserId = userId;
        CodeHash = codeHash;
        Purpose = purpose;
        ExpiresAt = expiresAt;
        AttemptCount = 0;
    }

    public static OtpVerification Create(
        Guid userId,
        string codeHash,
        OtpPurpose purpose,
        int expireMinutes = 5)
    {
        return new OtpVerification(
            userId,
            codeHash,
            purpose,
            DateTimeOffset.UtcNow.AddMinutes(expireMinutes));
    }

    public void MarkAsVerified()
    {
        VerifiedAt = DateTimeOffset.UtcNow;
    }
}

