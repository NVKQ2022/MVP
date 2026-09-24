using FirstAPIProject.Application.Common.Interfaces;

namespace FirstAPIProject.Infrastructure.Services;


public sealed class FakeEmailService : IEmailService
{

    public Task SendEmailAsync(
        string to,
        string subject,
        string body,
        CancellationToken cancellationToken = default)
    {

        Console.WriteLine("======================");
        Console.WriteLine("FAKE EMAIL SERVICE");
        Console.WriteLine("======================");

        Console.WriteLine($"To: {to}");
        Console.WriteLine($"Subject: {subject}");
        Console.WriteLine($"Body: {body}");

        Console.WriteLine("======================");


        return Task.CompletedTask;
    }
}

