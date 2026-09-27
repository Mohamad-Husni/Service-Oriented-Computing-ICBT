using Water.Shared;
namespace Water.Usage;

public sealed record ReadingRequest(decimal MeterValue, DateTimeOffset RecordedAt);
public sealed record MeterReading(long Id, decimal MeterValue, string RecordedAt, string RecordedBy);
public sealed record UsageSummary(string AccountId, string CustomerName, string Address, decimal Consumption, string Unit, IReadOnlyList<MeterReading> Readings, string AsOf);

public interface IUsageRepository
{
    UsageSummary Get(string account);
    void Record(string account, ReadingRequest request, string actor);
}

public sealed class UsageRepository(Database database) : IUsageRepository
{
    public void Initialize() => database.Initialize("""
        CREATE TABLE IF NOT EXISTS Accounts(Id TEXT PRIMARY KEY, Name TEXT NOT NULL, Address TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS Readings(Id INTEGER PRIMARY KEY AUTOINCREMENT,AccountId TEXT NOT NULL REFERENCES Accounts(Id),MilliUnits INTEGER NOT NULL CHECK(MilliUnits>=0),RecordedAt TEXT NOT NULL,RecordedBy TEXT NOT NULL,UNIQUE(AccountId,RecordedAt));
        INSERT OR IGNORE INTO Accounts VALUES('100000001','Amani Perera','Colombo 05'),('100000002','Dilan Silva','Kandy');
        INSERT OR IGNORE INTO Readings(Id,AccountId,MilliUnits,RecordedAt,RecordedBy) VALUES
        (1,'100000001',1240000,'2026-08-25T09:00:00.0000000+00:00','seed'),
        (2,'100000001',1258000,'2026-09-25T09:00:00.0000000+00:00','seed'),
        (3,'100000002',870000,'2026-08-25T09:00:00.0000000+00:00','seed'),
        (4,'100000002',882000,'2026-09-25T09:00:00.0000000+00:00','seed');
        """);
    public UsageSummary Get(string account)
    {
        using var c = database.Open();
        using var command = c.Command("SELECT Name,Address FROM Accounts WHERE Id=$a", null, ("$a",account));
        using var reader = command.ExecuteReader();
        if (!reader.Read()) throw new DomainException(404,"Account not found.");
        var name = reader.GetString(0); var address = reader.GetString(1); reader.Close();
        using var history = c.Command("SELECT Id,MilliUnits,RecordedAt,RecordedBy FROM Readings WHERE AccountId=$a ORDER BY RecordedAt DESC LIMIT 12", null, ("$a",account));
        using var r = history.ExecuteReader();
        var readings = new List<MeterReading>();
        while(r.Read()) readings.Add(new(r.GetInt64(0),r.GetInt64(1)/1000m,r.GetString(2),r.GetString(3)));
        var used = readings.Count >= 2 ? readings[0].MeterValue-readings[1].MeterValue : 0;
        return new(account,name,address,used,"m³",readings,DateTimeOffset.UtcNow.ToString("O"));
    }
    public void Record(string account, ReadingRequest request, string actor)
    {
        using var c=database.Open();
        using var tx=c.BeginTransaction(deferred:false);
        using var command=c.Command("SELECT MilliUnits,RecordedAt FROM Readings WHERE AccountId=$a ORDER BY RecordedAt DESC LIMIT 1",tx,("$a",account));
        using var r=command.ExecuteReader();
        if(!r.Read()) throw new DomainException(404,"Account not found.");
        Rules.Reading(r.GetInt64(0)/1000m,request.MeterValue,DateTimeOffset.Parse(r.GetString(1)),request.RecordedAt,DateTimeOffset.UtcNow);
        r.Close();
        using var insert=c.Command("INSERT INTO Readings(AccountId,MilliUnits,RecordedAt,RecordedBy) VALUES($a,$v,$at,$by)",tx,("$a",account),("$v",(long)(request.MeterValue*1000)),("$at",request.RecordedAt.ToUniversalTime().ToString("O")),("$by",actor));
        insert.ExecuteNonQuery();
        tx.Commit();
    }
}
