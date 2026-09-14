import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import json
import datetime
import plotly.graph_objects as go
import streamlit.components.v1 as components

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Avishkar Edge | Waste-to-Credit Ledger Simulator",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .receipt-box {
        background-color: #F8FAFC;
        border: 2px dashed #94A3B8;
        padding: 1.2rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', Courier, monospace;
        animation: fadeIn 0.6s ease-in;
    }
    .receipt-box p {
        opacity: 0;
        animation: lineIn 0.4s ease-in forwards;
    }
    .receipt-box p:nth-of-type(1) { animation-delay: 0.1s; }
    .receipt-box p:nth-of-type(2) { animation-delay: 0.2s; }
    .receipt-box p:nth-of-type(3) { animation-delay: 0.3s; }
    .receipt-box p:nth-of-type(4) { animation-delay: 0.4s; }
    .receipt-box p:nth-of-type(5) { animation-delay: 0.5s; }
    .receipt-box p:nth-of-type(6) { animation-delay: 0.6s; }
    .receipt-box p:nth-of-type(7) { animation-delay: 0.7s; }
    @keyframes fadeIn { from {opacity:0;} to {opacity:1;} }
    @keyframes lineIn { from {opacity:0; transform:translateX(-6px);} to {opacity:1; transform:translateX(0);} }
    .demo-tag {
        display: inline-block;
        background-color: #FEF3C7;
        color: #92400E;
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.15rem 0.5rem;
        border-radius: 0.3rem;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #16A34A;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# HEADER
# ------------------------------------------------------------------------------
st.markdown("<div class='main-title'>♻️ Avishkar Edge: Micro-Decentralized Waste-to-Credit Ledger</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Informal Sanitation Workers via NPCI UPI 2.0 / e-RUPI Micro-Escrow Automation</div>", unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/isometric/100/recycle.png", width=70)
st.sidebar.title("Navigation & Controls")
nav_option = st.sidebar.radio(
    "Select Module",
    [
        "1. Live Scrap Deposit Simulator",
        "2. 30-Day Income Simulation",
        "3. Supply Chain Costing (ABC Model)",
        "4. Corporate ESG Ledger Audit"
    ]
)

BASE_PRICE_PER_KG = 12.00
PWP_CERTIFICATE_POOL = 3500.00
LEDGER_FEE_PCT = 0.015

POLYMER_CATEGORIES = {
    "Category I: Rigid Packaging (PET / HDPE)": {
        "cat_code": "CAT_1", "gamma_cat": 1.00,
        "trading_range": "₹1,500 - ₹2,800 / MT",
        "description": "PET bottles, HDPE containers, rigid food boxes"
    },
    "Category II: Flexible Packaging (LDPE / PP)": {
        "cat_code": "CAT_2", "gamma_cat": 1.25,
        "trading_range": "₹3,200 - ₹4,800 / MT",
        "description": "Single/multilayer plastic sheets, grocery bags, liners"
    },
    "Category III: Multi-Layered Plastic (MLP / Sachets)": {
        "cat_code": "CAT_3", "gamma_cat": 1.60,
        "trading_range": "₹4,500 - ₹6,500 / MT",
        "description": "Metallized snack sachets, food wrappers (high scarcity)"
    },
    "Category IV: Compostable & Biodegradable": {
        "cat_code": "CAT_4", "gamma_cat": 1.10,
        "trading_range": "₹2,000 - ₹3,500 / MT",
        "description": "Bio-based polymer sheets and institutional carry bags"
    }
}

if "logged_deposits" not in st.session_state:
    st.session_state.logged_deposits = []


def animated_counter(label, value, prefix="₹", decimals=2, color="#16A34A", height=100):
    """Renders a number that counts up from 0 to `value` using JS — a real animation, not a Streamlit rerun hack."""
    html = f"""
    <div style="font-family: 'Source Sans Pro', sans-serif; text-align:center; padding:6px;">
      <div style="font-size:13px; color:#6B7280; margin-bottom:2px;">{label}</div>
      <div id="counter-{label.replace(' ', '')}" style="font-size:2rem; font-weight:800; color:{color};">{prefix}0.00</div>
    </div>
    <script>
    (function() {{
        let target = {value};
        let current = 0;
        let steps = 45;
        let increment = target / steps;
        let el = document.getElementById("counter-{label.replace(' ', '')}");
        let i = 0;
        let timer = setInterval(function() {{
            i++;
            current += increment;
            if (i >= steps) {{ current = target; clearInterval(timer); }}
            el.innerText = "{prefix}" + current.toLocaleString(undefined, {{minimumFractionDigits: {decimals}, maximumFractionDigits: {decimals}}});
        }}, 20);
    }})();
    </script>
    """
    components.html(html, height=height)


# ------------------------------------------------------------------------------
# MODULE 1: LIVE SCRAP DEPOSIT SIMULATOR
# ------------------------------------------------------------------------------
if nav_option == "1. Live Scrap Deposit Simulator":
    st.subheader("Tier A & C: IoT Edge Ingestion & Micro-Escrow Execution")
    st.write("Simulate an automated deposit at a Tier-1 micro-dealer (*kabadiwala*) center equipped with IoT scales and optical sensors.")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📥 1. Worker & Scrap Deposit Inputs")
        worker_id = st.text_input("Waste Picker ID (NFC Card / Aadhaar Jan Dhan)", value="WP_JAN_DHAN_9842")
        dealer_id = st.selectbox("Micro-Dealer Center (Kabadiwala)", ["KABADIWALA_DHARAVI_04", "KABADIWALA_DEONAR_12", "KABADIWALA_KURLA_08"])

        selected_cat_label = st.selectbox("Optical Sensor Classification (Polymer Type)", list(POLYMER_CATEGORIES.keys()), index=1)
        cat_info = POLYMER_CATEGORIES[selected_cat_label]

        st.info(f"**Category Multiplier (γ_cat):** {cat_info['gamma_cat']}x | **Market EPR Band:** {cat_info['trading_range']}")

        gross_weight = st.slider("IoT Scale Measured Weight (kg)", min_value=5.0, max_value=100.0, value=35.0, step=0.5)
        moisture_pct = st.slider("Moisture Sensor Tare Discount (%)", min_value=0.0, max_value=20.0, value=0.0, step=1.0)

        moisture_tare = moisture_pct / 100.0
        net_weight = gross_weight * (1.0 - moisture_tare)

    with col2:
        st.markdown("### ⚙️ 2. Smart Contract Payout Calculation (Eq. 4)")

        p_base = net_weight * BASE_PRICE_PER_KG
        weighted_kg = net_weight * cat_info['gamma_cat']
        epr_bonus = (weighted_kg / 35.0) * 191.60 * (1.0 - LEDGER_FEE_PCT)
        total_payout = p_base + epr_bonus

        status_quo_weight = gross_weight * (1.0 - 0.15)
        status_quo_pay = status_quo_weight * BASE_PRICE_PER_KG

        net_gain = total_payout - status_quo_pay
        pct_gain = (net_gain / status_quo_pay) * 100.0

        st.markdown("#### Payout Metrics")
        mcol1, mcol2 = st.columns(2)
        mcol1.metric("Base Cash Pay (P_base)", f"₹{p_base:.2f}")
        mcol2.metric("EPR Credit Bonus", f"₹{epr_bonus:.2f}")

        animated_counter(f"Total Net Payout  (+{pct_gain:.1f}% vs Status Quo)", total_payout, color="#16A34A")

        st.markdown("---")
        st.markdown("### 🧾 3. NPCI e-RUPI Digital Voucher Receipt")

        timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        tx_payload = f"{worker_id}-{dealer_id}-{net_weight}-{total_payout}-{timestamp_str}"
        tx_hash = hashlib.sha256(tx_payload.encode()).hexdigest()
        voucher_id = f"ERUPI_UPI_{tx_hash[:10].upper()}"

        st.markdown(f"""
        <div class="receipt-box">
            <span class="demo-tag">SIMULATED — DEMO ONLY</span>
            <h4>NATIONAL PAYMENTS CORPORATION OF INDIA (NPCI)</h4>
            <p><strong>e-RUPI PROGRAMMABLE MICRO-ESCROW REMITTANCE</strong></p>
            <hr>
            <p><strong>Voucher ID:</strong> {voucher_id}</p>
            <p><strong>Beneficiary Account:</strong> {worker_id}</p>
            <p><strong>Deposit Node:</strong> {dealer_id}</p>
            <p><strong>Material:</strong> {cat_info['cat_code']} ({net_weight:.1f} kg net)</p>
            <hr>
            <p>Base Scrap Payment    : ₹{p_base:.2f}</p>
            <p>EPR Credit Bonus      : ₹{epr_bonus:.2f}</p>
            <p><strong>TOTAL SETTLED PAYOUT : ₹{total_payout:.2f}</strong></p>
            <hr>
            <p><strong>Status:</strong> ✅ SETTLED_VIA_UPI_AUTOSPLIT (simulated)</p>
            <p><strong>Simulated Transaction Reference:</strong> {tx_hash[:24]}...</p>
        </div>
        """, unsafe_allow_html=True)
        st.caption("This receipt is a model output for demonstration purposes — it is not a real payment or blockchain transaction.")

        st.markdown("")
        if st.button("📌 Log this Deposit to Today's Ledger"):
            st.session_state.logged_deposits.append({
                "Worker": worker_id,
                "Category": cat_info["cat_code"],
                "Net Weight (kg)": round(net_weight, 2),
                "Total Payout (₹)": round(total_payout, 2),
                "Gain vs Status Quo (%)": round(pct_gain, 1)
            })
            st.success(f"Logged. {len(st.session_state.logged_deposits)} deposit(s) recorded so far — these now feed Module 2's income simulation.")

    if st.session_state.logged_deposits:
        st.markdown("---")
        st.markdown("### 📋 Today's Logged Deposits")
        log_df = pd.DataFrame(st.session_state.logged_deposits)
        st.dataframe(log_df, use_container_width=True)
        if st.button("🗑️ Clear Logged Deposits"):
            st.session_state.logged_deposits = []
            st.rerun()

# ------------------------------------------------------------------------------
# MODULE 2: 30-DAY INCOME SIMULATION  (Plotly animated race chart, play button)
# ------------------------------------------------------------------------------
elif nav_option == "2. 30-Day Income Simulation":
    st.subheader("Section 6: Empirical 30-Day Socioeconomic Impact Simulation")
    st.write("Comparing monthly income trajectories for informal waste pickers in Dharavi/Deonar (Mumbai).")

    baseline_daily = 357.00
    poverty_line_daily = 303.00

    if st.session_state.logged_deposits:
        avg_payout = np.mean([d["Total Payout (₹)"] for d in st.session_state.logged_deposits])
        deposits_per_day = st.slider("Assumed Deposits per Working Day", min_value=1, max_value=6, value=3)
        model_daily = avg_payout * deposits_per_day
        st.info(f"📡 Using **{len(st.session_state.logged_deposits)} logged deposit(s)** from Module 1 — average ₹{avg_payout:.2f}/deposit × {deposits_per_day} deposits/day = **₹{model_daily:.2f}/day**.")
    else:
        model_daily = 611.60
        st.warning("No deposits logged yet in Module 1 — showing the research paper's baseline projection (₹611.60/day). Log a deposit in Module 1 to personalize this simulation.")

    days = np.arange(1, 27)
    baseline_cum = days * baseline_daily
    model_cum = days * model_daily
    poverty_cum = days * poverty_line_daily

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### 🏁 Cumulative Income Growth Race — press Play")

        frames = []
        for i in range(1, len(days) + 1):
            frames.append(go.Frame(
                data=[
                    go.Scatter(x=days[:i], y=poverty_cum[:i], mode="lines", name="Poverty Line",
                                line=dict(color="#DC2626", width=2, dash="dash")),
                    go.Scatter(x=days[:i], y=baseline_cum[:i], mode="lines", name="Baseline Status Quo",
                                line=dict(color="#94A3B8", width=3)),
                    go.Scatter(x=days[:i], y=model_cum[:i], mode="lines+markers", name="Avishkar Edge Model",
                                line=dict(color="#16A34A", width=4),
                                marker=dict(size=6, color="#16A34A")),
                ],
                name=str(i)
            ))

        fig = go.Figure(
            data=[
                go.Scatter(x=[days[0]], y=[poverty_cum[0]], mode="lines", name="Poverty Line",
                            line=dict(color="#DC2626", width=2, dash="dash")),
                go.Scatter(x=[days[0]], y=[baseline_cum[0]], mode="lines", name="Baseline Status Quo",
                            line=dict(color="#94A3B8", width=3)),
                go.Scatter(x=[days[0]], y=[model_cum[0]], mode="lines+markers", name="Avishkar Edge Model",
                            line=dict(color="#16A34A", width=4)),
            ],
            frames=frames
        )

        fig.update_layout(
            xaxis=dict(range=[1, 26], title="Working Day"),
            yaxis=dict(range=[0, max(model_cum.max(), baseline_cum.max()) * 1.15], title="Cumulative Income (₹)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
            height=460,
            margin=dict(l=40, r=20, t=30, b=40),
            updatemenus=[dict(
                type="buttons",
                showactive=False,
                x=0, y=-0.15, xanchor="left", yanchor="top",
                buttons=[
                    dict(label="▶ Play", method="animate",
                         args=[None, {"frame": {"duration": 70, "redraw": True}, "fromcurrent": True, "transition": {"duration": 0}}]),
                    dict(label="⏸ Pause", method="animate",
                         args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
                ]
            )]
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Key Results")
        monthly_baseline = baseline_daily * 26
        monthly_model = model_daily * 26
        gain = monthly_model - monthly_baseline
        pct = (gain / monthly_baseline) * 100.0

        animated_counter("Avishkar Edge Monthly Income (26 days)", monthly_model, color="#16A34A")
        animated_counter("Baseline Monthly Income (26 days)", monthly_baseline, color="#94A3B8")
        st.metric("Net Monthly Gain", f"₹{gain:,.2f}", delta=f"{pct:+.1f}%")

        if monthly_model / 26 > poverty_line_daily:
            st.success("✅ Daily income under this simulation clears the World Bank Urban Poverty Line ($3.65/day PPP).")
        else:
            st.error("⚠️ Daily income under this simulation still falls below the World Bank Urban Poverty Line.")

# ------------------------------------------------------------------------------
# MODULE 3: SUPPLY CHAIN COSTING (ABC MODEL) — Sankey value-flow diagrams
# ------------------------------------------------------------------------------
elif nav_option == "3. Supply Chain Costing (ABC Model)":
    st.subheader("Section 3: Activity-Based Supply Chain Costing & Value Leakage")
    st.write("Tracking 1 Metric Ton (1,000 kg) of post-consumer plastic waste across supply chain nodes in Mumbai.")

    nodes = [
        "Tier 0: Segregation\n(Waste Picker)",
        "Tier 1: Collection\n(Micro-Dealer)",
        "Tier 2: Aggregation\n(Sub-Wholesaler)",
        "Tier 3: Baling/Traders\n(Bulk Aggregator)",
        "Tier 4: Recycling\n(Registered PWP)"
    ]
    price_per_kg = [12.00, 18.00, 26.00, 36.00, 48.00]
    gross_value_mt = [p * 1000 for p in price_per_kg]
    epr_captured_mt = [0.00, 0.00, 0.00, 0.00, PWP_CERTIFICATE_POOL]

    before_share = [7.74, 11.61, 17.03, 23.94, 39.68]
    after_share = [13.26, 10.92, 16.01, 22.51, 37.31]

    abc_data = pd.DataFrame({
        "Supply Chain Node": nodes,
        "Scrap Price Paid (INR/kg)": price_per_kg,
        "Gross Scrap Value / MT": gross_value_mt,
        "EPR Credit Captured / MT": epr_captured_mt,
        "Status Quo Share (%)": before_share,
        "Avishkar Edge Share (%)": after_share
    })
    st.dataframe(abc_data, use_container_width=True)

    st.markdown("### 💸 Where the Money Actually Goes — Value Flow per MT (₹51,500 total)")
    st.caption("Same ₹51,500 of value created per MT, split two ways. Watch how much reaches the waste picker (green) in each scenario.")

    def make_sankey(share_list, title, picker_color):
        total_value = 51500
        values = [round(s / 100 * total_value, 2) for s in share_list]
        labels = ["Total Value\nCreated / MT"] + nodes
        node_colors = ["#1E3A8A", picker_color, "#93C5FD", "#93C5FD", "#93C5FD", "#93C5FD"]
        link_colors = [picker_color.replace("#", "rgba(").rstrip(")") if False else "rgba(22,163,74,0.55)"] + ["rgba(59,130,246,0.35)"] * 4
        fig = go.Figure(data=[go.Sankey(
            node=dict(pad=22, thickness=16, line=dict(color="black", width=0.3),
                      label=labels, color=node_colors),
            link=dict(source=[0, 0, 0, 0, 0], target=[1, 2, 3, 4, 5], value=values, color=link_colors)
        )])
        fig.update_layout(title_text=title, font_size=11, height=360, margin=dict(l=10, r=10, t=40, b=10))
        return fig

    scol1, scol2 = st.columns(2)
    with scol1:
        st.plotly_chart(make_sankey(before_share, "Status Quo — Waste Picker Gets 7.74%", "#DC2626"), use_container_width=True)
    with scol2:
        st.plotly_chart(make_sankey(after_share, "Avishkar Edge — Waste Picker Gets 13.26%", "#16A34A"), use_container_width=True)

    st.warning("⚠️ **Key Finding:** Informal waste pickers perform 94% of physical occupational labor but capture only **7.74%** of the gross ₹51,500 total market value created per MT under the current status quo — rising to **13.26%** under the Avishkar Edge model, a 71% relative income gain.")

# ------------------------------------------------------------------------------
# MODULE 4: CORPORATE ESG LEDGER AUDIT
# ------------------------------------------------------------------------------
elif nav_option == "4. Corporate ESG Ledger Audit":
    st.subheader("Section 4 & 7: Corporate ESG Balance Sheet & Accounting Verification")
    st.write("Generating an audit-ready **Social Origin Ledger Certificate** under SEBI BRSR Core and Ind AS 38.")

    col1, col2 = st.columns(2)

    with col1:
        company_name = st.text_input("PIBO / Corporate Brand Owner Name", value="Hindustan Consumer Goods Ltd.")
        cert_period = st.selectbox("Compliance Quarter", ["Q1 FY 2026-27", "Q2 FY 2026-27", "Q3 FY 2026-27", "Q4 FY 2026-27"])
        tonnage = st.number_input("Verified Recycled Tonnage (MT)", value=250.0, step=10.0)

    with col2:
        st.markdown("### Audit Compliance Status")
        st.markdown("- **Ind AS 38 Intangible Asset:** Verified Fair Provenance")
        st.markdown("- **Ind AS 20 Government Grant:** Zero Labor Externalization")
        st.markdown("- **SEBI BRSR Core Principle 5 (Fair Wages):** 100% Pass-Through Verified")
        st.markdown("- **SEBI BRSR Core Principle 6 (Waste Neutrality):** Cryptographically Proven")

    if st.button("Generate Social Origin Ledger Certificate"):
        cert_payload = f"{company_name}-{cert_period}-{tonnage}"
        cert_hash = hashlib.sha256(cert_payload.encode()).hexdigest()
        remittance = tonnage * 5474.28

        animated_counter("Total Direct Worker Remittance", remittance, color="#1E3A8A")

        st.markdown(f"""
        <div class="receipt-box">
            <span class="demo-tag">SIMULATED — DEMO ONLY</span>
            <h3 style="text-align: center; color: #1E3A8A;">OFFICIAL SOCIAL ORIGIN LEDGER CERTIFICATE</h3>
            <p style="text-align: center;"><em>Issued under MoEFCC Plastic Waste Management Rules & SEBI BRSR Core Assurance</em></p>
            <hr>
            <p><strong>Corporate Entity:</strong> {company_name}</p>
            <p><strong>Compliance Period:</strong> {cert_period}</p>
            <p><strong>Certified Polymer Volume:</strong> {tonnage} Metric Tons (MT)</p>
            <p><strong>Total Direct Worker Remittance:</strong> ₹{remittance:,.2f}</p>
            <p><strong>Simulated Ledger Reference:</strong> {cert_hash[:32]}</p>
            <hr>
            <p><strong>Audit Guarantee:</strong> 100% of frontline informal collectors verified via Aadhaar-seeded Jan Dhan UPI micro-escrow receipts (simulated). Zero unverified scale fraud or predatory intermediary rent extraction detected.</p>
            <p style="text-align: right;"><strong>Central Audit Stamp:</strong> CPCB/PWM/BRSR-ASSURED/2026 (demo)</p>
        </div>
        """, unsafe_allow_html=True)
        st.caption("This certificate is a research-prototype mockup for the Avishkar convention — it is not an issued or legally valid compliance document.")

st.markdown("---")
st.markdown("<div style='text-align: center; color: #6B7280;'>Avishkar Research Convention Monograph Prototype | Banking, Accounting & Finance (BAF) Track</div>", unsafe_allow_html=True)
