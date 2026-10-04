import streamlit as st
import json
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import (get_customer_detail, get_customer_signals, get_customer_transactions,
                   get_flagged_txn_ids, search_policy, call_agent, extract_agent_text,
                   badge_html, SIGNAL_POLICY_MAP, get_risk_summary, get_session,
                   escape_dollars, save_analyst_decision)

st.markdown(
    '<p style="color:#546E7A;font-size:0.9rem;margin-bottom:-8px;">SentinelAI</p>'
    '<h1 style="margin-top:0;">Compliance Finding</h1>',
    unsafe_allow_html=True,
)

df_summary = get_risk_summary()
cust_options = df_summary["CUSTOMER_ID"].tolist() if not df_summary.empty else ["CUST-1042"]
idx = cust_options.index(st.session_state.get("selected_customer", "CUST-1042")) \
    if st.session_state.get("selected_customer") in cust_options else 0
cid = st.selectbox("Select customer", cust_options, index=idx, key="cf_cust")
st.session_state.selected_customer = cid

if st.button("Generate Draft Finding", type="primary"):
    cust = get_customer_detail(cid)
    if cust.empty:
        st.warning(
            f"Customer `{cid}` was not found. No evidence is available to "
            "generate a compliance finding."
        )
        st.session_state.pop("draft_finding", None)
        st.stop()

    signals = get_customer_signals(cid)
    transactions = get_customer_transactions(cid)
    flagged_ids = get_flagged_txn_ids(cid)
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    case_id = f"CASE-{cid}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

    total_score = int(signals["RISK_POINTS"].sum()) if not signals.empty else 0

    if signals.empty:
        st.info(
            f"No risk signals detected for `{cid}`. A compliance finding "
            "cannot be generated without supporting evidence."
        )
        st.session_state.pop("draft_finding", None)
        st.stop()

    policy_refs = []
    for stype in signals["SIGNAL_TYPE"].unique() if not signals.empty else []:
        query_text = SIGNAL_POLICY_MAP.get(stype, stype)
        pols = search_policy(query_text, limit=1)
        if pols:
            policy_refs.append(pols[0])

    with st.spinner("Generating AI investigation summary..."):
        try:
            agent_resp = call_agent(
                f"Investigate {cid}. Structure your response with these sections: "
                "Investigation Summary, Detected Risk Signals, Transaction Evidence, "
                "Relevant Policy, Recommended Analyst Action."
            )
            ai_summary = extract_agent_text(agent_resp)
        except Exception as e:
            st.error(f"AI summary could not be generated: {e}")
            ai_summary = ""

    finding = {
        "case_id": case_id,
        "customer_id": cid,
        "customer_name": cust.iloc[0]["FULL_NAME"] if not cust.empty else "Unknown",
        "risk_score": total_score,
        "signal_count": len(signals) if not signals.empty else 0,
        "generated_at": now,
        "ai_summary": ai_summary,
        "signals": signals.to_dict("records") if not signals.empty else [],
        "policy_refs": policy_refs,
        "flagged_transactions": [
            t for t in transactions.to_dict("records")
            if t.get("TRANSACTION_ID") in flagged_ids
        ] if not transactions.empty else [],
    }
    st.session_state.draft_finding = finding
    st.session_state.pop("decision_saved_for", None)

