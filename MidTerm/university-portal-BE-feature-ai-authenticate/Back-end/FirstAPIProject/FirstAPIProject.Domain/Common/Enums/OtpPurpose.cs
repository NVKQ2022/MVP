using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Domain.Common.Enums;

public enum OtpPurpose
{
    EmailVerification = 1,

    PasswordReset = 2,

    MfaLogin = 3
}

