namespace Water.Contracts;
/// <summary>Version 1 public message contracts. No persistence or user-interface dependencies.</summary>
public sealed record PaymentRequest(string AccountId, decimal Amount, string Reference);
public sealed record Receipt(string Id, string AccountId, decimal Amount, string Reference, string Channel, string RecordedAt);
public sealed record Balance(string AccountId, decimal Billed, decimal Paid, decimal Outstanding, string DueDate, string AsOf);
public sealed record PaymentResult(Receipt Receipt, bool Replay);
