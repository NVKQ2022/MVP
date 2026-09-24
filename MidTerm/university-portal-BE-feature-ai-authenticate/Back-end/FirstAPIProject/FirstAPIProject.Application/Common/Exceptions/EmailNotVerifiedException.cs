using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Common.Exceptions
{
    public sealed class EmailNotVerifiedException : Exception
    {
        public EmailNotVerifiedException() : base("Email has not been verified.")
        {
        }
    }
}
