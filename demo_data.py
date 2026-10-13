

import pandas as pd

# Synthetic data for hackathon evaluation.
# No Snowflake connection required.

CUSTOMERS = [
    {
        "CUSTOMER_ID": "CUST-1042",
        "FULL_NAME": "Viktor Reznikov",
        "COUNTRY": "UAE",
        "KYC_RISK_RATING": "HIGH",
        "TOTAL_RISK_SCORE": 70,
        "SIGNAL_COUNT": 2,
        "HIGH_SEVERITY_COUNT": 2,
        "LATEST_SIGNAL_AT": "2026-10-03",
        "SIGNAL_TYPES": "BENEFICIARY_CONVERGENCE, AMOUNT_CLUSTERING",
    },
    {
        "CUSTOMER_ID": "CUST-GEO-01",
        "FULL_NAME": "Demo Customer - Geographic Risk",
        "COUNTRY": "UAE",
        "KYC_RISK_RATING": "HIGH",
        "TOTAL_RISK_SCORE": 60,
        "SIGNAL_COUNT": 2,
        "HIGH_SEVERITY_COUNT": 1,
        "LATEST_SIGNAL_AT": "2026-10-03",
        "SIGNAL_TYPES": "GEOGRAPHIC_RISK",
    },
    {
        "CUSTOMER_ID": "CUST-RAPID-01",
        "FULL_NAME": "Demo Customer - Rapid Movement",
        "COUNTRY": "UAE",
        "KYC_RISK_RATING": "MEDIUM",
        "TOTAL_RISK_SCORE": 35,
        "SIGNAL_COUNT": 2,
        "HIGH_SEVERITY_COUNT": 0,
        "LATEST_SIGNAL_AT": "2026-10-03",
        "SIGNAL_TYPES": "RAPID_MOVEMENT",
    },
    {
        "CUSTOMER_ID": "CUST-VELOCITY-01",
        "FULL_NAME": "Demo Customer - Velocity",
        "COUNTRY": "UAE",
        "KYC_RISK_RATING": "MEDIUM",
        "TOTAL_RISK_SCORE": 25,
        "SIGNAL_COUNT": 1,
        "HIGH_SEVERITY_COUNT": 0,
        "LATEST_SIGNAL_AT": "2026-10-03",
        "SIGNAL_TYPES": "TRANSACTION_VELOCITY",
    },
]


def get_demo_kpis():
    return {
        "TOTAL_CUSTOMERS": 200,
        "TOTAL_TRANSACTIONS": 10001,
        "ACTIVE_SIGNALS": 7,
        "HIGH_RISK_CUSTOMERS": 4,
    }


def get_demo_risk_summary():
    return pd.DataFrame(CUSTOMERS)


def get_demo_signals_by_type():
    return pd.DataFrame([
        {"SIGNAL_TYPE": "BENEFICIARY_CONVERGENCE", "COUNT": 1},
        {"SIGNAL_TYPE": "AMOUNT_CLUSTERING", "COUNT": 1},
        {"SIGNAL_TYPE": "GEOGRAPHIC_RISK", "COUNT": 2},
        {"SIGNAL_TYPE": "RAPID_MOVEMENT", "COUNT": 2},
        {"SIGNAL_TYPE": "TRANSACTION_VELOCITY", "COUNT": 1},
    ])


def get_demo_signals_by_severity():
    return pd.DataFrame([
        {"SEVERITY": "HIGH", "COUNT": 3},
        {"SEVERITY": "MEDIUM", "COUNT": 4},
    ])
def get_demo_investigation(question: str) -> dict:
    """Return a simulated Cortex Agent response for the hackathon demo."""

    response = """
### Investigation Summary — CUST-1042

**Risk assessment:** HIGH (Risk Score: 70)

Customer CUST-1042 has triggered two high-severity risk signals:

1. **Beneficiary Convergence (+40 points):**
   Funds move through multiple intermediary accounts toward a common beneficiary, suggesting a potential layering pattern.

2. **Amount Clustering (+30 points):**
   Multiple transactions with similar amounts occur within a short period, indicating possible structuring behavior.

### Supporting Evidence
- Automated risk signals from the SentinelAI detection workflow.
- Transaction relationships connecting customer accounts to intermediary and beneficiary accounts.
- Risk scoring based on the identified transaction patterns.

### Applicable Policies
- **POL-AML-003:** Review potential beneficiary convergence and layering.
- **POL-AML-001:** Investigate clustered transaction amounts.

### Recommended Action
Escalate the case for enhanced due diligence and analyst review. Validate the transaction evidence before making any regulatory determination.

**Note:** This is a simulated investigation using synthetic hackathon data. No live Snowflake Cortex Agent was invoked.
"""

    return {
        "content": [
            {
                "type": "text",
                "text": response.strip()
            }
        ]
    }