if "draft_finding" in st.session_state:
    f = st.session_state.draft_finding

    st.markdown(
        '<div style="background:#FFF3E0;border:2px solid #FF9800;border-radius:6px;'
        'padding:12px 16px;margin-bottom:16px;text-align:center;">'
        '<strong style="color:#E65100;font-size:1.1rem;">'
        'DRAFT -- REQUIRES HUMAN REVIEW</strong></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    col1.markdown(f"**Case ID:** `{f['case_id']}`")
    col2.markdown(f"**Customer:** `{f['customer_id']}` ({f['customer_name']})")
    col3.markdown(f"**Risk Score:** {f['risk_score']} ({f['signal_count']} signals)")

    st.markdown(f"**Generated:** {f['generated_at']}")

    st.markdown("---")
    st.markdown(f'{badge_html("ai")} **AI Investigation Report**', unsafe_allow_html=True)
    if f['ai_summary'].strip():
        st.markdown(escape_dollars(f['ai_summary']))
    else:
        st.warning("The AI investigation summary could not be generated. "
                   "The grounded evidence sections below remain available for review.")

    st.markdown("---")
    st.markdown(f'{badge_html("signal")} **Observed Risk Indicators**', unsafe_allow_html=True)
    if f["signals"]:
        st.caption("Risk signals are automated indicators requiring analyst review, "
                   "not confirmed findings of fraud or financial crime.")
        for sig in f["signals"]:
            st.markdown(
                f"- **{sig['SIGNAL_TYPE']}** ({sig['SEVERITY']}, {sig['RISK_POINTS']} pts): "
                f"{escape_dollars(sig['EVIDENCE_DESCRIPTION'])}"
            )
    else:
        st.info("No risk signals found for this customer.")

    st.markdown("---")
    st.markdown(f'{badge_html("fact")} **Supporting Transaction Evidence**', unsafe_allow_html=True)
    if f["flagged_transactions"]:
        for txn in f["flagged_transactions"]:
            st.markdown(
                f"- `{txn['TRANSACTION_ID']}`: \\${txn['AMOUNT']:,.2f} {txn['CURRENCY']} "
                f"from `{txn['SOURCE_ACCOUNT_ID']}` to `{txn['DESTINATION_ACCOUNT_ID']}` "
                f"({txn['SOURCE_COUNTRY']} -> {txn['DESTINATION_COUNTRY']}) "
                f"at {txn['TRANSACTION_TIMESTAMP']}"
            )
    else:
        st.info("No flagged transactions associated with the detected signals.")

    st.markdown("---")
    st.markdown(f'{badge_html("policy")} **Relevant Policy References**', unsafe_allow_html=True)
    if f["policy_refs"]:
        for pol in f["policy_refs"]:
            st.markdown(
                f"- **{pol.get('policy_id', 'N/A')}**: {pol.get('policy_title', 'N/A')}\n"
                f"  > {escape_dollars(pol.get('policy_text', '')[:250])}..."
            )
            st.markdown(f"  **Recommended action:** {escape_dollars(pol.get('recommended_action', 'N/A'))}")
    else:
        st.info("No matching policy references were retrieved for the detected signals.")

    st.markdown("---")
    st.markdown(f'{badge_html("decision")} **Analyst Action**', unsafe_allow_html=True)

    already_submitted = st.session_state.get("decision_saved_for") == f["case_id"]

    if already_submitted:
        st.success(f"Decision for {f['case_id']} has been recorded.")
    else:
        analyst_comment = st.text_area(
            "Analyst comments",
            placeholder="Add your observations, justification, or notes for the audit trail...",
            key="analyst_comment",
        )

        col_a, col_b = st.columns(2)
        if col_a.button("Approve Finding", type="primary", use_container_width=True):
            try:
                session = get_session()
                summary_text = f['ai_summary'][:4000].replace("'", "''")
                session.sql(f"""
                    INSERT INTO SENTINEL_AI_DB.COMPLIANCE.INVESTIGATIONS
                    (case_id, customer_id, status, risk_score, investigation_summary, created_at)
                    VALUES ('{f["case_id"]}', '{f["customer_id"]}', 'APPROVED',
                            {f["risk_score"]}, '{summary_text}', CURRENT_TIMESTAMP())
                """).collect()

                for sig in f["signals"]:
                    finding_id = f"FIND-{f['case_id']}-{sig['SIGNAL_TYPE']}"
                    finding_text = str(sig.get("EVIDENCE_DESCRIPTION", ""))[:2000].replace("'", "''")
                    pol_ref = ""
                    for p in f["policy_refs"]:
                        if SIGNAL_POLICY_MAP.get(sig["SIGNAL_TYPE"], "") in str(p.get("policy_text", "")):
                            pol_ref = p.get("policy_id", "")
                            break
                    session.sql(f"""
                        INSERT INTO SENTINEL_AI_DB.COMPLIANCE.CASE_FINDINGS
                        (finding_id, case_id, finding_type, finding_text, policy_reference,
                         evidence_reference, created_at)
                        VALUES ('{finding_id}', '{f["case_id"]}', '{sig["SIGNAL_TYPE"]}',
                                '{finding_text}', '{pol_ref}',
                                '{sig.get("TRANSACTION_ID", "")}', CURRENT_TIMESTAMP())
                    """).collect()

                save_analyst_decision(f["case_id"], f["customer_id"], "APPROVED", analyst_comment)
                st.session_state.decision_saved_for = f["case_id"]
                st.success(f"Finding {f['case_id']} approved and persisted to COMPLIANCE schema.")
            except Exception as e:
                st.error(f"Error persisting finding: {e}")

        if col_b.button("Request Further Investigation", use_container_width=True):
            try:
                save_analyst_decision(f["case_id"], f["customer_id"], "FURTHER_INVESTIGATION", analyst_comment)
                st.session_state.decision_saved_for = f["case_id"]
                st.info(f"Case {f['case_id']} marked for further investigation. Decision recorded.")
            except Exception as e:
                st.error(f"Error recording decision: {e}")
