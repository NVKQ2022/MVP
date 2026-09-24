using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Common.Models;
namespace FirstAPIProject.Infrastructure.Services;

public sealed class LocalFileStorageService : IFileStorageService
{
    private const long MaxFileBytes = 2 * 1024 * 1024; // 2 MB
    private static readonly string[] AllowedExtensions = [".jpg", ".jpeg", ".png", ".webp"];
    private readonly string _storageFolder;
    private const string RequestPathPrefix = "/uploads/avatars/";


    public LocalFileStorageService()
    {
        _storageFolder = Path.Combine(AppContext.BaseDirectory, "wwwroot", "uploads", "avatars");


        if (!Directory.Exists(_storageFolder))
        {
            Directory.CreateDirectory(_storageFolder);
        }
    }


    public async Task<string> SaveAvatarAsync(
        FileUploadInput file,
        CancellationToken cancellationToken = default )
    {
        if (file.Length <= 0)
        {
            throw new ArgumentException("Avatar file cannot be empty.", nameof(file));
        }

        if (file.Length > MaxFileBytes)
        {
            throw new ArgumentException("Avatar file size must not exceed 2 MB.", nameof(file));
        }

        var extension = Path.GetExtension(file.FileName).ToLowerInvariant();
        if (string.IsNullOrEmpty(extension) ||
            !Array.Exists(AllowedExtensions, ext => ext == extension))
        {
            throw new ArgumentException(
                "Invalid file format. Allowed formats: .jpg, .jpeg, .png, .webp.", nameof(file));
        }


        // Validate file content signature (magic bytes)
        var buffer = new byte[12];
        if (file.Content.CanSeek)
        {
            file.Content.Position = 0;
        }

        var readBytes = await file.Content.ReadAsync(buffer.AsMemory(0, buffer.Length), cancellationToken);
        if (readBytes < 4 || !IsValidImageHeader(buffer, extension))
        {
            throw new ArgumentException(
                "File content does not match the expected image signature.", nameof(file));
        }


        if (file.Content.CanSeek)
        {
            file.Content.Position = 0;
        }


        var fileName = $"{Guid.NewGuid():N}{extension}";
        var physicalPath = Path.Combine(_storageFolder, fileName);


        await using (var stream = new FileStream(physicalPath, FileMode.Create, FileAccess.Write, FileShare.None))
        {
            await file.Content.CopyToAsync(stream, cancellationToken);
        }


        return $"{RequestPathPrefix}{fileName}";
    }


    public Task DeleteIfExistsAsync(
        string? relativePath,
        CancellationToken cancellationToken = default )
    {
        if (string.IsNullOrWhiteSpace(relativePath))
        {
            return Task.CompletedTask;
        }


        try
        {
            // Extract only the file name to prevent directory traversal attacks
            var fileName = Path.GetFileName(relativePath);
            var physicalPath = Path.Combine(_storageFolder, fileName);


            if (File.Exists(physicalPath))
            {
                File.Delete(physicalPath);
            }
        }
        catch
        {
            // File cleanup failure is swallowed or logged as operational
        }

        return Task.CompletedTask;
    }

    private static bool IsValidImageHeader( byte[] buffer, string extension )
    {
        return extension switch
        {
            ".jpg" or ".jpeg" => buffer[0] == 0xFF && buffer[1] == 0xD8 && buffer[2] == 0xFF,
            ".png" => buffer.Length >= 8 &&
                      buffer[0] == 0x89 && buffer[1] == 0x50 && buffer[2] == 0x4E && buffer[3] == 0x47 &&
                      buffer[4] == 0x0D && buffer[5] == 0x0A && buffer[6] == 0x1A && buffer[7] == 0x0A,
            ".webp" => buffer.Length >= 12 &&
                       buffer[0] == 0x52 && buffer[1] == 0x49 && buffer[2] == 0x46 && buffer[3] == 0x46 && // RIFF
                       buffer[8] == 0x57 && buffer[9] == 0x45 && buffer[10] == 0x42 && buffer[11] == 0x50, // WEBP
            _ => false
        };
    }
}
