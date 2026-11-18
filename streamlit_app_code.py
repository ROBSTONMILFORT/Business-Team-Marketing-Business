import streamlit as st
import pandas as pd
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Business Build Helper - MKT-4 Simulation",
    page_icon="📊",
    layout="wide"
)

# --- SESSION STATE INITIALIZATION ---
if 'team_name' not in st.session_state:
    st.session_state.team_name = "Business Team"
if 'challenge_level' not in st.session_state:
    st.session_state.challenge_level = "Advanced"
if 'simulation_version' not in st.session_state:
    st.session_state.simulation_version = 1
if 'starting_cash' not in st.session_state:
    st.session_state.starting_cash = 4000.0
if 'decision_history' not in st.session_state:
    st.session_state.decision_history = []

# --- HEADER BAR ---
st.title("🚀 Business Build Helper: MKT-4 Dashboard")
st.markdown("Career Venture Lab • Local-Business Marketing Agency Simulation (AP Statistics)")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("Simulation Settings")
st.session_state.team_name = st.sidebar.text_input("Team Name", value=st.session_state.team_name)
st.session_state.challenge_level = st.sidebar.selectbox("Math Challenge Level", ["Foundation", "Applied", "Advanced"], index=2)

st.sidebar.subheader("MKT-4 Operational Parameters")
price = st.sidebar.slider("Campaign Package Price ($)", 100, 500, 250, 10)
requested_demand = st.sidebar.slider("Requested Demand (D₀)", 1, 30, 12, 1)
staff_hours = st.sidebar.slider("Monthly Productive Staff Hours", 40, 160, 80, 5)
hours_per_unit = st.sidebar.slider("Hours per Package", 4, 16, 8, 1)
revision_hours = st.sidebar.slider("Client Revision Hours / Unit", 0, 6, 0, 1)
ad_campaign_cost = st.sidebar.number_input("Ad Campaign / Media Spend ($)", value=0.0, step=50.0)

# --- DETERMINISTIC FINANCIAL & OPERATIONAL ENGINE ---
effective_hours_per_unit = hours_per_unit + revision_hours
capacity = int(np.floor(staff_hours / effective_hours_per_unit)) if effective_hours_per_unit > 0 else 0
completed_sales = min(requested_demand, capacity)
unserved_demand = max(0, requested_demand - completed_sales)

base_variable_per_unit = 80.0  # COGS baseline from handbook
variable_cost_per_unit = base_variable_per_unit + (revision_hours * 5.0)
total_variable_costs = completed_sales * variable_cost_per_unit

fixed_costs = 900.0  # Monthly overhead (Software, space, admin, host)
total_expenses = total_variable_costs + fixed_costs + ad_campaign_cost

gross_revenue = price * completed_sales
operating_profit = gross_revenue - total_expenses
closing_cash = st.session_state.starting_cash + operating_profit

unit_contribution = price - variable_cost_per_unit
breakEvenUnits = int(np.ceil((fixed_costs + ad_campaign_cost) / unit_contribution)) if unit_contribution > 0 else float('inf')
is_break_even_feasible = breakEvenUnits <= capacity

# --- TABS LAYOUT ---
tab1, tab2, tab3, tab4 = st.tabs(["Executive Dashboard", "Model Controls", "AP Statistics Experiment", "AI Handoff JSON"])

