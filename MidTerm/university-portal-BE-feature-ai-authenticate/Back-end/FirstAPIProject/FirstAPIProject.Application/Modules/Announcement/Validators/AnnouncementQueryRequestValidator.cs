using FirstAPIProject.Application.Modules.Announcement.DTOs;
using FluentValidation;

namespace FirstAPIProject.Application.Modules.Announcement.Validators;

public sealed class AnnouncementQueryRequestValidator
    : AbstractValidator<AnnouncementQueryRequest>
{
    public AnnouncementQueryRequestValidator()
    {
        RuleFor(x => x.Keyword)
            .MaximumLength(200)
            .WithMessage(
                "Keyword must not exceed 200 characters.")
            .When(x =>
                !string.IsNullOrWhiteSpace(x.Keyword));

        RuleFor(x => x.Audience)
            .IsInEnum()
            .WithMessage("Audience is invalid.")
            .When(x => x.Audience.HasValue);

        RuleFor(x => x.PublicationStatus)
            .IsInEnum()
            .WithMessage(
                "PublicationStatus is invalid.")
            .When(x =>
                x.PublicationStatus.HasValue);

        RuleFor(x => x.PageNumber)
            .GreaterThanOrEqualTo(1)
            .WithMessage(
                "PageNumber must be greater than or equal to 1.");

        RuleFor(x => x.PageSize)
            .InclusiveBetween(1, 100)
            .WithMessage(
                "PageSize must be between 1 and 100.");
    }
}