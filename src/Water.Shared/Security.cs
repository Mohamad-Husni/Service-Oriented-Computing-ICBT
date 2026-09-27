using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;

namespace Water.Shared;

public sealed record DemoIdentity(string Name, string Role, string Account, string Token);

/// <summary>Environment-provisioned demo identities. Replace with OIDC and partner OAuth for production.</summary>
public sealed class IdentityRegistry
{
    public IReadOnlyList<DemoIdentity> Identities { get; }
    public IdentityRegistry(IConfiguration config)
    {
        Identities = new[] {
            new DemoIdentity("customer", "customer", "100000001", Required(config, "CUSTOMER_TOKEN")),
            new DemoIdentity("customer2", "customer", "100000002", Required(config, "CUSTOMER2_TOKEN")),
            new DemoIdentity("partner", "partner", "", Required(config, "PARTNER_TOKEN")),
            new DemoIdentity("operator", "operator", "", Required(config, "OPERATOR_TOKEN"))
        };
    }
    private static string Required(IConfiguration config, string key) =>
        config[key] is { Length: >= 24 } value ? value : throw new InvalidOperationException($"Set {key} to at least 24 characters.");
    public DemoIdentity? Find(string token) => Identities.FirstOrDefault(i => Equal(i.Token, token));
    public static bool Equal(string a, string b) => CryptographicOperations.FixedTimeEquals(SHA256.HashData(Encoding.UTF8.GetBytes(a)), SHA256.HashData(Encoding.UTF8.GetBytes(b)));
    public static ClaimsPrincipal Principal(DemoIdentity identity) => new(new ClaimsIdentity(new[] {
        new Claim(ClaimTypes.Name, identity.Name), new Claim(ClaimTypes.Role, identity.Role), new Claim("account", identity.Account)
    }, "Demo"));
}

public static class ServiceSecurity
{
    public static void UseServiceSecurity(this WebApplication app, IdentityRegistry registry)
    {
        app.Use(async (context, next) =>
        {
            context.Response.Headers.CacheControl = "no-store";
            context.Response.Headers["X-Content-Type-Options"] = "nosniff";
            context.Response.Headers["X-Correlation-ID"] = context.TraceIdentifier;
            try
            {
                if (context.Request.Path != "/health")
                {
                    var value = context.Request.Headers.Authorization.ToString();
                    var identity = value.StartsWith("Bearer ", StringComparison.Ordinal) ? registry.Find(value[7..]) : null;
                    if (identity is null) throw new DomainException(401, "Valid service credentials are required.");
                    context.User = IdentityRegistry.Principal(identity);
                }
                await next(context);
            }
            catch (DomainException e) { await Results.Problem(statusCode: e.Status, title: e.Message).ExecuteAsync(context); }
            catch (BadHttpRequestException) { await Results.Problem(statusCode: 400, title: "The request body is invalid.").ExecuteAsync(context); }
            catch (Exception e)
            {
                app.Logger.LogError(e, "Request failed {TraceId}", context.TraceIdentifier);
                await Results.Problem(statusCode: 500, title: "The service could not complete the request.").ExecuteAsync(context);
            }
        });
    }

    public static void Allow(ClaimsPrincipal user, string account, bool partners = true)
    {
        if (user.IsInRole("operator") || (partners && user.IsInRole("partner"))) return;
        if (!user.IsInRole("customer") || user.FindFirstValue("account") != account)
            throw new DomainException(403, "You do not have access to this account.");
    }
}
