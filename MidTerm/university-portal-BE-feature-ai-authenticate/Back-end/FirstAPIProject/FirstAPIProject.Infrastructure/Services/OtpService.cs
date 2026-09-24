using System.Security.Cryptography;
using System.Text;
using FirstAPIProject.Application.Common.Interfaces;


namespace FirstAPIProject.Infrastructure.Services;


public sealed class OtpService : IOtpService
{
    public string GenerateOtp()
    {
        var randomNumber = RandomNumberGenerator.GetInt32(100000, 999999);

        return randomNumber.ToString();
    }

    public string HashOtp(string otp)
    {
        var bytes = Encoding.UTF8.GetBytes(otp);

        var hash = SHA256.HashData(bytes);

        return Convert.ToHexString(hash);
    }

    public bool VerifyOtp(string otp, string hash)
    {
        var otpHash = HashOtp(otp);

        return otpHash == hash;
    }
}
