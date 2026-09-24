using FirstAPIProject.Application.Common.Models;

namespace FirstAPIProject.Application.Common.Interfaces;

public interface IFileStorageService
{
    Task<string> SaveAvatarAsync(
        FileUploadInput file,
        CancellationToken cancellationToken = default );

    Task DeleteIfExistsAsync(
        string? relativePath,
        CancellationToken cancellationToken = default );
}
