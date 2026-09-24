using FirstAPIProject.Infrastructure.VectorDb.Models;
using Google.Protobuf.WellKnownTypes;
using Microsoft.Extensions.Options;
using Qdrant.Client.Grpc;
//using System.Text.Json.Nodes;
//using ProtoValue = Google.Protobuf.WellKnownTypes.Value;

namespace FirstAPIProject.Infrastructure.VectorDb.Clients
{
    public sealed class QdrantVectorSearchClient
        : IVectorSearchClient
    {
        private readonly Qdrant.Client.QdrantClient _client;

        private readonly VectorDbOptions _options;

        public QdrantVectorSearchClient(
            Qdrant.Client.QdrantClient client,
            IOptions<VectorDbOptions> options)
        {
            _client = client;
            _options = options.Value;
        }

        
        public async Task UpsertAsync(
            Guid pointId,
            float[] vector,
            Dictionary<string, object> payload,
            CancellationToken cancellationToken = default)
            {
                var qdrantPayload = payload.ToDictionary(
                    x => x.Key,
                    x => ToPayloadValue(x.Value));

                var point = new PointStruct
                {
                    Id = new PointId
                    {
                        Uuid = pointId.ToString()
                    }
                };

                point.Vectors = vector;

                point.Payload.Add((IDictionary<string, Qdrant.Client.Grpc.Value>)qdrantPayload);

                await _client.UpsertAsync(
                    collectionName: _options.CollectionName,
                    points: [point],
                    cancellationToken: cancellationToken);
            }

        public async Task DeleteAsync(
            Guid pointId,
            CancellationToken cancellationToken = default)
        {
            await _client.DeleteAsync(
                collectionName: _options.CollectionName,
                id: new PointId { Uuid = pointId.ToString() },
                cancellationToken: cancellationToken);
            throw new NotImplementedException();
        }

        public async Task<VectorRecord?> GetAsync(
            Guid pointId,
            CancellationToken cancellationToken = default)
        {
            //_client.SearchAsync
            //_client.GetAsync(
            //    collectionName: _options.CollectionName,
            //    id: new PointId { Uuid = pointId.ToString() },
            //    cancellationToken: cancellationToken); return null;
            throw new NotImplementedException();
        }

        [Obsolete]
        public async Task<VectorSearchResult?> SearchAsync(
            float[] vector,
            float? threshold,
            CancellationToken cancellationToken = default)
        {
            var results = await _client.SearchAsync(
                collectionName: _options.CollectionName,
                vector: vector,
                limit: 1,
                scoreThreshold: threshold,
                cancellationToken: cancellationToken);

            var match = results.FirstOrDefault();

            if (match is null)
            {
                return null;
            }

            return new VectorSearchResult
            {
                PointId = Guid.Parse(match.Id.Uuid),
                Score = match.Score,
                Payload = match.Payload.ToDictionary(
                x => x.Key,
                x =>
                {
                    if (!string.IsNullOrEmpty(x.Value.StringValue))
                    {
                        return (object)x.Value.StringValue;
                    }

                    if (x.Value.HasIntegerValue)
                    {
                        return x.Value.IntegerValue;
                    }

                    if (x.Value.HasBoolValue)
                    {
                        return x.Value.BoolValue;
                    }

                    if (x.Value.HasDoubleValue)
                    {
                        return x.Value.DoubleValue;
                    }

                    return x.Value.ToString();
                })
            };
        }


        //private static Dictionary<string, Value> ToPayload(JsonObject payload)
        //{
        //    var result = new Dictionary<string, Value>();

        //    foreach (var property in payload)
        //    {
        //        result[property.Key] = ToQdrantValue(property.Value);
        //    }

        //    return result;
        //}
        private static Qdrant.Client.Grpc.Value ToPayloadValue(
    object value)
        {
            return value switch
            {
                string s => new Qdrant.Client.Grpc.Value
                {
                    StringValue = s
                },

                Guid g => new Qdrant.Client.Grpc.Value
                {
                    StringValue = g.ToString()
                },

                int i => new Qdrant.Client.Grpc.Value
                {
                    IntegerValue = i
                },

                bool b => new Qdrant.Client.Grpc.Value
                {
                    BoolValue = b
                },

                _ => new Qdrant.Client.Grpc.Value
                {
                    StringValue = value?.ToString() ?? string.Empty
                }
            };
        }
    }
}
