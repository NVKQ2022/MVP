using FirstAPIProject.Infrastructure.VectorDb.Models;
using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Nodes;
namespace FirstAPIProject.Infrastructure.VectorDb.Clients
{


    public interface IVectorSearchClient
    {
        Task UpsertAsync(
            Guid pointId,
            float[] vector,
            Dictionary<string, object> payload,
            CancellationToken cancellationToken = default);

        Task DeleteAsync(
            Guid pointId,
            CancellationToken cancellationToken = default);

        Task<VectorRecord?> GetAsync(
            Guid pointId,
            CancellationToken cancellationToken = default);

        Task<VectorSearchResult?> SearchAsync(
            float[] vector,
            float? scoreThreshold = 0.8f,
            CancellationToken cancellationToken = default);
    }
}
