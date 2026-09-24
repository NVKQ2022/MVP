using FirstAPIProject.Application.Common.Exceptions;
using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Modules.Auth.DTOs;
using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Application.Modules.User.Interfaces;
using FirstAPIProject.Application.Modules.Whitelist.Interfaces;
using FirstAPIProject.Domain.Common.Enums;
using FirstAPIProject.Domain.Entities;

namespace FirstAPIProject.Application.Modules.Auth.Services
{
    public class AuthService : IAuthService
    {
        private readonly IUserRepository _userRepository;
        private readonly IPasswordService _passwordService;
        private readonly IJwtService _jwtService;
        private readonly IRefreshTokenRepository _refreshTokenRepository;
        private readonly IRefreshTokenService _refreshTokenService;
        private readonly IOtpVerificationRepository _otpVerificationRepository;
        private readonly IOtpService _otpService;
        private readonly IEmailService _emailService;
        //private readonly IFaceRecognitionClient _faceClient;
        private readonly IFaceEmbeddingRepository _faceEmbeddingRepository;
        private readonly IUnitOfWork _unitOfWork;
        private readonly IEmailWhitelistRepository _emailWhitelistRepository;

        public AuthService(
            IUserRepository userRepository,
            IPasswordService passwordService,
            IJwtService jwtService,
            IRefreshTokenRepository refreshTokenRepository,

            IRefreshTokenService refreshTokenService,
            IOtpVerificationRepository otpVerificationRepository,
            IOtpService otpService,
            IEmailService emailService,
            IEmailWhitelistRepository emailWhitelistRepository,
            IUnitOfWork unitOfWork )
        {
            _userRepository = userRepository;
            _passwordService = passwordService;
            _jwtService = jwtService;
            _refreshTokenRepository = refreshTokenRepository;
            _refreshTokenService = refreshTokenService;
            _otpVerificationRepository = otpVerificationRepository;
            _otpService = otpService;
            _emailService = emailService;
            _emailWhitelistRepository = emailWhitelistRepository;
            _unitOfWork = unitOfWork;
        }

        public async Task<RegisterResponse> RegisterAsync( RegisterRequest request, CancellationToken cancellationToken = default )
        {
            var isAllowed = await _emailWhitelistRepository.IsEmailAllowedAsync(request.Email, cancellationToken);
            if (!isAllowed)
            {
                throw new EmailNotWhitelistedException(request.Email);
            }

            var exists = await _userRepository.AnyAsync(x => x.Email == request.Email, cancellationToken);

            if (exists)
            {
                throw new UserAlreadyExistsException(request.Email);
            }

            var passwordHash = _passwordService.HashPassword(request.Password);

            var user = Domain.Entities.User.Create(request.Email, passwordHash);

            await _userRepository.AddAsync(user, cancellationToken);

            var otp = _otpService.GenerateOtp();

            var otpHash = _otpService.HashOtp(otp);

            var otpVerification =
                OtpVerification.Create(
                    user.Id,
                    otpHash,
                    OtpPurpose.EmailVerification);

            await _otpVerificationRepository.AddAsync(otpVerification, cancellationToken);

            await _emailService.SendEmailAsync(
                user.Email,
                "Verify your email",
                $"Your verification code is: {otp}",
                cancellationToken);

            await _unitOfWork.SaveChangesAsync(cancellationToken);

            return new RegisterResponse("Verification email sent", user.Email);
        }

        public async Task VerifyEmailAsync( VerifyEmailRequest request, CancellationToken cancellationToken = default )
        {
            var user = await _userRepository.GetByEmailAsync(request.Email, cancellationToken);

            if (user is null)
            {
                throw new InvalidCredentialsException();
            }

            var otp =
                await _otpVerificationRepository.GetLatestByPurposeAsync(
                        user.Id,
                        OtpPurpose.EmailVerification,
                        cancellationToken);

            if (otp is null)
            {
                throw new InvalidOperationException("OTP not found.");
            }

            if (otp.ExpiresAt < DateTimeOffset.UtcNow)
            {
                throw new InvalidOperationException("OTP expired.");
            }

            var valid = _otpService.VerifyOtp(request.Otp, otp.CodeHash);

            if (!valid)
            {
                throw new InvalidOperationException("Invalid OTP.");
            }

            user.VerifyEmail();

            otp.MarkAsVerified();

            await _unitOfWork.SaveChangesAsync(cancellationToken);
        }

