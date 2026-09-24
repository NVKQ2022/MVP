namespace FirstAPIProject.Application.Common.Exceptions
{
    public sealed class InvalidRefreshTokenException : Exception
    {
        public InvalidRefreshTokenException() : base("The refresh token is invalid or expired.")
        {
        }
    }
}
