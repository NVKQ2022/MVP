using System.Text.Json.Serialization;

namespace FirstAPIProject.Infrastructure.FaceRecognition.DTOs
{
    public sealed class ExtractEmbeddingResponse
    {
        [JsonPropertyName("embedding")]
        public float[] Embedding { get; set; } = [];
    }
}
