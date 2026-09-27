using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Layout;
using Avalonia.Media;
using Avalonia.Themes.Fluent;
using Water.Contracts;
namespace Water.Desktop;

internal static class Program
{
    [STAThread]
    public static int Main(string[] args)
    {
        if (args.Contains("--smoke")) return Smoke().GetAwaiter().GetResult();
        BuildAvaloniaApp().StartWithClassicDesktopLifetime(args); return 0;
    }
    public static AppBuilder BuildAvaloniaApp() => AppBuilder.Configure<PaymentApplication>().UsePlatformDetect();
    private static async Task<int> Smoke()
    {
        using var client=new PaymentClient(Environment.GetEnvironmentVariable("PAYMENTS_URL")??"http://127.0.0.1:5102",Environment.GetEnvironmentVariable("PARTNER_TOKEN")??throw new InvalidOperationException("Set PARTNER_TOKEN."));
        var before=await client.GetBalance("100000001");
        var request=new PaymentRequest("100000001",1m,"DESKTOP-"+Guid.NewGuid().ToString("N"));
        var first=await client.Pay(request);var repeat=await client.Pay(request);var after=await client.GetBalance(request.AccountId);
        if(first.Replay || !repeat.Replay || first.Receipt.Id!=repeat.Receipt.Id || after.Outstanding!=before.Outstanding-1)throw new Exception("Desktop client regression.");
        Console.WriteLine("PASS Desktop HTTP balance; payment; retry identity; refreshed balance (4 checks)");return 0;
    }
}

public sealed class PaymentApplication : Application
{
    public override void Initialize(){Styles.Add(new FluentTheme());RequestedThemeVariant=Avalonia.Styling.ThemeVariant.Light;}
    public override void OnFrameworkInitializationCompleted()
    {
        if(ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop) desktop.MainWindow=new PaymentWindow();
        base.OnFrameworkInitializationCompleted();
    }
}

public sealed class PaymentWindow : Window
{
    private readonly TextBox account=new(){Text="100000001",PlaceholderText="Account number"};
    private readonly TextBox token=new(){PasswordChar='●',PlaceholderText="Partner API credential"};
    private readonly TextBox amount=new(){PlaceholderText="Amount in LKR"};
    private readonly TextBox reference=new(){Text="DESK-"+Guid.NewGuid().ToString("N")};
    private readonly TextBlock balance=new(){Text="Look up an account to see its balance",FontSize=22,TextWrapping=TextWrapping.Wrap};
    private readonly TextBlock status=new(){Text="Demonstration only. No money is transferred.",TextWrapping=TextWrapping.Wrap};
    private readonly Button lookup=new(){Content="Check balance",HorizontalAlignment=HorizontalAlignment.Stretch};
    private readonly Button pay=new(){Content="Record payment",HorizontalAlignment=HorizontalAlignment.Stretch};
    public PaymentWindow()
    {
        Title="WaterLink Partner Payments";Width=550;Height=760;MinWidth=440;MinHeight=680;
        token.Text=Environment.GetEnvironmentVariable("PARTNER_TOKEN")??"";
        var panel=new StackPanel{Margin=new Thickness(32),Spacing=12};
        panel.Children.Add(new TextBlock{Text="WaterLink",FontSize=30,FontWeight=FontWeight.Bold});
        panel.Children.Add(new TextBlock{Text="PARTNER PAYMENT DESK",FontSize=12});
        void Field(string label,Control control){panel.Children.Add(new TextBlock{Text=label});panel.Children.Add(control);}
        Field("Partner credential",token);Field("Customer account",account);panel.Children.Add(lookup);panel.Children.Add(balance);
        Field("Payment amount in LKR",amount);Field("Unique payment reference",reference);panel.Children.Add(pay);panel.Children.Add(status);
        Content=new ScrollViewer{Content=panel};
        lookup.Click+=async(_,_)=>await Execute(async client=>{var result=await client.GetBalance(account.Text??"");balance.Text=$"LKR {result.Outstanding:N2} outstanding";status.Text="Balance refreshed from the payment service.";});
        pay.Click+=async(_,_)=>await Execute(async client=>{
            if(!decimal.TryParse(amount.Text,System.Globalization.NumberStyles.Number,System.Globalization.CultureInfo.InvariantCulture,out var value))throw new InvalidOperationException("Enter a valid amount using a decimal point.");
            var result=await client.Pay(new(account.Text??"",value,reference.Text??""));
            status.Text=$"{(result.Replay?"Existing":"New")} receipt: {result.Receipt.Id}\nLKR {result.Receipt.Amount:N2}. Keep this reference for a retry; enter a new reference for a new payment.";
            balance.Text=$"LKR {(await client.GetBalance(account.Text??"")).Outstanding:N2} outstanding";
        });
    }
    private async Task Execute(Func<PaymentClient,Task> action)
    {
        lookup.IsEnabled=false;pay.IsEnabled=false;
        try{using var client=new PaymentClient(Environment.GetEnvironmentVariable("PAYMENTS_URL")??"http://127.0.0.1:5102",token.Text??"");await action(client);}
        catch(Exception e){status.Text=e.Message;}
        finally{lookup.IsEnabled=true;pay.IsEnabled=true;}
    }
}
