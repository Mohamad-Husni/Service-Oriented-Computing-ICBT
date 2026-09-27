using System.Net.Http.Headers;
using System.Net.Http.Json;
using Water.Contracts;
namespace Water.Desktop;
/// <summary>The desktop client consumes HTTP contracts only, never service repositories.</summary>
public sealed class PaymentClient : IDisposable
{
    private readonly HttpClient client;
    public PaymentClient(string origin, string token)
    {
        client = new HttpClient { BaseAddress = new Uri(origin), Timeout = TimeSpan.FromSeconds(10) };
        client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
    }
    public async Task<Balance> GetBalance(string account) => await Read<Balance>(await client.GetAsync($"/api/v1/accounts/{Uri.EscapeDataString(account)}/balance"));
    public async Task<PaymentResult> Pay(PaymentRequest request) => await Read<PaymentResult>(await client.PostAsJsonAsync("/api/v1/payments", request));
    private static async Task<T> Read<T>(HttpResponseMessage response)
    {
        using (response)
        {
            if (!response.IsSuccessStatusCode)
            {
                var error=await response.Content.ReadFromJsonAsync<System.Text.Json.JsonElement>();
                throw new InvalidOperationException(error.TryGetProperty("title",out var title) ? title.GetString() : "Payment service unavailable.");
            }
            return (await response.Content.ReadFromJsonAsync<T>())!;
        }
    }
    public void Dispose() => client.Dispose();
}
