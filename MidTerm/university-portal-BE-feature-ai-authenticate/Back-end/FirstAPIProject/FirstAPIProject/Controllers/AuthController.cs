using Asp.Versioning;
using FirstAPIProject.Application.Modules.Auth.DTOs;
using FirstAPIProject.Application.Modules.Auth.Interfaces;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.RateLimiting;
using System.Security.Claims;

namespace FirstAPIProject.API.Controllers
{
    [ApiController]
    [ApiVersion(1.0)]
    [Route("api/v{version:apiVersion}/[controller]")]
    [EnableRateLimiting("auth")]
    public class AuthController : ControllerBase
    {
        private readonly IAuthService _authService;
        private readonly IFaceAuthenticateService _faceAuthenticateService;

        public AuthController(
            IAuthService authService,
            IFaceAuthenticateService faceAuthenticateService)
        {
            _authService = authService;
            _faceAuthenticateService = faceAuthenticateService;
        }

        [HttpPost("register")]
        public async Task<IActionResult> Register(RegisterRequest request, CancellationToken cancellationToken)
        {
            var response = await _authService.RegisterAsync(request, cancellationToken);

            return Ok(response);
        }

        [HttpPost("verify-email")]
        public async Task<IActionResult> VerifyEmail(VerifyEmailRequest request, CancellationToken cancellationToken)
        {
            await _authService.VerifyEmailAsync(request, cancellationToken);

            return Ok(new
            {
                message = "Email verified successfully"
            });
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login(LoginRequest request, CancellationToken cancellationToken)
        {
            var response = await _authService.LoginAsync(request, cancellationToken);

            return Ok(response);
        }

        [HttpPost("face-login")]
        [Consumes("multipart/form-data")]
        public async Task<IActionResult> FaceLogin([FromForm] FaceAuthenticateLoginRequest request, CancellationToken cancellationToken)
        {
            var response = await _faceAuthenticateService.FaceAuthenticateAsync(request, cancellationToken);

            return Ok(response);
        }

        [HttpPost("refresh")]
        public async Task<IActionResult> Refresh(RefreshTokenRequest request, CancellationToken cancellationToken)
        {
            var response = await _authService.RefreshTokenAsync(request, cancellationToken);

            return Ok(response);
        }

        [Authorize]
        [HttpPost("logout")]
        public async Task<IActionResult> Logout(RefreshTokenRequest request, CancellationToken cancellationToken)
        {
            var userId = Guid.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);

            await _authService.LogoutAsync(userId, request, cancellationToken);

            return NoContent();
        }

        [Authorize]
        [HttpPost("enable-mfa")]
        public async Task<IActionResult> EnableMfa(CancellationToken cancellationToken)
        {
            var userId = Guid.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);

            var response = await _authService.EnableMfaAsync(userId, cancellationToken);

            return Ok(response);
        }

        [HttpPost("verify-mfa")]
        public async Task<IActionResult> VerifyMfa(VerifyMfaRequest request, CancellationToken cancellationToken)
        {
            var response =
                await _authService.VerifyMfaAsync(
                    request.ChallengeId,
                    request.Otp,
                    cancellationToken);

            return Ok(response);
        }
    }
}
