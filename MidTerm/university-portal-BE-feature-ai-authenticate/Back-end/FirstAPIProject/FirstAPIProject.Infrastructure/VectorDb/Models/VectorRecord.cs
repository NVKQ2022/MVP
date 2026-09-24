using System;
using System.Collections.Generic;
using System.Text;
using System.Text.Json.Nodes;

namespace FirstAPIProject.Infrastructure.VectorDb.Models
{
    public sealed class VectorRecord
    {
        public Guid PointId { get; init; }

        public float[] Vector { get; init; } = [];

        public Dictionary<string, object> Payload { get; init; } = [];
    }
}
