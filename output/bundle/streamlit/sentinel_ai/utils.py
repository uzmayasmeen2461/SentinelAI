import streamlit as st
import json
import re
import pandas as pd

import logging

_log = logging.getLogger(__name__)

AGENT_FQN = "SENTINEL_AI_DB.COMPLIANCE.SENTINEL_INVESTIGATION_AGENT"
SEARCH_FQN = "SENTINEL_AI_DB.COMPLIANCE.SENTINEL_POLICY_SEARCH"
DB = "SENTINEL_AI_DB"


def get_session():
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        return st.connection("snowflake").session()


@st.cache_data(ttl=300)
def run_query(sql: str) -> pd.DataFrame:
    session = get_session()
    return session.sql(sql).to_pandas()


def call_agent(question: str) -> dict:
    session = get_session()
    payload = {
        "messages": [
            {"role": "user", "content": [{"type": "text", "text": question}]}
        ]
    }
    payload_json = json.dumps(payload).replace("'", "\\'")
    sql = f"""
        SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
            '{AGENT_FQN}',
            $${json.dumps(payload)}$$,
            TRUE
        )
    """
    try:
        rows = session.sql(sql).collect()
    except Exception as e:
        _log.error("Cortex Agent call failed: %s", e)
        raise RuntimeError(
            "The investigation service is temporarily unavailable. Please try again."
        ) from e
    if not rows or rows[0][0] is None:
        return {"content": []}
    raw = str(rows[0][0])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"content": [{"type": "text", "text": raw}]}


_NARRATION_RE = re.compile(
    r"^(I'll |I will |Let me |Now let me |Now I'll |Now I will |"
    r"I have the |I need to |I'm going to |Let's |I'll now |"
    r"First,? I'll |First,? let me |Next,? I'll |Next,? let me |"
    r"Let me fix |Let me check |Let me also )",
    re.IGNORECASE,
)


def _clean_narration(text: str) -> str:
    """Strip intermediate chain-of-thought narration lines."""
    lines = text.split("\n")
    cleaned = [ln for ln in lines if not _NARRATION_RE.match(ln.strip())]
    while cleaned and not cleaned[0].strip():
        cleaned.pop(0)
    return "\n".join(cleaned)


def extract_agent_text(response: dict) -> str:
    texts = []
    for block in response.get("content", []):
        if block.get("type") == "text":
            texts.append(block["text"])
    if not texts:
        return ""
    final = _clean_narration(texts[-1])
    return final


def save_analyst_decision(case_id: str, customer_id: str, decision: str, comment: str) -> None:
    session = get_session()
    session.sql(
        "INSERT INTO SENTINEL_AI_DB.COMPLIANCE.ANALYST_DECISIONS "
        "(CASE_ID, CUSTOMER_ID, DECISION, ANALYST_COMMENT, DECISION_TIMESTAMP) "
        "VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP())",
        params=[case_id, customer_id, decision, comment],
    ).collect()


def search_policy(query: str, limit: int = 3) -> list:
    session = get_session()
    search_params = json.dumps({
        "query": query,
        "columns": ["policy_id", "policy_title", "policy_text",
                     "recommended_action", "evidence_required"],
        "limit": limit
    })
    sql = f"""
        SELECT PARSE_JSON(
            SNOWFLAKE.CORTEX.SEARCH_PREVIEW(
                '{SEARCH_FQN}',
                $${search_params}$$
            )
        )['results'] AS results
    """
    try:
        rows = session.sql(sql).collect()
    except Exception as e:
        _log.error("Policy search failed: %s", e)
        return []
    if not rows or rows[0][0] is None:
        return []
    raw = str(rows[0][0])
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return []


