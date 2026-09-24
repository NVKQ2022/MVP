
﻿namespace FirstAPIProject.Domain.Entities;

public abstract class BaseEntity
{
    public Guid Id { get; protected set; }
    public DateTimeOffset CreatedAt { get; protected set; }
    public DateTimeOffset UpdatedAt { get; protected set; }

    protected BaseEntity()
    {
        Id = Guid.NewGuid();
    }

    public void SetCreatedAt( DateTimeOffset createdAt )
    {
        CreatedAt = createdAt;
        UpdatedAt = createdAt;
    }

    public void SetUpdatedAt( DateTimeOffset updatedAt )
    {
        UpdatedAt = updatedAt;
    }
}
