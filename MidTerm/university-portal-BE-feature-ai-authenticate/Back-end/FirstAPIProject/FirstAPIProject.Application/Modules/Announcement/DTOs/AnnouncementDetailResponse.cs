using FirstAPIProject.Domain.Common.Enums;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Announcement.DTOs
{
    public sealed class AnnouncementDetailResponse
    {
        public Guid Id { get; set; }

        public string Title { get; set; } = string.Empty;

        public string Content { get; set; } = string.Empty;

        public Audience Audience { get; set; }

        public PublicationStatus PublicationStatus { get; set; }

        public Guid CreatedBy { get; set; }

        public string CreatorName { get; set; } = string.Empty;

        public DateTimeOffset? PublishedAt { get; set; }

        public DateTimeOffset CreatedAt { get; set; }

        public DateTimeOffset? UpdatedAt { get; set; }
    }
}