using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Common.Exceptions
{
    public sealed class UserAlreadyExistsException : Exception
    {
        public UserAlreadyExistsException(string email) : base($"User with email '{email}' already exists.")
        {
        }
    }
}
