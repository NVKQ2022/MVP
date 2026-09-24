using FirstAPIProject.Application.Common.Interfaces;
using FirstAPIProject.Application.Modules.Auth.DTOs;
using FirstAPIProject.Application.Modules.Auth.Interfaces;
using FirstAPIProject.Application.Modules.User.Interfaces;
using FirstAPIProject.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.Services
{
    public sealed class FaceAuthenticateService
    : IFaceAuthenticateService
    {
        private readonly IFaceRecognitionClient _faceRecognitionClient;
        private readonly IFaceEmbeddingRepository _faceEmbeddingRepository;
        private readonly IUserRepository _userRepository;
        private readonly IJwtService _jwtService;
        private readonly IRefreshTokenRepository _refreshTokenRepository;
        private readonly IRefreshTokenService _refreshTokenService;
        private readonly IUnitOfWork _unitOfWork;

        public FaceAuthenticateService(
            IFaceRecognitionClient faceRecognitionClient,
            IFaceEmbeddingRepository faceEmbeddingRepository,
            IUserRepository userRepository,
            IJwtService jwtService,
            IRefreshTokenRepository refreshTokenRepository,
            IRefreshTokenService refreshTokenService,
            IUnitOfWork unitOfWork)
        {
            _faceRecognitionClient = faceRecognitionClient;
            _faceEmbeddingRepository = faceEmbeddingRepository;
            _userRepository = userRepository;
            _jwtService = jwtService;
            _refreshTokenRepository = refreshTokenRepository;
            _refreshTokenService = refreshTokenService;
            _unitOfWork = unitOfWork;
        }

        public async Task<AuthResponse> FaceAuthenticateAsync(
    FaceAuthenticateLoginRequest request,
    CancellationToken cancellationToken = default)
        {
            var embedding =
                await _faceRecognitionClient
                    .ExtractEmbeddingAsync(
                        request.Capture,
                        cancellationToken);

            var match =
                await _faceEmbeddingRepository
                    .FindBestMatchAsync(
                        embedding,
                        cancellationToken);

            if (match is null)
            {
                throw new UnauthorizedAccessException(
                    "Face not recognized.");
            }

            var user =
                await _userRepository.GetByIdAsync(
                    match.UserId,
                    cancellationToken);

            if (user is null)
            {
                throw new UnauthorizedAccessException(
                    "Face not recognized.");
            }

            return await CreateAuthResponseAsync(
                user,
                cancellationToken);
        }


        //DUPLICATE
        private async Task<AuthResponse> CreateAuthResponseAsync(FirstAPIProject.Domain.Entities.User user, CancellationToken cancellationToken)
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