# Synthetic evidence data for the public hackathon demo.

DEMO_ACCOUNTS = [
    {"ACCOUNT_ID": "ACC-1042-A", "CUSTOMER_ID": "CUST-1042"},
    {"ACCOUNT_ID": "ACC-1042-B", "CUSTOMER_ID": "CUST-1042"},
]

DEMO_TRANSACTIONS = [
    {
        "TRANSACTION_ID": "TXN-1001",
        "SOURCE_ACCOUNT_ID": "ACC-1042-A",
        "DESTINATION_ACCOUNT_ID": "ACC-BEN-01",
        "AMOUNT": 9800.0,
        "CURRENCY": "USD",
        "TRANSACTION_TYPE": "TRANSFER",
        "TRANSACTION_TIMESTAMP": "2026-10-03 09:10:00",
        "SOURCE_COUNTRY": "UAE",
        "DESTINATION_COUNTRY": "UAE",
    },
    {
        "TRANSACTION_ID": "TXN-1002",
        "SOURCE_ACCOUNT_ID": "ACC-1042-A",
        "DESTINATION_ACCOUNT_ID": "ACC-BEN-02",
        "AMOUNT": 9900.0,
        "CURRENCY": "USD",
        "TRANSACTION_TYPE": "TRANSFER",
        "TRANSACTION_TIMESTAMP": "2026-10-03 09:15:00",
        "SOURCE_COUNTRY": "UAE",
        "DESTINATION_COUNTRY": "UAE",
    },
    {
        "TRANSACTION_ID": "TXN-1003",
        "SOURCE_ACCOUNT_ID": "ACC-1042-B",
        "DESTINATION_ACCOUNT_ID": "ACC-BEN-03",
        "AMOUNT": 9750.0,
        "CURRENCY": "USD",
        "TRANSACTION_TYPE": "TRANSFER",
        "TRANSACTION_TIMESTAMP": "2026-10-03 09:20:00",
        "SOURCE_COUNTRY": "UAE",
        "DESTINATION_COUNTRY": "UAE",
    },
    {
        "TRANSACTION_ID": "TXN-1004",
        "SOURCE_ACCOUNT_ID": "ACC-BEN-01",
        "DESTINATION_ACCOUNT_ID": "ACC-HUB-001",
        "AMOUNT": 9500.0,
        "CURRENCY": "USD",
        "TRANSACTION_TYPE": "TRANSFER",
        "TRANSACTION_TIMESTAMP": "2026-10-03 10:00:00",
        "SOURCE_COUNTRY": "UAE",
        "DESTINATION_COUNTRY": "UAE",
    },
    {
        "TRANSACTION_ID": "TXN-1005",
        "SOURCE_ACCOUNT_ID": "ACC-BEN-02",
        "DESTINATION_ACCOUNT_ID": "ACC-HUB-001",
        "AMOUNT": 9600.0,
        "CURRENCY": "USD",
        "TRANSACTION_TYPE": "TRANSFER",
        "TRANSACTION_TIMESTAMP": "2026-10-03 10:05:00",
        "SOURCE_COUNTRY": "UAE",
        "DESTINATION_COUNTRY": "UAE",
    },
    {
        "TRANSACTION_ID": "TXN-1006",
        "SOURCE_ACCOUNT_ID": "ACC-BEN-03",
        "DESTINATION_ACCOUNT_ID": "ACC-HUB-001",
        "AMOUNT": 9400.0,
        "CURRENCY": "USD",
        "TRANSACTION_TYPE": "TRANSFER",
        "TRANSACTION_TIMESTAMP": "2026-10-03 10:10:00",
        "SOURCE_COUNTRY": "UAE",
        "DESTINATION_COUNTRY": "UAE",
    },
]

