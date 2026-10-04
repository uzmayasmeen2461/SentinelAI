import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (get_customer_accounts, get_customer_signals,
                   get_customer_transactions, get_flagged_txn_ids, build_network_dot,
                   search_policy, badge_html, SEVERITY_COLORS, SIGNAL_POLICY_MAP,
                   get_risk_summary, escape_dollars)

st.markdown(
    '<p style="color:#546E7A;font-size:0.9rem;margin-bottom:-8px;">SentinelAI</p>'
    '<h1 style="margin-top:0;">Evidence Workspace</h1>',
    unsafe_allow_html=True,
)

df_summary = get_risk_summary()
cust_options = df_summary["CUSTOMER_ID"].tolist() if not df_summary.empty else ["CUST-1042"]
idx = cust_options.index(st.session_state.get("selected_customer", "CUST-1042")) \
    if st.session_state.get("selected_customer") in cust_options else 0
cid = st.selectbox("Select customer", cust_options, index=idx, key="ew_cust")
st.session_state.selected_customer = cid

signals = get_customer_signals(cid)
accounts = get_customer_accounts(cid)
transactions = get_customer_transactions(cid)
flagged_ids = get_flagged_txn_ids(cid)

# --- A. RISK SCORE ---
st.markdown("---")
st.subheader("A. Risk Score")
st.markdown(f'{badge_html("signal")}', unsafe_allow_html=True)

if not signals.empty:
    total_score = int(signals["RISK_POINTS"].sum())
    sig_count = len(signals)
    high_count = int((signals["SEVERITY"] == "HIGH").sum())

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Risk Score", total_score)
    c2.metric("Signal Count", sig_count)
    c3.metric("HIGH Severity Signals", high_count)
    st.caption("Scores are computed by deterministic detection rules, not by the LLM.")
else:
    st.info("No risk signals detected for this customer.")

# --- B. RISK SCORE BREAKDOWN ---
st.markdown("---")
st.subheader("B. Risk Score Breakdown")

if not signals.empty:
    fig = px.bar(signals, x="RISK_POINTS", y="SIGNAL_TYPE", orientation="h",
                 color="SEVERITY", color_discrete_map=SEVERITY_COLORS,
                 text="RISK_POINTS")
    fig.update_layout(yaxis=dict(autorange="reversed"), height=200,
                      margin=dict(t=10, b=10), xaxis_title="Risk Points",
                      yaxis_title="", legend_title="Severity")
    st.plotly_chart(fig, use_container_width=True)

    for _, sig in signals.iterrows():
        sev_color = SEVERITY_COLORS.get(sig["SEVERITY"], "#999")
        st.markdown(
            f'<div style="background:#F0F4F8;padding:10px 14px;border-radius:4px;'
            f'margin-bottom:8px;border-left:4px solid {sev_color};">'
            f'<strong>{sig["SIGNAL_TYPE"]}</strong> &nbsp; '
            f'<span style="background:{sev_color};color:white;padding:1px 6px;'
            f'border-radius:3px;font-size:0.75rem;">{sig["SEVERITY"]}</span> &nbsp; '
            f'+{int(sig["RISK_POINTS"])} pts<br>'
            f'<span style="color:#546E7A;font-size:0.85rem;">{sig["EVIDENCE_DESCRIPTION"]}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

# --- C. TRANSACTION TIMELINE ---
st.markdown("---")
st.subheader("C. Transaction Timeline")
st.markdown(f'{badge_html("fact")}', unsafe_allow_html=True)

if not transactions.empty:
    txn_display = transactions.copy()
    txn_display["FLAGGED"] = txn_display["TRANSACTION_ID"].isin(flagged_ids)
    txn_display = txn_display.sort_values("TRANSACTION_TIMESTAMP")

    def highlight_flagged(row):
        if row["FLAGGED"]:
            return ["background-color: #FFEBEE"] * len(row)
        return [""] * len(row)

    cols = ["TRANSACTION_ID", "TRANSACTION_TIMESTAMP", "SOURCE_ACCOUNT_ID",
            "DESTINATION_ACCOUNT_ID", "AMOUNT", "CURRENCY",
            "SOURCE_COUNTRY", "DESTINATION_COUNTRY", "FLAGGED"]
    st.dataframe(
        txn_display[cols].style.apply(highlight_flagged, axis=1),
        use_container_width=True, hide_index=True, height=350,
    )
    st.caption("Rows highlighted in red are associated with detected risk signals.")
else:
    st.info("No transactions found for this customer.")

# --- D. TRANSACTION NETWORK ---
st.markdown("---")
st.subheader("D. Transaction Network")
st.markdown(f'{badge_html("fact")} &nbsp; Generated from transaction data.', unsafe_allow_html=True)

dot = build_network_dot(cid)
if dot:
    st.graphviz_chart(dot)
    st.caption("Blue = customer accounts. Grey = external accounts. Red edges = flagged transactions.")
else:
    st.info("Insufficient transaction data to render a network.")

# --- E. EVIDENCE CHAIN ---
st.markdown("---")
st.subheader("E. Evidence Chain")

if not signals.empty:
    for _, sig in signals.iterrows():
        st.markdown(f"#### Signal: {sig['SIGNAL_TYPE']}")

        st.markdown(f'{badge_html("signal")} **Risk Signal**', unsafe_allow_html=True)
        st.markdown(f"> {escape_dollars(sig['EVIDENCE_DESCRIPTION'])}")

        st.markdown(f'{badge_html("fact")} **Transaction Evidence**', unsafe_allow_html=True)
        if sig["TRANSACTION_ID"] and not transactions.empty:
            txn_row = transactions[transactions["TRANSACTION_ID"] == sig["TRANSACTION_ID"]]
            if not txn_row.empty:
                t = txn_row.iloc[0]
                st.markdown(
                    f"- **Transaction:** `{t['TRANSACTION_ID']}` &mdash; "
                    f"\\${t['AMOUNT']:,.2f} {t['CURRENCY']} &mdash; "
                    f"`{t['SOURCE_ACCOUNT_ID']}` -> `{t['DESTINATION_ACCOUNT_ID']}` &mdash; "
                    f"{t['SOURCE_COUNTRY']} -> {t['DESTINATION_COUNTRY']}"
                )
            else:
                st.markdown(f"- Referenced transaction: `{sig['TRANSACTION_ID']}`")
        else:
            st.caption("No specific transaction linked to this signal.")

        st.markdown(f'{badge_html("policy")} **Policy Evidence**', unsafe_allow_html=True)
        query_text = SIGNAL_POLICY_MAP.get(sig["SIGNAL_TYPE"], sig["SIGNAL_TYPE"])
        policies = search_policy(query_text, limit=1)
        if policies:
            pol = policies[0]
            st.markdown(
                f'- **{pol.get("policy_id", "N/A")}** &mdash; '
                f'{pol.get("policy_title", "N/A")}\n'
                f'  > {escape_dollars(pol.get("policy_text", "")[:300])}...'
            )
        else:
            st.caption("No matching policy retrieved.")

        st.markdown(f'{badge_html("decision")} **Analyst Recommendation**', unsafe_allow_html=True)
        if policies:
            action = policies[0].get("recommended_action", "Review with senior compliance officer.")
            st.markdown(f"> {escape_dollars(action)}")
        st.markdown("---")
else:
    st.info("No risk signals to build evidence chain.")
