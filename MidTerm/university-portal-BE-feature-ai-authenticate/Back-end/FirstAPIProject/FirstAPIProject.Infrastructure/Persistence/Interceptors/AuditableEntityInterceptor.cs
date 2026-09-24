using FirstAPIProject.Domain.Entities;
using Microsoft.EntityFrameworkCore;
using Microsoft.EntityFrameworkCore.Diagnostics;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Infrastructure.Persistence.Interceptors
{
    public sealed class AuditableEntityInterceptor : SaveChangesInterceptor
    {
        public override InterceptionResult<int> SavingChanges(DbContextEventData eventData, InterceptionResult<int> result)
        {
            UpdateTimestamps(eventData.Context);

            return base.SavingChanges(eventData, result);
        }

        public override ValueTask<InterceptionResult<int>> SavingChangesAsync(
            DbContextEventData eventData,
            InterceptionResult<int> result,
            CancellationToken cancellationToken = default)
        {
            UpdateTimestamps(eventData.Context);

            return base.SavingChangesAsync(
                eventData,
                result,
                cancellationToken);
        }

        private static void UpdateTimestamps(DbContext? context)
        {
            if (context is null)
            {
                return;
            }

            var now = DateTime.UtcNow;

            foreach (var entry in context.ChangeTracker.Entries<BaseEntity>())
            {
                switch (entry.State)
                {
                    case EntityState.Added:

                        entry.Entity.SetCreatedAt(now);

                        break;

                    case EntityState.Modified:

                        entry.Entity.SetUpdatedAt(now);

                        // CreatedAt must never change after creation.
                        entry.Property(x => x.CreatedAt).IsModified = false;
                        break;
                }
            }
        }
    }
}
