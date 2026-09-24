using FirstAPIProject.Domain.Common.Enums;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Announcement.DTOs
{

    public sealed class AnnouncementSummaryResponse
    {
        public Guid Id { get; set; }
        public string Title { get; set; } = string.Empty;
        public string CreatorName { get; set; } = string.Empty; // get by use create by ID to find the name of the User who create this announcement
        public PublicationStatus PublicationStatus { get; set; }
        public bool IsRead { get; set; }
        public DateTimeOffset? PublishedAt { get; set; }
    }
}


