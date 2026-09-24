# Entity Framework Core Migration Guide

This guide documents the command used to add a new database migration in an ASP.NET Core solution with a separate Infrastructure project.

## Adding the Initial Migration

Run the following command from the root directory of your solution (where your solution file `.sln` is located):

```bash
dotnet ef migrations add InitialCreate --project .\FirstAPIProject.Infrastructure\FirstAPIProject.Infrastructure.csproj --startup-project .\FirstAPIProject\FirstAPIProject.API.csproj
```

### Breakdown of the Command Arguments:
* `dotnet ef migrations add InitialCreate`: Creates a new migration named `InitialCreate`.
* `--project <path>`: Specifies the path to the project where your `DbContext` and entity configurations are located (`FirstAPIProject.Infrastructure`).
* `--startup-project <path>`: Specifies the entry point project (your API project) which contains the database connection string and program configuration (`FirstAPIProject.API`).

## Applying the Migration to the Database

Once the migration has been successfully added, apply it to your database using the update command:

```bash
dotnet ef database update --project .\FirstAPIProject.Infrastructure\FirstAPIProject.Infrastructure.csproj --startup-project .\FirstAPIProject\FirstAPIProject.API.csproj
```

## Prerequisites
Make sure you have the EF Core tools installed globally or locally in your .NET tool manifest:
```bash
dotnet tool install --global dotnet-ef