DEMO_SIGNALS = [
    {
        "SIGNAL_ID": "SIG-1042-01",
        "CUSTOMER_ID": "CUST-1042",
        "SIGNAL_TYPE": "BENEFICIARY_CONVERGENCE",
        "SEVERITY": "HIGH",
        "RISK_POINTS": 40,
        "TRANSACTION_ID": "TXN-1004",
        "DETECTED_AT": "2026-10-03",
        "EVIDENCE_DESCRIPTION": (
            "Multiple intermediary accounts transfer funds "
            "to the same beneficiary account."
        ),
    },
    {
        "SIGNAL_ID": "SIG-1042-02",
        "CUSTOMER_ID": "CUST-1042",
        "SIGNAL_TYPE": "AMOUNT_CLUSTERING",
        "SEVERITY": "HIGH",
        "RISK_POINTS": 30,
        "TRANSACTION_ID": "TXN-1002",
        "DETECTED_AT": "2026-10-03",
        "EVIDENCE_DESCRIPTION": (
            "Several transactions of similar amounts "
            "occurred within a short period."
        ),
    },
]


def get_demo_customer_detail(cid: str):
    return pd.DataFrame([
        customer for customer in CUSTOMERS
        if customer["CUSTOMER_ID"] == cid
    ])


def get_demo_customer_accounts(cid: str):
    return pd.DataFrame([
        account for account in DEMO_ACCOUNTS
        if account["CUSTOMER_ID"] == cid
    ], columns=["ACCOUNT_ID", "CUSTOMER_ID"])


def get_demo_customer_signals(cid: str):
    columns = [
        "SIGNAL_ID", "SIGNAL_TYPE", "SEVERITY",
        "RISK_POINTS", "TRANSACTION_ID",
        "DETECTED_AT", "EVIDENCE_DESCRIPTION",
    ]
    return pd.DataFrame([
        {key: signal[key] for key in columns}
        for signal in DEMO_SIGNALS
        if signal["CUSTOMER_ID"] == cid
    ], columns=columns)


def get_demo_customer_transactions(cid: str):
    account_ids = {
        account["ACCOUNT_ID"]
        for account in DEMO_ACCOUNTS
        if account["CUSTOMER_ID"] == cid
    }
    return pd.DataFrame([
        transaction for transaction in DEMO_TRANSACTIONS
        if transaction["SOURCE_ACCOUNT_ID"] in account_ids
        or transaction["DESTINATION_ACCOUNT_ID"] in account_ids
    ], columns=list(DEMO_TRANSACTIONS[0].keys()))


def get_demo_flagged_txn_ids(cid: str):
    return {
        signal["TRANSACTION_ID"]
        for signal in DEMO_SIGNALS
        if signal["CUSTOMER_ID"] == cid
        and signal["TRANSACTION_ID"] is not None
    }


def get_demo_network_dot(cid: str):
    accounts = get_demo_customer_accounts(cid)
    if accounts.empty:
        return ""

    account_ids = set(accounts["ACCOUNT_ID"])
    hop1 = [
        txn for txn in DEMO_TRANSACTIONS
        if txn["SOURCE_ACCOUNT_ID"] in account_ids
        or txn["DESTINATION_ACCOUNT_ID"] in account_ids
    ]

    external_ids = {
        account
        for txn in hop1
        for account in (
            txn["SOURCE_ACCOUNT_ID"],
            txn["DESTINATION_ACCOUNT_ID"],
        )
        if account not in account_ids
    }

    hop2 = [
        txn for txn in DEMO_TRANSACTIONS
        if txn["SOURCE_ACCOUNT_ID"] in external_ids
    ]

    flagged_ids = get_demo_flagged_txn_ids(cid)

    dot = [
        "digraph G {",
        "rankdir=LR;",
        'bgcolor="transparent";',
        'node [shape=box, style="filled,rounded"];',
    ]

    for account in sorted(account_ids):
        dot.append(
            f'"{account}" [fillcolor="#1B6B93", fontcolor="white"];'
        )

    for account in sorted(external_ids | {"ACC-HUB-001"}):
        if account not in account_ids:
            dot.append(
                f'"{account}" [fillcolor="#F0F4F8"];'
            )

    seen = set()
    for txn in hop1 + hop2:
        src = txn["SOURCE_ACCOUNT_ID"]
        dst = txn["DESTINATION_ACCOUNT_ID"]
        if (src, dst) in seen:
            continue
        seen.add((src, dst))

        color = (
            "#D32F2F"
            if txn["TRANSACTION_ID"] in flagged_ids
            else "#90A4AE"
        )
        amount = f'${txn["AMOUNT"]:,.0f}'
        dot.append(
            f'"{src}" -> "{dst}" '
            f'[label="{amount}", color="{color}"];'
        )

    dot.append("}")
    return "\n".join(dot)
