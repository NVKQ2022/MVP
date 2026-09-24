using FirstAPIProject.Domain.Common.Enums;
using System;
using System.Collections.Generic;
using System.Text;

namespace FirstAPIProject.Application.Modules.Announcement.DTOs
{
    public sealed class CreateAnnouncementRequest
    {
        public string Title { get; set; } = null!;

        public string Content { get; set; } = null!;

        public Audience Audience { get; set; }
    }
}
