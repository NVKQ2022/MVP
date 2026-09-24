using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Domain.Entities;
using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.Services
{
    public sealed class FaceRegistrationService
    : IFaceRegistrationService
    {
        private readonly IFaceRecognitionClient _faceRecognitionClient;
        private readonly IFaceEmbeddingRepository _faceEmbeddingRepository;

        public FaceRegistrationService(
            IFaceRecognitionClient faceRecognitionClient,
            IFaceEmbeddingRepository faceEmbeddingRepository)
        {
            _faceRecognitionClient = faceRecognitionClient;
            _faceEmbeddingRepository = faceEmbeddingRepository;
        }

        public async Task RegisterAsync(
            Guid userId,
            IFormFile image,
            CancellationToken cancellationToken = default)
        {
            var embedding =
                await _faceRecognitionClient
                    .ExtractEmbeddingAsync(
                        image,
                        cancellationToken);

            var faceEmbedding =
                new FaceEmbedding(
                    userId,
                    embedding);

            await _faceEmbeddingRepository
                .StoreAsync(
                    faceEmbedding,
                    cancellationToken);
        }
    }
}
