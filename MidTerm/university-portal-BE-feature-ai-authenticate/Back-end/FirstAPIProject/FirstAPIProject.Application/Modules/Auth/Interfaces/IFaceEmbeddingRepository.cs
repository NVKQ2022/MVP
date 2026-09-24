using FirstAPIProject.Application.Modules.Auth.DTOs;
using FirstAPIProject.Domain.Entities;

namespace FirstAPIProject.Application.Modules.Auth.Interfaces
{
    public interface IFaceEmbeddingRepository
    {
        Task StoreAsync(
            FaceEmbedding embedding,
            CancellationToken cancellationToken = default);

        Task<FaceEmbedding?> GetByUserIdAsync(
            Guid userId,
            CancellationToken cancellationToken = default);

        Task DeleteAsync(
            Guid userId,
            CancellationToken cancellationToken = default);

        Task<FaceMatchResult?> FindBestMatchAsync(
            float[] embedding,
            CancellationToken cancellationToken = default);
    }
}