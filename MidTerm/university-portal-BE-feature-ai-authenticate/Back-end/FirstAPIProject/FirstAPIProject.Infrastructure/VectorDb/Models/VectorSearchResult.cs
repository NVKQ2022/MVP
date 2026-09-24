using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Nodes;

namespace FirstAPIProject.Infrastructure.VectorDb.Models
{
    public sealed class VectorSearchResult
    {
        public Guid PointId { get; init; }

        public double Score { get; init; }

        public Dictionary<string, object> Payload { get; init; } = [];
    }
}