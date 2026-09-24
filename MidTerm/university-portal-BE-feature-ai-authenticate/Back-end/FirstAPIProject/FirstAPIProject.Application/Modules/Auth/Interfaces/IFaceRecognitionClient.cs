using Microsoft.AspNetCore.Http;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.Interfaces
{
    public interface IFaceRecognitionClient
    {
        Task<float[]> ExtractEmbeddingAsync(
            IFormFile image,
            CancellationToken cancellationToken = default);
    }
}
