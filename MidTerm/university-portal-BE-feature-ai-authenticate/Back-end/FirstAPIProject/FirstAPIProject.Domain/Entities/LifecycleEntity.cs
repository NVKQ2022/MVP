using FirstAPIProject.Domain.Common.Interfaces;

namespace FirstAPIProject.Domain.Entities;

public abstract class LifecycleEntity : BaseEntity, IActivatable, IDeletable
{
    public bool IsActive { get; private set; }

    public bool IsDeleted { get; private set; }

    public DateTimeOffset? DeletedAt { get; private set; }

    protected LifecycleEntity()
    {
        IsActive = false;
        IsDeleted = false;
    }

    public void Activate()
    {
        EnsureNotDeleted();
        IsActive = true;
    }

    public void Deactivate()
    {
        EnsureNotDeleted();
        IsActive = false;
    }

    public void SoftDelete( DateTimeOffset deletedAt )
    {
        if (IsDeleted)
        {
            return;
        }

        IsDeleted = true;
        IsActive = false;
        DeletedAt = deletedAt;
    }

    public void Restore()
    {
        if (!IsDeleted)
        {
            return;
        }

        IsDeleted = false;
        DeletedAt = null;
    }

    protected void EnsureNotDeleted()
    {
        if (IsDeleted)
        {
            throw new InvalidOperationException("The entity has been deleted.");

        }
    }
}
