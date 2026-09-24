using FirstAPIProject.Application.Modules.Announcement.DTOs;
using FluentValidation;

namespace FirstAPIProject.Application.Modules.Announcement.Validators;

public sealed class CreateAnnouncementRequestValidator
    : AbstractValidator<CreateAnnouncementRequest>
{
    public CreateAnnouncementRequestValidator()
    {
        RuleFor(x => x.Title)
            .Cascade(CascadeMode.Stop)
            .NotEmpty()
            .WithMessage("Title is required.")
            .MaximumLength(200)
            .WithMessage(
                "Title must not exceed 200 characters.");

        RuleFor(x => x.Content)
            .NotEmpty()
            .WithMessage("Content is required.");

        RuleFor(x => x.Audience)
            .IsInEnum()
            .WithMessage("Audience is invalid.");
    }
}