@st.cache_data(ttl=300)
def get_kpis() -> dict:
    df = run_query(f"""
        SELECT
            (SELECT COUNT(*) FROM {DB}.CORE.CUSTOMERS) AS total_customers,
            (SELECT COUNT(*) FROM {DB}.CORE.TRANSACTIONS) AS total_transactions,
            (SELECT COUNT(*) FROM {DB}.RISK.RISK_SIGNALS) AS active_signals,
            (SELECT COUNT(DISTINCT customer_id) FROM {DB}.RISK.RISK_SIGNALS) AS high_risk_customers
    """)
    if df.empty:
        return {"TOTAL_CUSTOMERS": 0, "TOTAL_TRANSACTIONS": 0,
                "ACTIVE_SIGNALS": 0, "HIGH_RISK_CUSTOMERS": 0}
    return df.iloc[0].to_dict()


@st.cache_data(ttl=300)
def get_signals_by_type() -> pd.DataFrame:
    return run_query(f"""
        SELECT signal_type, COUNT(*) AS count
        FROM {DB}.RISK.RISK_SIGNALS
        GROUP BY signal_type ORDER BY count DESC
    """)


@st.cache_data(ttl=300)
def get_signals_by_severity() -> pd.DataFrame:
    return run_query(f"""
        SELECT severity, COUNT(*) AS count
        FROM {DB}.RISK.RISK_SIGNALS
        GROUP BY severity ORDER BY count DESC
    """)


@st.cache_data(ttl=300)
def get_risk_summary() -> pd.DataFrame:
    return run_query(f"""
        SELECT customer_id, full_name, country, kyc_risk_rating,
               total_risk_score, signal_count, high_severity_count,
               latest_signal_at, signal_types
        FROM {DB}.RISK.CUSTOMER_RISK_SUMMARY
        ORDER BY total_risk_score DESC
    """)


def get_customer_detail(cid: str) -> pd.DataFrame:
    return run_query(f"""
        SELECT * FROM {DB}.CORE.CUSTOMERS WHERE customer_id = '{cid}'
    """)


def get_customer_accounts(cid: str) -> pd.DataFrame:
    return run_query(f"""
        SELECT * FROM {DB}.CORE.ACCOUNTS WHERE customer_id = '{cid}'
    """)


def get_customer_signals(cid: str) -> pd.DataFrame:
    return run_query(f"""
        SELECT signal_id, signal_type, severity, risk_points,
               transaction_id, detected_at, evidence_description
        FROM {DB}.RISK.RISK_SIGNALS
        WHERE customer_id = '{cid}'
        ORDER BY risk_points DESC
    """)


def get_customer_transactions(cid: str) -> pd.DataFrame:
    return run_query(f"""
        SELECT t.transaction_id, t.source_account_id, t.destination_account_id,
               t.amount, t.currency, t.transaction_type,
               t.transaction_timestamp, t.source_country, t.destination_country
        FROM {DB}.CORE.TRANSACTIONS t
        JOIN {DB}.CORE.ACCOUNTS a ON a.account_id IN (t.source_account_id, t.destination_account_id)
        WHERE a.customer_id = '{cid}'
        ORDER BY t.transaction_timestamp DESC
    """)


def get_flagged_txn_ids(cid: str) -> set:
    df = run_query(f"""
        SELECT transaction_id FROM {DB}.RISK.RISK_SIGNALS
        WHERE customer_id = '{cid}' AND transaction_id IS NOT NULL
    """)
    return set(df["TRANSACTION_ID"].tolist()) if not df.empty else set()


