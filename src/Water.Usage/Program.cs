using Water.Shared;
using Water.Usage;
var builder=WebApplication.CreateBuilder(args);
builder.Services.AddSingleton(new Database(builder.Configuration["DATA_PATH"] ?? ".data/usage.db"));
builder.Services.AddSingleton<IdentityRegistry>();
builder.Services.AddSingleton<IUsageRepository,UsageRepository>();
var app=builder.Build();
((UsageRepository)app.Services.GetRequiredService<IUsageRepository>()).Initialize();
app.UseServiceSecurity(app.Services.GetRequiredService<IdentityRegistry>());
app.MapGet("/health",()=>Results.Ok(new{status="healthy",service="usage"}));
app.MapGet("/api/v1/accounts/{account}/usage",(string account,HttpContext context,IUsageRepository store)=>{
    ServiceSecurity.Allow(context.User,account,partners:false);
    return Results.Ok(store.Get(account));
});
app.MapPost("/api/v1/accounts/{account}/readings",(string account,ReadingRequest request,HttpContext context,IUsageRepository store)=>{
    if(!context.User.IsInRole("operator")) throw new DomainException(403,"Only meter operators can record readings.");
    store.Record(account,request,context.User.Identity!.Name!);
    return Results.Json(store.Get(account),statusCode:201);
});
app.Run();
