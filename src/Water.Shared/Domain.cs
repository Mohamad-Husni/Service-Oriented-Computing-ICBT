using Microsoft.Data.Sqlite;

namespace Water.Shared;

public sealed class DomainException(int status, string message) : Exception(message)
{
    public int Status { get; } = status;
}

public static class Rules
{
    public static long Cents(decimal amount)
    {
        if (amount <= 0 || amount > 1_000_000 || decimal.Round(amount, 2) != amount)
            throw new DomainException(400, "Enter an amount between LKR 0.01 and 1,000,000 with at most two decimal places.");
        return checked((long)(amount * 100));
    }

    public static void Reading(decimal previous, decimal current, DateTimeOffset last, DateTimeOffset at, DateTimeOffset now)
    {
        if (current < previous || current > 10_000_000 || decimal.Round(current, 3) != current)
            throw new DomainException(400, "The cumulative reading must not decrease and allows at most three decimal places.");
        if (at <= last || at > now)
            throw new DomainException(400, "Reading time must be later than the previous reading and not in the future.");
    }

    public static string Reference(string? value)
    {
        if (string.IsNullOrWhiteSpace(value) || value.Length is < 8 or > 80 || !value.All(c => char.IsAsciiLetterOrDigit(c) || c is '-' or '_'))
            throw new DomainException(400, "Use an 8 to 80 character reference containing letters, numbers, hyphens or underscores.");
        return value;
    }
}

/// <summary>Each service passes its own database path; databases are never shared between domains.</summary>
public sealed class Database(string path)
{
    public SqliteConnection Open()
    {
        Directory.CreateDirectory(Path.GetDirectoryName(Path.GetFullPath(path))!);
        var c = new SqliteConnection(new SqliteConnectionStringBuilder { DataSource = path, DefaultTimeout = 15 }.ToString());
        c.Open();
        using var pragma = c.CreateCommand();
        pragma.CommandText = "PRAGMA foreign_keys=ON; PRAGMA journal_mode=WAL;";
        pragma.ExecuteNonQuery();
        return c;
    }

    public void Initialize(string sql)
    {
        using var c = Open();
        using var command = c.CreateCommand();
        command.CommandText = sql;
        command.ExecuteNonQuery();
    }
}

public static class Sql
{
    public static SqliteCommand Command(this SqliteConnection c, string sql, SqliteTransaction? transaction = null, params (string, object)[] parameters)
    {
        var command = c.CreateCommand();
        command.CommandText = sql;
        command.Transaction = transaction;
        foreach (var (key, value) in parameters) command.Parameters.AddWithValue(key, value);
        return command;
    }
}
