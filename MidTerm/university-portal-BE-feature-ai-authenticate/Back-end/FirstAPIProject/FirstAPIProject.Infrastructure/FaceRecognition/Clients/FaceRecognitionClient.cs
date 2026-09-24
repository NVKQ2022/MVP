using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Infrastructure.FaceRecognition.DTOs;
using FirstAPIProject.Infrastructure.FaceRecognition.Models;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Options;
using System.Net.Http.Json;

namespace FirstAPIProject.Infrastructure.FaceRecognition.Clients
{
    public sealed class FaceRecognitionClient
        : IFaceRecognitionClient
    {
        private readonly HttpClient _httpClient;
        private readonly FaceRecognitionOptions _options;

        public FaceRecognitionClient(
            HttpClient httpClient,
            IOptions<FaceRecognitionOptions> options)
        {
            _httpClient = httpClient;
            _options = options.Value;
        }

        public async Task<float[]> ExtractEmbeddingAsync(
            IFormFile image,
            CancellationToken cancellationToken = default)
        {
            using var content = new MultipartFormDataContent();

            using var stream = image.OpenReadStream();

            using var fileContent =
                new StreamContent(stream);

            fileContent.Headers.ContentType =
                new System.Net.Http.Headers.MediaTypeHeaderValue(
                    image.ContentType);

            content.Add(
                fileContent,
                "file",
                image.FileName);

            var response =
                await _httpClient.PostAsync(
                    _options.ExtractEmbeddingEndpoint,
                    content,
                    cancellationToken);

            response.EnsureSuccessStatusCode();

            var result =
                await response.Content.ReadFromJsonAsync<
                    ExtractEmbeddingResponse>(
                    cancellationToken);

            if (result is null)
            {
                throw new InvalidOperationException(
                    "Failed to extract face embedding.");
            }

            return result.Embedding;
        }
    }
}