namespace FirstAPIProject.Application.Common.Exceptions
{
    public sealed class EmailNotWhitelistedException : Exception
    {
        public EmailNotWhitelistedException( string email )
            : base($"Email {email} is not in the whitelist. Only approved school domains or emails can register.")
        { }

    }
}
