using FirstAPIProject.Domain.Common.Enums;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Announcement.DTOs
{

    public sealed class AnnouncementQueryRequest
    {
        public string? Keyword { get; set; }
        public Audience? Audience { get; set; }

        public PublicationStatus? PublicationStatus { get; set; }

        public int PageNumber { get; set; } = 1;

        public int PageSize { get; set; } = 10;
    }
}