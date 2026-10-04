import streamlit as st

st.set_page_config(
    page_title="SentinelAI",
    page_icon="shield",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    [data-testid="stSidebar"] { background-color: #0F2B46; }
    [data-testid="stSidebar"] * { color: #E0E8F0 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label { color: #A0B4C8 !important; }
    div[data-testid="stMetric"] {
        background: #F0F4F8; border-left: 4px solid #1B6B93;
        padding: 12px 16px; border-radius: 4px;
    }
    div[data-testid="stMetric"] label { font-size: 0.8rem; color: #546E7A; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 1.8rem; font-weight: 700; color: #0F2B46;
    }
    .block-container { padding-top: 2rem; }
    h1 { color: #0F2B46; font-weight: 700; }
    h2, h3 { color: #1B6B93; }
    .stDataFrame { border: 1px solid #E0E8F0; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

if "selected_customer" not in st.session_state:
    st.session_state.selected_customer = "CUST-1042"

pg_command_center = st.Page("pages/1_Risk_Command_Center.py",
                            title="Risk Command Center", icon=":material/dashboard:")
pg_investigation = st.Page("pages/2_AI_Investigation.py",
                           title="AI Investigation Copilot", icon=":material/search:")
pg_evidence = st.Page("pages/3_Evidence_Workspace.py",
                       title="Evidence Workspace", icon=":material/description:")
pg_finding = st.Page("pages/4_Compliance_Finding.py",
                      title="Compliance Finding", icon=":material/gavel:")

pg = st.navigation([pg_command_center, pg_investigation, pg_evidence, pg_finding])
pg.run()
