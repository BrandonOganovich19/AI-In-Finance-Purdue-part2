# Portfolio Engine Flowchart

This chart shows the portfolio estimation and search workflow used by the app.

```mermaid
flowchart TD
    A["Start: select input source"] --> B{"Meridian or uploaded CSV?"}
    B -->|Meridian| C["Load training returns, volatilities and correlations"]
    B -->|CSV| D["Validate tickers, dates and positive monthly prices"]
    D --> E["Calculate monthly returns: current price / previous price - 1"]
    E --> F["Use all monthly returns or the last 36"]
    F --> G["Estimate annual returns: monthly mean × 12"]
    G --> H["Estimate annual volatility: sample standard deviation × √12"]
    H --> I["Calculate correlations"]
    C --> J["Apply return estimates, objective and reserve eligibility"]
    I --> J
    J --> K["Validate inputs and build covariance matrix"]
    K --> L["Initialize best portfolio as None"]
    L --> M{"Another fully invested, long-only mix in 5-point steps?"}
    M -->|Yes| N["Calculate expected return and reserve weight"]
    N --> O{"Meets both objective and reserve minimum?"}
    O -->|No| M
    O -->|Yes| P["Calculate portfolio volatility"]
    P --> Q{"First feasible mix or lower volatility?"}
    Q -->|Yes| R["Save mix as best portfolio"]
    Q -->|No| M
    R --> M
    M -->|No| S{"Feasible portfolio found?"}
    S -->|Yes| T["Return weights, estimated return, volatility and reserve weight"]
    S -->|No| U["Return None: no mix meets the objective"]
    T --> V["App compares current inputs with loaded inputs"]
    U --> V
```

**Disclaimer: This project was made with Codex. I am not a financial advisor. For educational purposes only; this is not investment advice.**

