using FirstAPIProject.Domain.Common.Enums;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Domain.Entities
{

    public sealed class FaceEmbedding
    {
        public Guid Id { get; private set; }

        public Guid UserId { get; private set; }

        public float[] Embedding { get; private set; } = [];

        public int Dimension { get; private set; }

        public DateTime CreatedAt { get; private set; }

        public DateTime? UpdatedAt { get; private set; }

        private FaceEmbedding()
        {
        }

        public FaceEmbedding(
            Guid userId,
            float[] embedding)
        {
            Id = Guid.NewGuid();
            UserId = userId;
            CreatedAt = DateTime.UtcNow;

            SetEmbedding(embedding);
        }

        public void SetEmbedding(float[] embedding)
        {
            ValidateEmbedding(embedding);

            Embedding = embedding;
            Dimension = embedding.Length;
        }

        public void ReplaceEmbedding(float[] embedding)
        {
            SetEmbedding(embedding);
            UpdatedAt = DateTime.UtcNow;
        }

        public bool HasSameDimension(int dimension)
        {
            return Dimension == dimension;
        }

        public bool IsCompatibleWith(float[] embedding)
        {
            return embedding.Length == Dimension;
        }

        private static void ValidateEmbedding(float[] embedding)
        {
            if (embedding is null)
            {
                throw new ArgumentNullException(nameof(embedding));
            }

            if (embedding.Length == 0)
            {
                throw new ArgumentException(
                    "Embedding cannot be empty.",
                    nameof(embedding));
            }
        }
    }
}
