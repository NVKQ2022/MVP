namespace FirstAPIProject.Infrastructure.FaceRecognition.Models
{
    public sealed class FaceRecognitionOptions
    {
        public string BaseUrl { get; set; } = string.Empty;

        public string ExtractEmbeddingEndpoint { get; set; }
            = "/api/v1/embedding/file";
    }
}