with tab1:
    st.subheader(f"Performance Overview — Team: {st.session_state.team_name} (v{st.session_state.simulation_version})")
    
    # KPI Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Completed Sales", f"{completed_sales} / {capacity}", delta=f"{unserved_demand} unmet")
    col2.metric("Gross Revenue", f"${gross_revenue:,.2f}")
    col3.metric("Operating Profit", f"${operating_profit:,.2f}", delta_color="normal")
    col4.metric("Closing Cash", f"${closing_cash:,.2f}")
    col5.metric("Break-Even", f"{breakEvenUnits} pkgs" if breakEvenUnits != float('inf') else "N/A")

    st.markdown("---")
    
    # Financial Breakdown Table
    st.markdown("### Monthly Financial & Operating Ledger")
    ledger_data = {
        "Line Item": ["Gross Sales Revenue", "Total Variable Costs (COGS)", "Fixed Monthly Overhead", "Ad Spend", "Net Operating Profit"],
        "Formula / Notes": [
            f"{completed_sales} pkgs × ${price}",
            f"{completed_sales} pkgs × ${variableCostPerUnit}",
            "Standard overhead ($900)",
            "Direct campaign expenses",
            "Revenue - Total Expenses"
        ],
        "Amount ($)": [
            f"${gross_revenue:,.2f}",
            f"${total_variable_costs:,.2f}",
            f"${fixed_costs:,.2f}",
            f"${ad_campaign_cost:,.2f}",
            f"${operating_profit:,.2f}"
        ]
    }
    st.table(pd.DataFrame(ledger_data))

with tab2:
    st.subheader("Model Parameters & Scenario Settings")
    st.info(f"Current Capacity Formula: `floor({staff_hours} hrs / {effective_hours_per_unit} hrs/pkg) = {capacity} packages`")
    
    colA, colB = st.columns(2)
    with colA:
        st.write("#### Capital Management")
        new_start_cash = st.number_input("Opening Cash Reserve ($)", value=float(st.session_state.starting_cash), step=100.0)
        if new_start_cash != st.session_state.starting_cash:
            st.session_state.starting_cash = new_start_cash
            st.rerun()
            
    with colB:
        st.write("#### Operational Status")
        st.write(f"**Break-Even Feasible:** {is_break_even_feasible}")
        st.write(f"**Unserved Demand Lost:** {unserved_demand} potential clients")

with tab3:
    st.subheader("AP Statistics: Two-Proportion Z-Test Experiment")
    st.write("Synthetic randomized trial comparing conversion success rates between Message A and Message B (N=80 prospects).")
    
    # Generate synthetic experiment data
    rng = np.random.default_rng(2027)
    group = np.array(['A']*40 + ['B']*40)
    success = np.r_[rng.permutation([1]*12 + [0]*28), rng.permutation([1]*20 + [0]*20)]
    exp_df = pd.DataFrame({'prospect_id': [f'P{i:03}' for i in range(1, 81)], 'message': group, 'converted': success})
    
    summary_stats = exp_df.groupby('message')['converted'].agg(['count', 'sum', 'mean']).reset_index()
    summary_stats.columns = ['Message Group', 'Total Trials', 'Successes', 'Proportion Success']
    st.dataframe(summary_stats, use_container_width=True)
    
    st.markdown("""
    **Advanced Statistical Findings:**
    * **Message A Proportion ($p_A$):** 30.0% ($12/40$)
    * **Message B Proportion ($p_B$):** 50.0% ($20/40$)
    * **Difference ($p_B - p_A$):** $+20.0\%$ effect size
    """)

with tab4:
    st.subheader("AI Departmental Specialists Handoff (JSON)")
    st.write("Copy this snapshot payload directly into your Finance, Operations, Market, or Reviewer AI assistants.")
    
    snapshot_payload = {
        "team_id": st.session_state.team_name,
        "course": "AP Statistics",
        "pathway_id": "MKT-4",
        "state_version": st.session_state.simulation_version,
        "level": st.session_state.challenge_level,
        "inputs": {
            "price": price,
            "requested_demand": requested_demand,
            "staff_hours": staff_hours,
            "hours_per_unit": hours_per_unit,
            "revision_hours": revision_hours,
            "fixed_costs": fixed_costs,
            "variable_cost_per_unit": variableCostPerUnit
        },
        "outputs": {
            "capacity": capacity,
            "completed_sales": completed_sales,
            "gross_revenue": gross_revenue,
            "operating_profit": operating_profit,
            "closing_cash": closing_cash,
            "break_even_units": breakEvenUnits
        }
    }
    
    st.json(snapshot_payload)