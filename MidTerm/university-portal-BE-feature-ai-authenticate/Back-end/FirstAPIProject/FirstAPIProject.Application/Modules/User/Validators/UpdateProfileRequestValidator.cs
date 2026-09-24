using FirstAPIProject.Application.Modules.User.DTOs;
using FluentValidation;

namespace FirstAPIProject.Application.Modules.User.Validators;

public sealed class UpdateProfileRequestValidator
    : AbstractValidator<UpdateProfileRequest>
{
    public UpdateProfileRequestValidator()
    {
        RuleFor(x => x.UserName)
            .MaximumLength(50);

        RuleFor(x => x.PhoneNumber)
            .MaximumLength(20)
            .Matches(@"^[0-9+()\-\s]*$")
            .When(x => !string.IsNullOrWhiteSpace(x.PhoneNumber));

        RuleFor(x => x.Address)
            .MaximumLength(500);

        RuleFor(x => x.Gender)
            .IsInEnum()
            .When(x => x.Gender.HasValue);

        RuleFor(x => x.DateOfBirth)
            .Must(date => !date.HasValue ||
                date.Value <= DateOnly.FromDateTime(DateTime.UtcNow))
            .WithMessage("Date of birth cannot be in the future.");
    }
}
