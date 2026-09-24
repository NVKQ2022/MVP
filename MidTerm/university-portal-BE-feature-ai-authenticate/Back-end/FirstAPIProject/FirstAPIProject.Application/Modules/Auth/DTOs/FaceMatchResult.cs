using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Auth.DTOs
{
    public sealed class FaceMatchResult
    {
        public Guid UserId { get; init; }

        public double Score { get; init; }

        public float[] Embedding { get; init; } = [];
    }
}
