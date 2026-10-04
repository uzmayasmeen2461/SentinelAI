# 🛡️ SentinelAI
## Risk & Regulatory Intelligence Copilot

SentinelAI is an AI-powered risk and regulatory intelligence copilot designed to help financial crime and compliance teams investigate suspicious activity faster, understand the evidence behind risk signals, and produce policy-grounded compliance findings with human oversight.

Built for the **Risk, Fraud and Regulatory Intelligence Copilot** challenge.

---

## 🎯 The Problem

Financial institutions process large volumes of transactions while compliance analysts must investigate potentially suspicious activity across fragmented data, risk signals, transaction histories, and regulatory policies.

Traditional investigation workflows can be:

- Time-consuming and highly manual
- Difficult to explain and audit
- Fragmented across multiple systems
- Prone to information overload
- Dependent on analysts manually connecting multiple risk indicators

Analysts need more than another alerting system. They need an investigation workspace that explains **why a customer is risky, what evidence supports the conclusion, and which policies may apply**.

---

## 💡 The Solution

**SentinelAI** transforms risk signals and transaction evidence into an explainable investigation workflow.

Instead of simply generating another risk alert, SentinelAI helps an analyst move through:

**Risk Detection → AI Investigation → Evidence Analysis → Compliance Finding → Human Decision**

The system combines deterministic risk signals with AI-assisted investigation to produce evidence-backed narratives while keeping the final compliance decision with the analyst.

---

## 🚀 Core Features

### 1. 📊 Risk Command Center

A centralized view of monitored customers, transactions, risk signals, and high-risk cases.

Analysts can:

- Review portfolio-level risk metrics
- Identify high-risk customers
- Compare risk scores
- Inspect active risk signals
- Prioritize cases requiring investigation

---

### 2. 🔎 AI Investigation Copilot

The investigation copilot assists analysts in understanding why a customer has been flagged.

It converts structured risk evidence into a concise investigation narrative designed to answer:

- What happened?
- Why is the activity suspicious?
- Which signals contributed to the risk?
- What evidence supports the finding?
- What should the analyst investigate next?

AI assists the investigation but does not make the final compliance decision.

---

### 3. 🧩 Evidence Workspace

The Evidence Workspace provides explainability behind each risk score.

It brings together:

- Customer risk score
- Individual risk signals
- Signal contribution breakdown
- Transaction timeline
- Transaction relationships
- Evidence chain
- Network visualization

This allows analysts to move from an AI-generated explanation back to the underlying evidence.

---

### 4. ⚖️ Compliance Finding

SentinelAI converts investigation evidence into a structured draft compliance finding.

The finding includes:

- Investigation summary
- Supporting evidence
- Relevant risk patterns
- Applicable policy references
- Analyst review controls

The analyst can then:

- **Approve the finding**, or
- **Request further investigation**

This human-in-the-loop workflow ensures that AI supports — rather than replaces — compliance professionals.

---

## 🧠 Risk Intelligence

The prototype demonstrates explainable risk detection patterns such as:

### Amount Clustering
Detects groups of transactions with similar amounts that may indicate structured or coordinated activity.

### Beneficiary Convergence
Detects transaction flows where funds from multiple paths converge toward a common beneficiary or account.

### Velocity / Rapid Activity
Identifies unusually rapid transaction behavior that may warrant additional investigation.

Each signal contributes to the overall risk score and remains visible to the analyst.

---

## 🏗️ Architecture

```text
┌───────────────────────────────┐
│       Financial / Risk Data   │
│    Customers + Transactions   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│       Risk Signal Engine      │
│                               │
│ • Amount Clustering           │
│ • Beneficiary Convergence     │
│ • Velocity / Rapid Activity   │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│      Risk Scoring Layer       │
│   Evidence + Signal Scores    │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│    AI Investigation Layer     │
│                               │
│ Evidence-backed narratives    │
│ Investigation assistance      │
│ Policy-grounded findings      │
└───────────────┬───────────────┘
                │
                ▼
┌──────────────────────────────────────────┐
│           SentinelAI UI                  │
│                                          │
│  Risk Command Center                    │
│          ↓                               │
│  AI Investigation Copilot               │
│          ↓                               │
│  Evidence Workspace                     │
│          ↓                               │
│  Compliance Finding                     │
└──────────────────┬───────────────────────┘
                   │
                   ▼
┌───────────────────────────────┐
│       Human Analyst           │
│                               │
│ Approve Finding               │
│          OR                   │
│ Request Further Investigation│
└───────────────────────────────┘
```

---

## ❄️ Built on Snowflake