def build_network_dot(cid: str) -> str:
    accounts = get_customer_accounts(cid)
    if accounts.empty:
        return ""
    acct_ids = accounts["ACCOUNT_ID"].tolist()
    acct_list = ",".join(f"'{a}'" for a in acct_ids)

    hop1 = run_query(f"""
        SELECT DISTINCT source_account_id, destination_account_id, amount
        FROM {DB}.CORE.TRANSACTIONS
        WHERE source_account_id IN ({acct_list})
           OR destination_account_id IN ({acct_list})
    """)
    if hop1.empty:
        return ""

    all_accts = set(hop1["SOURCE_ACCOUNT_ID"].tolist() + hop1["DESTINATION_ACCOUNT_ID"].tolist())
    external_accts = all_accts - set(acct_ids)
    ext_list = ",".join(f"'{a}'" for a in external_accts)

    hop2 = pd.DataFrame()
    if ext_list:
        hop2 = run_query(f"""
            SELECT DISTINCT source_account_id, destination_account_id, amount
            FROM {DB}.CORE.TRANSACTIONS
            WHERE source_account_id IN ({ext_list})
        """)

    all_edges = pd.concat([hop1, hop2], ignore_index=True) if not hop2.empty else hop1

    flagged = get_flagged_txn_ids(cid)
    flagged_edges = set()
    if flagged:
        flist = ",".join(f"'{t}'" for t in flagged)
        flagged_df = run_query(f"""
            SELECT source_account_id, destination_account_id
            FROM {DB}.CORE.TRANSACTIONS
            WHERE transaction_id IN ({flist})
        """)
        for _, r in flagged_df.iterrows():
            flagged_edges.add((r["SOURCE_ACCOUNT_ID"], r["DESTINATION_ACCOUNT_ID"]))

    dot = ['digraph G {', '  rankdir=LR;', '  bgcolor="transparent";',
           '  node [shape=box, style="filled,rounded", fontname="Helvetica", fontsize=10];',
           '  edge [fontname="Helvetica", fontsize=8];']

    for a in set(acct_ids):
        dot.append(f'  "{a}" [fillcolor="#1B6B93", fontcolor="white"];')
    for a in external_accts:
        dot.append(f'  "{a}" [fillcolor="#F0F4F8", fontcolor="#0F2B46"];')

    seen = set()
    for _, row in all_edges.iterrows():
        src, dst = row["SOURCE_ACCOUNT_ID"], row["DESTINATION_ACCOUNT_ID"]
        key = (src, dst)
        if key in seen:
            continue
        seen.add(key)
        amt = f"${row['AMOUNT']:,.0f}" if pd.notna(row["AMOUNT"]) else ""
        color = "#D32F2F" if key in flagged_edges else "#90A4AE"
        penwidth = "2.5" if key in flagged_edges else "1.0"
        dot.append(f'  "{src}" -> "{dst}" [label="{amt}", color="{color}", penwidth={penwidth}];')

    dot.append("}")
    return "\n".join(dot)


def escape_dollars(text: str) -> str:
    """Escape bare $ signs so Streamlit markdown does not trigger LaTeX."""
    return re.sub(r'(?<!\\)\$', r'\\$', str(text))


SIGNAL_POLICY_MAP = {
    "AMOUNT_CLUSTERING": "clustered similar-value transfers short period structuring",
    "TRANSACTION_VELOCITY": "sudden increase transaction frequency abnormal velocity",
    "BENEFICIARY_CONVERGENCE": "intermediary accounts converge same beneficiary layering",
    "GEOGRAPHIC_ANOMALY": "geographic deviation unusual international activity",
    "RAPID_FUND_MOVEMENT": "rapid multi-hop fund movement layering pass-through",
}


SEVERITY_COLORS = {
    "HIGH": "#D32F2F",
    "MEDIUM": "#F57C00",
    "LOW": "#388E3C",
}

SOURCE_BADGES = {
    "fact": ("OBSERVED FACT", "#1B6B93"),
    "signal": ("AUTOMATED RISK SIGNAL", "#F57C00"),
    "ai": ("AI-GENERATED EXPLANATION", "#7B1FA2"),
    "policy": ("POLICY EVIDENCE", "#388E3C"),
    "decision": ("ANALYST DECISION", "#0F2B46"),
}


def badge_html(badge_type: str) -> str:
    label, color = SOURCE_BADGES.get(badge_type, ("UNKNOWN", "#999"))
    return (
        f'<span style="background:{color};color:white;padding:2px 8px;'
        f'border-radius:3px;font-size:0.7rem;font-weight:600;'
        f'letter-spacing:0.5px;">{label}</span>'
    )
