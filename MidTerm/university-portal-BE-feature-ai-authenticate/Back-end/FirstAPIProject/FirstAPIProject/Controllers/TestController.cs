using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Domain.Entities;
using Microsoft.AspNetCore.Mvc;

namespace FirstAPIProject.API.Controllers;

[ApiController]
[Route("api/test")]
public class TestController : ControllerBase
{
    private readonly IFaceEmbeddingRepository _faceEmbeddingRepository;
    private readonly IFaceRecognitionClient _faceRecognitionClient;

    public TestController(
        IFaceEmbeddingRepository faceEmbeddingRepository,
        IFaceRecognitionClient faceRecognitionClient)
    {
        _faceEmbeddingRepository = faceEmbeddingRepository;
        _faceRecognitionClient = faceRecognitionClient;
    }
    [HttpPost("qdrant/create-collection")]
    public async Task<IActionResult> CreateCollection(
    [FromServices] Qdrant.Client.QdrantClient client)
    {
        await client.CreateCollectionAsync(
            collectionName: "face_embeddings",
            vectorsConfig: new Qdrant.Client.Grpc.VectorParams
            {
                Size = 512,
                Distance = Qdrant.Client.Grpc.Distance.Cosine
            });

        return Ok();
    }
    [HttpPost("qdrant/store")]
    public async Task<IActionResult> Store()
    {
        var userId = Guid.NewGuid();

        var embedding = Enumerable
            .Repeat(0.5f, 512)
            .ToArray();

        var faceEmbedding =
            new FaceEmbedding(
                userId,
                embedding);

        await _faceEmbeddingRepository
            .StoreAsync(faceEmbedding);

        return Ok(new
        {
            userId
        });
    }
    [HttpPost("qdrant/search")]
    public async Task<IActionResult> Search()
    {
        var vector = Enumerable
            .Repeat(0.5f, 512)
            .ToArray();

        var result =
            await _faceEmbeddingRepository
                .FindBestMatchAsync(vector);

        return Ok(result);
    }
    [HttpGet("qdrant/{userId}")]
    public async Task<IActionResult> Get(
    Guid userId)
    {
        var embedding =
            await _faceEmbeddingRepository
                .GetByUserIdAsync(userId);

        return Ok(embedding);
    }
    [HttpDelete("qdrant/{userId}")]
    public async Task<IActionResult> Delete(
    Guid userId)
    {
        await _faceEmbeddingRepository
            .DeleteAsync(userId);

        return Ok();
    }
    [HttpPost("face/extract")]
    public async Task<IActionResult> ExtractEmbedding(
    IFormFile image)
    {
        var embedding =
            await _faceRecognitionClient
                .ExtractEmbeddingAsync(image);

        return Ok(new
        {
            dimension = embedding.Length,
            preview = embedding.Take(10)
        });
    }
}