        public async Task<LoginResponse> LoginAsync( LoginRequest request, CancellationToken cancellationToken = default )
        {
            var user = await _userRepository.GetByEmailAsync(request.Email, cancellationToken);

            if (user is null)
            {
                throw new InvalidCredentialsException();
            }

            var validPassword = _passwordService.VerifyPassword(user.PasswordHash, request.Password);

            if (!validPassword)
            {
                throw new InvalidCredentialsException();
            }

            if (!user.IsEmailVerified)
            {
                throw new EmailNotVerifiedException();
            }

            if (user.IsMfaEnabled)
            {
                return await CreateMfaChallengeAsync(
                    user,
                    cancellationToken);
            }


            var authResponse =
                await CreateAuthResponseAsync(
                    user,
                    cancellationToken);


            return new LoginResponse
            (
                false,
                authResponse.AccessToken,
                authResponse.ExpiresAt,
                authResponse.RefreshToken,
                null
            );
        }
         
        
        public async Task<AuthResponse> FaceAuthenticateAsync(FaceAuthenticateLoginRequest request, CancellationToken cancellationToken = default)
        {
            // Implementation for face-based authentication
            throw new NotImplementedException();
        }

        public async Task<AuthResponse> RefreshTokenAsync(RefreshTokenRequest request, CancellationToken cancellationToken = default)
        {
            // Hash the raw refresh token sent by the client.
            var tokenHash = _refreshTokenService.HashToken(request.RefreshToken);

            // Find the refresh token in the database.
            var storedToken = await _refreshTokenRepository.GetByTokenHashAsync(tokenHash, cancellationToken);

            // Reject if the token does not exist or is no longer active.
            if (storedToken is null || !storedToken.IsActive())
            {
                throw new InvalidRefreshTokenException();
            }

            // Find the user associated with the refresh token.
            var user = await _userRepository.GetByIdAsync(storedToken.UserId, cancellationToken);

            // Reject if the user no longer exists.
            if (user is null)
            {
                throw new InvalidRefreshTokenException();
            }

            // Generate a new refresh token.
            var newRawRefreshToken = _refreshTokenService.GenerateToken();

            // Store only the hash of the new refresh token.
            var newRefreshTokenHash = _refreshTokenService.HashToken(newRawRefreshToken);

            // Create the new refresh token.
            var newRefreshToken = RefreshToken.Create(
                user.Id,
                newRefreshTokenHash,
                _refreshTokenService.GetExpiration());

            // Revoke the old refresh token and link it to the newly generated refresh token.
            storedToken.Revoke(newRefreshTokenHash);

            // Add the new refresh token to the database.
            await _refreshTokenRepository.AddAsync(newRefreshToken, cancellationToken);

            // Generate a new access token.
            var accessToken = _jwtService.GenerateToken(user);

            // Persist both the revoked old token and the newly created refresh token.
            await _unitOfWork.SaveChangesAsync(cancellationToken);

            // Return the new access token and refresh token.
            return new AuthResponse(
                accessToken.AccessToken,
                accessToken.ExpiresAt,
                newRawRefreshToken);
        }

        public async Task LogoutAsync( Guid userId, RefreshTokenRequest request, CancellationToken cancellationToken = default )
        {
            var tokenHash = _refreshTokenService.HashToken(request.RefreshToken);

            var storedToken = await _refreshTokenRepository.GetByTokenHashAsync(tokenHash, cancellationToken);

            if (storedToken is null)
            {
                return;
            }

            if (storedToken.UserId != userId)
            {
                throw new UnauthorizedAccessException();
            }

            if (!storedToken.IsActive())
            {
                return;
            }

            storedToken.Revoke();

            await _unitOfWork.SaveChangesAsync(cancellationToken);
        }

