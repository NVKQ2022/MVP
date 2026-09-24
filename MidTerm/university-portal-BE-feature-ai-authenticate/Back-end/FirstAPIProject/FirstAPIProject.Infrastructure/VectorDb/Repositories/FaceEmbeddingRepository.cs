using System.Text.Json.Nodes;
using FirstAPIProject.Application.Modules.Auth.DTOs;
using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Domain.Entities;
using FirstAPIProject.Infrastructure.VectorDb.Clients;

namespace FirstAPIProject.Infrastructure.VectorDb.Repositories
{
    public sealed class FaceEmbeddingRepository
        : IFaceEmbeddingRepository
    {
        private readonly float threshold = 0.45f;

        private readonly IVectorSearchClient _vectorSearchClient;

        public FaceEmbeddingRepository(
            IVectorSearchClient vectorSearchClient)
        {
            _vectorSearchClient = vectorSearchClient;
        }

        public async Task StoreAsync(
            FaceEmbedding embedding,
            CancellationToken cancellationToken = default)
        {
            var payload = new Dictionary<string, object>
            {
                ["userId"] = embedding.UserId.ToString(),
                ["dimension"] = embedding.Dimension,
                ["createdAt"] = embedding.CreatedAt.ToString("O")
            };

            await _vectorSearchClient.UpsertAsync(
                pointId: embedding.UserId,
                vector: embedding.Embedding,
                payload: payload,
                cancellationToken);
        }

        public async Task<FaceEmbedding?> GetByUserIdAsync(
            Guid userId,
            CancellationToken cancellationToken = default)
        {
            var record = await _vectorSearchClient.GetAsync(
                userId,
                cancellationToken);

            if (record is null)
            {
                return null;
            }

            return new FaceEmbedding(
                userId,
                record.Vector);
        }

        public Task DeleteAsync(
            Guid userId,
            CancellationToken cancellationToken = default)
        {
            return _vectorSearchClient.DeleteAsync(
                userId,
                cancellationToken);
        }

        public async Task<FaceMatchResult?> FindBestMatchAsync(
            float[] embedding,
            CancellationToken cancellationToken = default)
        {
            var result =
                await _vectorSearchClient.SearchAsync(
                    embedding,
                    threshold,
                    cancellationToken);

            if (result is null)
            {
                return null;
            }

            var userId =
                result.Payload["userId"].ToString();

            if (string.IsNullOrWhiteSpace(userId))
            {
                return null;
            }

            return new FaceMatchResult
            {
                UserId = Guid.Parse(userId),
                Score = result.Score
            };
        }
    }
}