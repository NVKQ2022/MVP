using FirstAPIProject.Domain.Common.Enums;
using FirstAPIProject.Domain.Entities;
using System;
using System.Collections.Generic;
using System.Text;
namespace FirstAPIProject.Domain.Entities
{
    public class Announcement : LifecycleEntity
    {
        public string Title { get; private set; } = null!;

        public string Content { get; private set; } = null!;

        public PublicationStatus PublicationStatus { get; private set; }

        public Audience Audience { get; private set; }

        public Guid CreatedBy { get; private set; }

        public DateTimeOffset? PublishedAt { get; private set; }

        // Navigation Property
        public User Creator { get; private set; } = null!;
        public ICollection<AnnouncementRead> ReadRecords { get; private set; }
            = new List<AnnouncementRead>();

        private Announcement()
        {
        }

        private Announcement(
            string title,
            string content,
            PublicationStatus publicationStatus,
            Audience audience,
            Guid createdBy)
        {
            Title = title;
            Content = content;
            PublicationStatus = publicationStatus;
            Audience = audience;
            CreatedBy = createdBy;
        }

        public static Announcement Create(
            string title,
            string content,
            Audience audience,
            Guid createdBy)
        {
            return new Announcement(
                title,
                content,
                PublicationStatus.DRAFT,
                audience,
                createdBy);
        }



        public void Update(
            string title,
            string content,
            Audience audience)
        {
            if (PublicationStatus != PublicationStatus.DRAFT)
            {
                throw new InvalidOperationException(
                    "Only draft announcements can be updated.");
            }

            Title = title;
            Content = content;
            Audience = audience;
        }

        public void Publish()
        {
            if (PublicationStatus != PublicationStatus.DRAFT)
            {
                throw new InvalidOperationException(
                    "Only draft announcements can be published.");
            }

            PublicationStatus = PublicationStatus.PUBLISHED;
            PublishedAt = DateTimeOffset.UtcNow;
            Activate();
        }

        public void Archive()
        {
            if (PublicationStatus != PublicationStatus.PUBLISHED)
            {
                throw new InvalidOperationException(
                    "Only published announcements can be archived.");
            }

            PublicationStatus = PublicationStatus.ARCHIVED;
            Deactivate();
        }
    }


}
