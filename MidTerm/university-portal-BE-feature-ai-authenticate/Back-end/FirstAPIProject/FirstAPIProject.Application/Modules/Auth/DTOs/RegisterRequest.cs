using System;
using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.DTOs
{
    public sealed record RegisterRequest
    {
        [Required]
        [EmailAddress]
        [MaxLength(255)]
        public string Email { get; init; } = null!;

        [Required]
        [MinLength(8)]
        public string Password { get; init; } = null!;
    }
}