        public async Task<EnableMfaResponse> EnableMfaAsync(Guid userId, CancellationToken cancellationToken = default)
        {
            var user = await _userRepository.GetByIdAsync(userId, cancellationToken);

            if (user is null)
            {
                throw new InvalidCredentialsException();
            }
            
            if (!user.IsEmailVerified)
            {
                throw new InvalidOperationException("Email must be verified before enabling MFA");
            }

            if (user.IsMfaEnabled)
            {
                throw new InvalidOperationException("MFA already enabled");
            }

            user.EnableMfa(MfaMethod.EmailOtp);

            await _unitOfWork.SaveChangesAsync(cancellationToken);

            return new EnableMfaResponse(true, MfaMethod.EmailOtp.ToString());
        }

        public async Task<AuthResponse> VerifyMfaAsync(Guid challengeId, string otp, CancellationToken cancellationToken = default)
        {

            var otpVerification =
                await _otpVerificationRepository
                    .GetByIdAsync(
                        challengeId,
                        cancellationToken);


            if (otpVerification == null)
            {
                throw new InvalidOperationException("MFA challenge not found.");
            }


            if (otpVerification.Purpose != OtpPurpose.MfaLogin)
            {
                throw new InvalidOperationException("Invalid MFA challenge.");
            }


            if (otpVerification.ExpiresAt < DateTimeOffset.UtcNow)
            {
                throw new InvalidOperationException("OTP expired.");
            }

            if (otpVerification.VerifiedAt.HasValue)
            {
                throw new InvalidOperationException("OTP already used.");
            }

            var valid = _otpService.VerifyOtp(otp, otpVerification.CodeHash);


            if (!valid)
            {
                throw new InvalidOperationException("Invalid OTP.");
            }


            var user = await _userRepository.GetByIdWithRoleAsync(otpVerification.UserId, cancellationToken);

            if (user == null)
            {
                throw new InvalidOperationException("User not found.");
            }

            otpVerification.MarkAsVerified();

            await _unitOfWork.SaveChangesAsync(
                cancellationToken);


            return await CreateAuthResponseAsync(
                user,
                cancellationToken);
        }

        private async Task<LoginResponse> CreateMfaChallengeAsync(FirstAPIProject.Domain.Entities.User user, CancellationToken cancellationToken)
        {
            var otp = _otpService.GenerateOtp();

            var otpHash = _otpService.HashOtp(otp);


            var otpVerification =
                OtpVerification.Create(
                    user.Id,
                    otpHash,
                    OtpPurpose.MfaLogin);


            await _otpVerificationRepository.AddAsync(otpVerification, cancellationToken);


            await _emailService.SendEmailAsync(
                user.Email,
                "MFA Verification Code",
                $"Your verification code is: {otp}",
                cancellationToken);


            await _unitOfWork.SaveChangesAsync(cancellationToken);


            return new LoginResponse
            (
                true,
                null,
                null,
                null,
                otpVerification.Id
            );
        }

        private async Task<AuthResponse> CreateAuthResponseAsync(FirstAPIProject.Domain.Entities.User user, CancellationToken cancellationToken )
        {
            var accessToken = _jwtService.GenerateToken(user);

            var rawRefreshToken = _refreshTokenService.GenerateToken();

            var refreshTokenHash = _refreshTokenService.HashToken(rawRefreshToken);

            var refreshToken = RefreshToken.Create(
                user.Id,
                refreshTokenHash,
                _refreshTokenService.GetExpiration());

            await _refreshTokenRepository.AddAsync(refreshToken, cancellationToken);

            await _unitOfWork.SaveChangesAsync(cancellationToken);

            return new AuthResponse(
                accessToken.AccessToken,
                accessToken.ExpiresAt,
                rawRefreshToken);
        }
    }
}
