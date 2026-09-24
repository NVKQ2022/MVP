using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Infrastructure.VectorDb.Models
{
    public sealed class VectorDbOptions
    {
        public string Host { get; set; } = string.Empty;

        public int Port { get; set; }

        public string CollectionName { get; set; } = string.Empty;
    }
}