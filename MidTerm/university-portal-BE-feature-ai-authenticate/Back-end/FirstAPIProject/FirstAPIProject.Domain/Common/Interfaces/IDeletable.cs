
﻿namespace FirstAPIProject.Domain.Common.Interfaces;

public interface IDeletable
{
    bool IsDeleted { get; }

    DateTimeOffset? DeletedAt { get; }

    void SoftDelete( DateTimeOffset deletedAt );

    void Restore();
}
