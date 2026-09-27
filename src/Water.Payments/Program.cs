using Water.Contracts;
using Water.Shared;
using Water.Payments;
using System.Security.Claims;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton(new Database(builder.Configuration["DATA_PATH"] ?? ".data/payments.db"));
builder.Services.AddSingleton<IdentityRegistry>();
builder.Services.AddSingleton<IPaymentRepository, PaymentRepository>();
var app = builder.Build();
((PaymentRepository)app.Services.GetRequiredService<IPaymentRepository>()).Initialize();
app.UseServiceSecurity(app.Services.GetRequiredService<IdentityRegistry>());
app.MapGet("/health", () => Results.Ok(new { status = "healthy", service = "payments" }));
app.MapGet("/api/v1/accounts/{account}/balance", (string account, HttpContext context, IPaymentRepository store) => {
    ServiceSecurity.Allow(context.User, account);
    return Results.Ok(store.Balance(account));
});
app.MapGet("/api/v1/accounts/{account}/payments", (string account, HttpContext context, IPaymentRepository store) => {
    ServiceSecurity.Allow(context.User, account);
    store.Balance(account);
    return Results.Ok(store.History(account, context.User.IsInRole("partner") ? context.User.Identity!.Name : null));
});
app.MapPost("/api/v1/payments", (PaymentRequest request, HttpContext context, IPaymentRepository store) => {
    if (context.User.IsInRole("operator")) throw new DomainException(403, "Operators cannot record payments.");
    ServiceSecurity.Allow(context.User, request.AccountId);
    var result = store.Record(request, context.User.Identity!.Name!);
    return Results.Json(new { receipt = result.Receipt, replay = result.Replay }, statusCode: result.Replay ? 200 : 201);
});
app.Run();
