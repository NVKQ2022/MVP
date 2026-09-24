using FirstAPIProject.Application.Modules.User.DTOs;
using FluentValidation;

namespace FirstAPIProject.Application.Modules.User.Validators;

public sealed class AdminUserFilterRequestValidator : AbstractValidator<AdminUserFilterRequest>
{
    public AdminUserFilterRequestValidator()
    {
        RuleFor(x => x.Page)
            .GreaterThanOrEqualTo(1)
            .WithMessage("Page must be greater than or equal to 1.");

        RuleFor(x => x.PageSize)
            .InclusiveBetween(1, 100)
            .WithMessage("PageSize must be between 1 and 100.");
    }
}

public sealed class AdminUpdateUserRequestValidator : AbstractValidator<AdminUpdateUserRequest>
{
    public AdminUpdateUserRequestValidator()
    {
        RuleFor(x => x.RoleId)
            .NotEmpty()
            .WithMessage("RoleId is required.");
    }
}

