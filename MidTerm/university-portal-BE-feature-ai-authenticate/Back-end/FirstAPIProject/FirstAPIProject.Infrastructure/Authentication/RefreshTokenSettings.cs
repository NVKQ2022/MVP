using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Infrastructure.Authentication
{
    public sealed class RefreshTokenSettings
    {
        public const string SectionName = "RefreshTokenSettings";

        public int ExpirationDays { get; set; }
    }
}
