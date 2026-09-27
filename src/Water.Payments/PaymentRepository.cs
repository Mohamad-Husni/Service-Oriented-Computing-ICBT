using Water.Contracts;
using Water.Shared;
namespace Water.Payments;

public interface IPaymentRepository
{
    Balance Balance(string account);
    IReadOnlyList<Receipt> History(string account, string? channel);
    (Receipt Receipt, bool Replay) Record(PaymentRequest request, string channel);
}

public sealed class PaymentRepository(Database database) : IPaymentRepository
{
    public void Initialize() => database.Initialize("""
        CREATE TABLE IF NOT EXISTS Bills(AccountId TEXT PRIMARY KEY, AmountCents INTEGER NOT NULL CHECK(AmountCents>=0), DueDate TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS Payments(Id TEXT PRIMARY KEY, AccountId TEXT NOT NULL REFERENCES Bills(AccountId), AmountCents INTEGER NOT NULL CHECK(AmountCents>0), Reference TEXT NOT NULL, Channel TEXT NOT NULL, RecordedAt TEXT NOT NULL, UNIQUE(Channel, Reference));
        INSERT OR IGNORE INTO Bills VALUES('100000001',425000,'2026-10-15'),('100000002',260000,'2026-10-15');
        """);

    public Balance Balance(string account)
    {
        using var c = database.Open();
        using var command = c.Command("SELECT b.AmountCents, COALESCE(SUM(p.AmountCents),0), b.DueDate FROM Bills b LEFT JOIN Payments p ON p.AccountId=b.AccountId WHERE b.AccountId=$a GROUP BY b.AccountId", null, ("$a", account));
        using var r = command.ExecuteReader();
        if (!r.Read()) throw new DomainException(404, "Account not found.");
        return new(account, r.GetInt64(0)/100m, r.GetInt64(1)/100m, (r.GetInt64(0)-r.GetInt64(1))/100m, r.GetString(2), DateTimeOffset.UtcNow.ToString("O"));
    }

    public IReadOnlyList<Receipt> History(string account, string? channel)
    {
        using var c = database.Open();
        using var command = c.Command("SELECT Id,AccountId,AmountCents,Reference,Channel,RecordedAt FROM Payments WHERE AccountId=$a AND ($channel='' OR Channel=$channel) ORDER BY RecordedAt DESC LIMIT 100", null, ("$a", account), ("$channel", channel ?? ""));
        using var r = command.ExecuteReader();
        var result = new List<Receipt>();
        while (r.Read()) result.Add(Read(r));
        return result;
    }

    public (Receipt Receipt, bool Replay) Record(PaymentRequest request, string channel)
    {
        var cents = Rules.Cents(request.Amount);
        var reference = Rules.Reference(request.Reference);
        using var c = database.Open();
        // An immediate transaction serializes competing payments before checking available balance.
        using var tx = c.BeginTransaction(deferred: false);
        using (var duplicate = c.Command("SELECT Id,AccountId,AmountCents,Reference,Channel,RecordedAt FROM Payments WHERE Channel=$channel AND Reference=$r", tx, ("$channel", channel), ("$r", reference)))
        using (var reader = duplicate.ExecuteReader())
        {
            if (reader.Read())
            {
                var existing = Read(reader);
                if (existing.AccountId != request.AccountId || existing.Amount != request.Amount)
                    throw new DomainException(409, "This reference was already used for a different payment.");
                return (existing, true);
            }
        }
        using var balance = c.Command("SELECT AmountCents-COALESCE((SELECT SUM(AmountCents) FROM Payments WHERE AccountId=$a),0) FROM Bills WHERE AccountId=$a", tx, ("$a", request.AccountId));
        var available = balance.ExecuteScalar();
        if (available is null) throw new DomainException(404, "Account not found.");
        if (cents > Convert.ToInt64(available)) throw new DomainException(409, "Payment exceeds the outstanding balance. Refresh the account before paying.");
        var receipt = new Receipt(Guid.NewGuid().ToString("N"), request.AccountId, request.Amount, reference, channel, DateTimeOffset.UtcNow.ToString("O"));
        using var insert = c.Command("INSERT INTO Payments VALUES($id,$a,$amount,$r,$channel,$at)", tx, ("$id", receipt.Id), ("$a", receipt.AccountId), ("$amount", cents), ("$r", receipt.Reference), ("$channel", receipt.Channel), ("$at", receipt.RecordedAt));
        insert.ExecuteNonQuery();
        tx.Commit();
        return (receipt, false);
    }
    private static Receipt Read(Microsoft.Data.Sqlite.SqliteDataReader r) => new(r.GetString(0),r.GetString(1),r.GetInt64(2)/100m,r.GetString(3),r.GetString(4),r.GetString(5));
}
