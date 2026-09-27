# WaterLink diagrams
All diagrams below are editable Mermaid source. The use case view uses Mermaid flowchart notation to show actors and actions. The two databases are separate; no cross-service foreign key is implied.

## Architecture

```mermaid
flowchart TB
 Customer[Customer browser] -->|Cookie session| Portal[ASP.NET Core portal]
 Operator[Meter operator browser] --> Portal
 Portal -->|Bearer HTTP JSON| Usage[Usage API 5101]
 Portal -->|Bearer HTTP JSON| Payments[Payment API 5102]
 Partner[Partner .NET desktop] -->|Bearer HTTP JSON| Payments
 Usage --> UsageDB[(Usage SQLite)]
 Payments --> PayDB[(Payments SQLite)]
 Contracts[Water.Contracts library] -.-> Payments
 Contracts -.-> Partner
```

## Use cases

```mermaid
flowchart LR
    C["Customer"]
    P["Payment partner"]
    O["Meter operator"]
    subgraph WaterLink["WaterLink key use cases"]
        B(["View balance"])
        Pay(["Record payment"])
        H(["View payment history"])
        U(["View recorded usage"])
        R(["Add meter reading"])
    end
    C --- B
    C --- Pay
    C --- H
    C --- U
    P --- B
    P --- Pay
    P --- H
    O --- U
    O --- R
```

## Classes

```mermaid
classDiagram
class PaymentClient {
  -HttpClient client
  +GetBalance(account)
  +Pay(request)
}
class PaymentRequest {
  +string AccountId
  +decimal Amount
  +string Reference
}
class IPaymentRepository {
  <<interface>>
  +Balance(account)
  +History(account, channel)
  +Record(request, channel)
}
class PaymentRepository {
  Database database
  +Balance(account)
  +History(account, channel)
  +Record(request, channel)
}
class Database {
  +Open()
  +Initialize(sql)
}
PaymentClient ..> PaymentRequest : sends through HTTP
PaymentRepository ..> PaymentRequest : reads
PaymentRepository ..|> IPaymentRepository
PaymentRepository --> Database : uses
note for PaymentClient "Calls the HTTP API, not the repository directly"
```

## Payment sequence

```mermaid
sequenceDiagram
    actor C as Web or desktop client
    participant A as Payment API
    participant R as PaymentRepository
    participant D as Payment database
    C->>A: POST payment with account, amount and reference
    A->>A: Authenticate and authorize caller
    A->>R: Record(request, channel)
    R->>R: Validate money and reference
    R->>D: BEGIN IMMEDIATE transaction
    R->>D: Find channel and reference
    D-->>R: Existing receipt or no match
    alt Matching account and amount
        R-->>A: Existing receipt, replay true
        A-->>C: 200 original receipt
    else Existing reference with changed payload
        R-->>A: Conflict; transaction disposed
        A-->>C: 409 conflict
    else New reference
        R->>D: Read remaining balance
        D-->>R: Available cents
        alt Amount exceeds balance
            R-->>A: Conflict; transaction rolled back
            A-->>C: 409 conflict
        else Valid payment
            R->>D: Insert receipt and COMMIT
            D-->>R: Saved
            R-->>A: New receipt, replay false
            A-->>C: 201 created
        end
    end
    C->>A: GET current balance
    A->>R: Balance(account)
    R->>D: Read billed cents minus paid cents
    D-->>R: Balance
    R-->>A: Balance record
    A-->>C: Current outstanding amount
```

## Data model

```mermaid
erDiagram
    Accounts ||--|{ Readings : has
    Bills ||--o{ Payments : receives
    Accounts {
        string Id PK
    }
    Readings {
        int Id PK
        string AccountId FK
        long MilliUnits
        string RecordedAt
        string RecordedBy
    }
    Bills {
        string AccountId PK
        long AmountCents
        string DueDate
    }
    Payments {
        string Id PK
        string AccountId FK
        long AmountCents
        string Reference
        string Channel
        string RecordedAt
    }
```
