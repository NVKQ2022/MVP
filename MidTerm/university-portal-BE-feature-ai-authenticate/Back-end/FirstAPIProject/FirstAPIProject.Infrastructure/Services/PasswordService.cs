using FirstAPIProject.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;
using Microsoft.AspNetCore.Identity;
using FirstAPIProject.Application.Modules.Auth.Interfaces;

namespace FirstAPIProject.Infrastructure.Services
{
    public sealed class PasswordService : IPasswordService
    {
        private readonly PasswordHasher<object> _passwordHasher;

        public PasswordService()
        {
            _passwordHasher = new PasswordHasher<object>();
        }

        public string HashPassword(string password)
        {
            return _passwordHasher.HashPassword(
                new object(),
                password);
        }

        public bool VerifyPassword(string passwordHash, string providedPassword)
        {
            var result = _passwordHasher.VerifyHashedPassword(
                new object(),
                passwordHash,
                providedPassword);

            return result == PasswordVerificationResult.Success || result == PasswordVerificationResult.SuccessRehashNeeded;
        }
    }
}
