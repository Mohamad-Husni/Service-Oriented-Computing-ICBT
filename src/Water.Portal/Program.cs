using System.Threading.RateLimiting;
using Microsoft.AspNetCore.RateLimiting;
using System.Net.Http.Headers;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Water.Shared;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<IdentityRegistry>();
builder.Services.AddHttpClient("services", c => c.Timeout = TimeSpan.FromSeconds(8));
builder.Services.AddAuthentication("portal").AddCookie("portal", options => {
    options.Cookie.Name = "waterlink.session";
    options.Cookie.HttpOnly = true;
    options.Cookie.SameSite = SameSiteMode.Strict;
    options.Cookie.SecurePolicy = builder.Environment.IsDevelopment() ? CookieSecurePolicy.SameAsRequest : CookieSecurePolicy.Always;
    options.ExpireTimeSpan = TimeSpan.FromMinutes(30);
    options.Events.OnRedirectToLogin = c => { c.Response.StatusCode = 401; return Task.CompletedTask; };
});
builder.Services.AddAuthorization();
builder.Services.AddRateLimiter(o => { o.RejectionStatusCode = 429; o.AddFixedWindowLimiter("login", l => { l.PermitLimit=10; l.Window=TimeSpan.FromMinutes(1); l.QueueLimit=0; }); });
var app = builder.Build();
var identities = app.Services.GetRequiredService<IdentityRegistry>();
var password = app.Configuration["DEMO_PASSWORD"] ?? throw new InvalidOperationException("Set DEMO_PASSWORD.");
app.Use(async (context, next) => {
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["Content-Security-Policy"] = "default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; frame-ancestors 'none'; base-uri 'none'";
    context.Response.Headers.CacheControl = "no-store";
    // Browser cross-origin callers cannot set this custom header without CORS preflight approval.
    if (context.Request.Method == "POST" && context.Request.Headers["X-WaterLink"] != "1") {
        context.Response.StatusCode = 403; return;
    }
    await next(context);
});
app.UseDefaultFiles(); app.UseStaticFiles();
app.UseAuthentication(); app.UseAuthorization(); app.UseRateLimiter();
app.MapGet("/health", () => Results.Ok(new { status="healthy", service="portal" }));
app.MapPost("/session", async (Login request, HttpContext context) => {
    var identity = identities.Identities.FirstOrDefault(i => i.Name == request.Username);
    if (identity is null || !IdentityRegistry.Equal(request.Password ?? "", password)) return Results.Unauthorized();
    await context.SignInAsync("portal", IdentityRegistry.Principal(identity));
    return Results.Ok(new { identity.Name, identity.Role, identity.Account });
}).RequireRateLimiting("login");
app.MapGet("/session", (HttpContext context) => Results.Ok(new {
    name=context.User.Identity!.Name, role=context.User.FindFirst(System.Security.Claims.ClaimTypes.Role)!.Value,
    account=context.User.FindFirst("account")!.Value
})).RequireAuthorization();
app.MapPost("/logout", async (HttpContext context) => { await context.SignOutAsync("portal"); return Results.NoContent(); });
app.MapMethods("/gateway/{service}/{**path}", new[]{"GET","POST"}, async (string service, string? path, HttpContext context, IHttpClientFactory clients) => {
    var origin=service switch {"usage"=>app.Configuration["USAGE_URL"],"payments"=>app.Configuration["PAYMENTS_URL"],_=>null};
    if(origin is null || path is null || !path.StartsWith("api/v1/",StringComparison.Ordinal)) return Results.NotFound();
    var identity=identities.Identities.Single(i=>i.Name==context.User.Identity!.Name);
    using var message=new HttpRequestMessage(new HttpMethod(context.Request.Method),origin.TrimEnd('/')+"/"+path);
    message.Headers.Authorization=new AuthenticationHeaderValue("Bearer",identity.Token);
    if(context.Request.Method=="POST") {
        message.Content=new StreamContent(context.Request.Body);
        message.Content.Headers.ContentType=new MediaTypeHeaderValue("application/json");
    }
    try {
        using var response=await clients.CreateClient("services").SendAsync(message,context.RequestAborted);
        return Results.Content(await response.Content.ReadAsStringAsync(context.RequestAborted),"application/json",statusCode:(int)response.StatusCode);
    }
    catch(Exception e) when(e is HttpRequestException or TaskCanceledException) {
        return Results.Problem(statusCode:503,title:"This service is temporarily unavailable. Please retry shortly.");
    }
}).RequireAuthorization();
app.Run();
record Login(string Username,string? Password);
