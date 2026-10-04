import streamlit as st
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils import get_kpis, get_signals_by_type, get_signals_by_severity, get_risk_summary

st.markdown(
    '<p style="color:#546E7A;font-size:0.9rem;margin-bottom:-8px;">SentinelAI</p>'
    '<h1 style="margin-top:0;">Risk Command Center</h1>'
    '<p style="color:#78909C;margin-top:-10px;">'
    'From risk signal to evidence-backed regulatory finding.</p>',
    unsafe_allow_html=True,
)

kpis = get_kpis()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Customers", f"{int(kpis['TOTAL_CUSTOMERS']):,}")
c2.metric("Transactions Monitored", f"{int(kpis['TOTAL_TRANSACTIONS']):,}")
c3.metric("Active Risk Signals", int(kpis["ACTIVE_SIGNALS"]))
c4.metric("High-Risk Customers", int(kpis["HIGH_RISK_CUSTOMERS"]))

st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Risk Signals by Type")
    df_type = get_signals_by_type()
    if not df_type.empty:
        fig = px.bar(df_type, x="SIGNAL_TYPE", y="COUNT", color="SIGNAL_TYPE",
                     color_discrete_sequence=["#1B6B93", "#2196F3", "#4CAF50", "#FF9800", "#D32F2F"],
                     text_auto=True)
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count",
                          margin=dict(t=10, b=10), height=300)
        fig.update_xaxes(tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No risk signals detected.")

with col_right:
    st.subheader("Risk Signals by Severity")
    df_sev = get_signals_by_severity()
    if not df_sev.empty:
        color_map = {"HIGH": "#D32F2F", "MEDIUM": "#FF9800", "LOW": "#4CAF50"}
        fig2 = px.bar(df_sev, x="SEVERITY", y="COUNT", color="SEVERITY",
                      color_discrete_map=color_map, text_auto=True)
        fig2.update_layout(showlegend=False, xaxis_title="", yaxis_title="Count",
                           margin=dict(t=10, b=10), height=300)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No risk signals detected.")

st.markdown("---")
st.subheader("Highest-Risk Customers")
df_summary = get_risk_summary()
if not df_summary.empty:
    fig3 = px.bar(df_summary.head(5), x="TOTAL_RISK_SCORE", y="CUSTOMER_ID",
                  orientation="h", color="TOTAL_RISK_SCORE",
                  color_continuous_scale=["#4CAF50", "#FF9800", "#D32F2F"],
                  text="TOTAL_RISK_SCORE")
    fig3.update_layout(yaxis=dict(autorange="reversed"), showlegend=False,
                       coloraxis_showscale=False, margin=dict(t=10, b=10), height=250,
                       xaxis_title="Total Risk Score", yaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("No customers with risk signals found.")

st.markdown("---")
st.subheader("Customers Requiring Review")
if not df_summary.empty:
    display_cols = ["CUSTOMER_ID", "FULL_NAME", "TOTAL_RISK_SCORE",
                    "SIGNAL_COUNT", "HIGH_SEVERITY_COUNT", "SIGNAL_TYPES",
                    "LATEST_SIGNAL_AT"]
    st.dataframe(df_summary[display_cols], use_container_width=True, hide_index=True)

    cust_options = df_summary["CUSTOMER_ID"].tolist()
    selected = st.selectbox("Select a customer to investigate", cust_options,
                            index=cust_options.index(st.session_state.selected_customer)
                            if st.session_state.selected_customer in cust_options else 0)
    st.session_state.selected_customer = selected

    col_a, col_b = st.columns(2)
    if col_a.button("Open Investigation Copilot", type="primary", use_container_width=True):
        st.switch_page("pages/2_AI_Investigation.py")
    if col_b.button("Open Evidence Workspace", use_container_width=True):
        st.switch_page("pages/3_Evidence_Workspace.py")
else:
    st.info("No customers require review at this time.")