SentinelAI is deployed as a **Streamlit in Snowflake** application.

The solution uses Snowflake as the foundation for bringing together data, analytics, AI-assisted investigation, and the application experience.

### Technology Stack

| Layer | Technology |
|---|---|
| Application | Streamlit |
| Platform | Snowflake |
| Language | Python |
| Data Processing | Pandas |
| Visualization | Plotly |
| Network Analysis | NetworkX |
| Graph Visualization | Graphviz |
| AI / Investigation | Snowflake AI capabilities |
| Deployment | Streamlit in Snowflake |

---

## 🔄 Investigation Workflow

A typical SentinelAI investigation follows this flow:

```text
1. Risk Command Center
        ↓
2. Identify a high-risk customer
        ↓
3. Open AI Investigation Copilot
        ↓
4. Generate evidence-backed investigation narrative
        ↓
5. Review supporting evidence
        ↓
6. Analyze transaction patterns and relationships
        ↓
7. Generate draft compliance finding
        ↓
8. Review relevant policy references
        ↓
9. Analyst approves or requests further investigation
```

This creates a traceable path from **risk signal to human decision**.

---

## 🤖 Responsible AI & Human Oversight

SentinelAI is intentionally designed as a **copilot rather than an autonomous decision-maker**.

AI-generated investigation narratives and compliance findings are treated as recommendations.

Key design principles include:

- Human-in-the-loop decision making
- Evidence-backed AI responses
- Explainable risk scoring
- Visible signal contributions
- Traceability from finding to evidence
- Policy references
- Analyst approval before final action

The goal is to improve analyst productivity without removing human accountability from high-impact compliance decisions.

---

## 🔍 Example Investigation

A high-risk customer may receive multiple signals such as:

```text
Customer
   │
   ├── Amount Clustering
   │        └── +30 Risk
   │
   └── Beneficiary Convergence
            └── +40 Risk

Total Risk Score: 70
```

The analyst can then inspect the transactions behind those signals, visualize account relationships, review the AI investigation narrative, and determine whether the evidence supports a compliance finding.

---

## 📁 Project Structure

```text
SentinelAI/
│
├── streamlit_app.py
├── utils.py
├── environment.yml
├── pyproject.toml
├── snowflake.yml
│
├── .streamlit/
│   └── config.toml
│
└── pages/
    ├── 1_Risk_Command_Center.py
    ├── 2_AI_Investigation.py
    ├── 3_Evidence_Workspace.py
    └── 4_Compliance_Finding.py
```

---

## ▶️ Running the Application

### Prerequisites

- Snowflake account
- Snowflake CLI
- Python environment
- Access to the required Snowflake database, schema, warehouse, and AI capabilities

### Deploy to Snowflake

Using a configured Snowflake CLI connection:

```bash
snow streamlit deploy -c <CONNECTION_NAME> --replace
```

Retrieve the deployed application URL:

```bash
snow streamlit get-url SENTINELAI_APP -c <CONNECTION_NAME>
```

> Connection names, credentials, passwords, tokens, and other secrets are intentionally excluded from this repository.

---

## 🔐 Security

Sensitive credentials are not stored in the repository.

The project excludes:

```text
.env
.env.*
.streamlit/secrets.toml
.venv/
```

Secrets should be managed using appropriate Snowflake or environment-specific secret-management mechanisms.

---

## 🧪 Prototype Scope

SentinelAI is a hackathon prototype demonstrating how AI can augment financial crime and regulatory investigations.

The current implementation focuses on:

- Risk prioritization
- Explainable risk signals
- Evidence-driven investigations
- Transaction relationship analysis
- AI-assisted investigation narratives
- Policy-grounded compliance findings
- Human review and approval

The data and investigation scenarios used in the prototype are intended for demonstration purposes.

---

## 🌟 Why SentinelAI?

Many systems stop at:

> **"This customer is high risk."**

SentinelAI is designed to go further:

> **"This customer is high risk, these signals contributed to the score, this is the supporting transaction evidence, this is the investigation narrative, these policies are relevant, and a human analyst makes the final decision."**

That shift from **alert generation to explainable investigation** is the core idea behind SentinelAI.

---

## 🏆 Hackathon Challenge

**Risk, Fraud and Regulatory Intelligence Copilot**

SentinelAI demonstrates how Snowflake and AI can be combined to create a more explainable, evidence-driven, and human-centered approach to financial risk and regulatory investigation.

---

## 👩‍💻 Author

**Uzma Yasmeen**

Built as a hackathon prototype using Snowflake, Streamlit, Python, analytics, visualization, and AI-assisted investigation.