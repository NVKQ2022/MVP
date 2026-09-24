using FirstAPIProject.Application.Modules.Whitelist.DTOs;
using FluentValidation;
using System.Text.RegularExpressions;

namespace FirstAPIProject.Application.Modules.Whitelist.Validators;

public sealed class WhitelistFilterRequestValidator : AbstractValidator<WhitelistFilterRequest>
{
    public WhitelistFilterRequestValidator()
    {
        RuleFor(x => x.Page)
            .GreaterThanOrEqualTo(1)
            .WithMessage("Page must be greater than or equal to 1.");

        RuleFor(x => x.PageSize)
            .InclusiveBetween(1, 100)
            .WithMessage("PageSize must be between 1 and 100.");
    }
}

public sealed class CreateWhitelistRequestValidator : AbstractValidator<CreateWhitelistRequest>
{
    private static readonly Regex DomainRegex = new(@"^@?[a-zA-Z0-9.\-]+$", RegexOptions.Compiled);

    public CreateWhitelistRequestValidator()
    {
        RuleFor(x => x)
            .Must(x => (!string.IsNullOrWhiteSpace(x.Email) && string.IsNullOrWhiteSpace(x.Domain)) ||
                       (string.IsNullOrWhiteSpace(x.Email) && !string.IsNullOrWhiteSpace(x.Domain)))
            .WithMessage("Exactly one of Email or Domain must be provided, not both and not neither.");

        When(x => !string.IsNullOrWhiteSpace(x.Email), () =>
        {
            RuleFor(x => x.Email)
                .EmailAddress()
                .WithMessage("A valid email address is required.")
                .MaximumLength(255)
                .WithMessage("Email must not exceed 255 characters.");
        });

        When(x => !string.IsNullOrWhiteSpace(x.Domain), () =>
        {
            RuleFor(x => x.Domain)
                .Matches(DomainRegex)
                .WithMessage("Domain must contain only letters, numbers, hyphens, dots, and optional leading '@'.")
                .MaximumLength(255)
                .WithMessage("Domain must not exceed 255 characters.");
        });
    }
}

public sealed class UpdateWhitelistRequestValidator : AbstractValidator<UpdateWhitelistRequest>
{
    private static readonly Regex DomainRegex = new(@"^@?[a-zA-Z0-9.\-]+$", RegexOptions.Compiled);

    public UpdateWhitelistRequestValidator()
    {
        RuleFor(x => x)
            .Must(x => (!string.IsNullOrWhiteSpace(x.Email) && string.IsNullOrWhiteSpace(x.Domain)) ||
                       (string.IsNullOrWhiteSpace(x.Email) && !string.IsNullOrWhiteSpace(x.Domain)))
            .WithMessage("Exactly one of Email or Domain must be provided, not both and not neither.");

        When(x => !string.IsNullOrWhiteSpace(x.Email), () =>
        {
            RuleFor(x => x.Email)
                .EmailAddress()
                .WithMessage("A valid email address is required.")
                .MaximumLength(255)
                .WithMessage("Email must not exceed 255 characters.");
        });

        When(x => !string.IsNullOrWhiteSpace(x.Domain), () =>
        {
            RuleFor(x => x.Domain)
                .Matches(DomainRegex)
                .WithMessage("Domain must contain only letters, numbers, hyphens, dots, and optional leading '@'.")
                .MaximumLength(255)
                .WithMessage("Domain must not exceed 255 characters.");
        });
    }
}