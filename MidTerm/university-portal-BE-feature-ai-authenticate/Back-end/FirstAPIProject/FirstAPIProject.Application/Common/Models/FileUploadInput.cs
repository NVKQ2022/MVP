namespace FirstAPIProject.Application.Common.Models;

public sealed record FileUploadInput(
    Stream Content,
    string FileName,
    long Length );
