import streamlit as st
import pandas as pd
import numpy as np
import hashlib
import json
import datetime

# ------------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Avishkar Edge | Waste-to-Credit Ledger Simulator",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
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
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #2563EB;
    }
    .receipt-box {
        background-color: #F8FAFC;
        border: 2px dashed #94A3B8;
        padding: 1.2rem;
        border-radius: 0.5rem;
        font-family: 'Courier New', Courier, monospace;
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
# HEADER SECTION
# ------------------------------------------------------------------------------
st.markdown("<div class='main-title'>♻️ Avishkar Edge: Micro-Decentralized Waste-to-Credit Ledger</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Empowering Informal Sanitation Workers via NPCI UPI 2.0 / e-RUPI Micro-Escrow Automation</div>", unsafe_allow_html=True)

st.sidebar.image("https://img.icons8.com/isometric/100/recycle.png", width=70)
st.sidebar.title("Navigation & Controls")
nav_option = st.sidebar.radio(
    "Select Module",
    ["1. Live Scrap Deposit Simulator", "2. 30-Day Income Simulation", "3. Supply Chain Costing (ABC Model)", "4. Corporate ESG Ledger Audit"]
)

# Shared Constants from Research Paper
BASE_PRICE_PER_KG = 12.00  # INR/kg Tier 0 baseline nominal price
PWP_CERTIFICATE_POOL = 3500.00  # INR/MT formal EPR credit market price
LEDGER_FEE_PCT = 0.015  # 1.5% protocol maintenance fee (Phi_ledger)

POLYMER_CATEGORIES = {
    "Category I: Rigid Packaging (PET / HDPE)": {
        "cat_code": "CAT_1",
        "gamma_cat": 1.00,
        "trading_range": "₹1,500 - ₹2,800 / MT",
        "description": "PET bottles, HDPE containers, rigid food boxes"
    },
    "Category II: Flexible Packaging (LDPE / PP)": {
        "cat_code": "CAT_2",
        "gamma_cat": 1.25,
        "trading_range": "₹3,200 - ₹4,800 / MT",
        "description": "Single/multilayer plastic sheets, grocery bags, liners"
    },
    "Category III: Multi-Layered Plastic (MLP / Sachets)": {
        "cat_code": "CAT_3",
        "gamma_cat": 1.60,
        "trading_range": "₹4,500 - ₹6,500 / MT",
        "description": "Metallized snack sachets, food wrappers (high scarcity)"
    },
    "Category IV: Compostable & Biodegradable": {
        "cat_code": "CAT_4",
        "gamma_cat": 1.10,
        "trading_range": "₹2,000 - ₹3,500 / MT",
        "description": "Bio-based polymer sheets and institutional carry bags"
    }
}

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
        
        status_quo_weight = gross_weight * (1.0 - 0.15) # 15% scale fraud loss
        status_quo_pay = status_quo_weight * BASE_PRICE_PER_KG
        
        net_gain = total_payout - status_quo_pay
        pct_gain = (net_gain / status_quo_pay) * 100.0
        
        st.markdown("#### Payout Metrics")
        mcol1, mcol2, mcol3 = st.columns(3)
        mcol1.metric("Base Cash Pay (P_base)", f"₹{p_base:.2f}")
        mcol2.metric("EPR Credit Bonus", f"₹{epr_bonus:.2f}")
        mcol3.metric("Total Net Payout", f"₹{total_payout:.2f}", delta=f"+{pct_gain:.1f}% vs Status Quo")

        st.markdown("---")
        st.markdown("### 🧾 3. NPCI e-RUPI Digital Voucher Receipt")
        
        timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()
        tx_payload = f"{worker_id}-{dealer_id}-{net_weight}-{total_payout}-{timestamp_str}"
        tx_hash = hashlib.sha256(tx_payload.encode()).hexdigest()
        voucher_id = f"ERUPI_UPI_{tx_hash[:10].upper()}"
        
        st.markdown(f"""
        <div class="receipt-box">
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
            <p><strong>Status:</strong> ✅ SETTLED_VIA_UPI_AUTOSPLIT</p>
            <p><strong>Ledger Block Hash:</strong> {tx_hash[:24]}...</p>
        </div>
        """, unsafe_allow_html=True)

# ------------------------------------------------------------------------------
# MODULE 2: 30-DAY INCOME SIMULATION
# ------------------------------------------------------------------------------
elif nav_option == "2. 30-Day Income Simulation":
    st.subheader("Section 6: Empirical 30-Day Socioeconomic Impact Simulation")
    st.write("Comparing monthly income trajectories for 500 informal waste pickers in Dharavi/Deonar (Mumbai).")

    days = np.arange(1, 27)
    baseline_daily = 357.00
    model_daily = 611.60
    poverty_line_daily = 303.00

    baseline_cum = days * baseline_daily
    model_cum = days * model_daily
    poverty_cum = days * poverty_line_daily

    df_sim = pd.DataFrame({
        "Working Day": days,
        "Baseline Status Quo (₹357/day)": baseline_cum,
        "Avishkar Edge Model (₹611.60/day)": model_cum,
        "World Bank Urban Poverty Line Benchmark": poverty_cum
    })

    col1, col2 = st.columns(2)

    with col1:
        st.line_chart(df_sim.set_index("Working Day"), height=400)

    with col2:
        st.markdown("### Key Simulation Results")
        st.metric("Baseline Monthly Income (26 Days)", "₹9,282.00")
        st.metric("Avishkar Edge Monthly Income", "₹15,901.60", delta="+₹6,619.60 (+71.32%)")
        st.metric("IoT Scale Fraud Recovery", "+5.25 kg/day", delta="+17.6% Effective Volume")
        st.metric("EPR Pass-Through Bonus", "₹191.60 / day", delta="Direct Escrow Asset")
        
        st.success("✅ Participating waste-picker households are safely elevated above the World Bank Urban Poverty Line ($3.65/day PPP).")

# ------------------------------------------------------------------------------
# MODULE 3: SUPPLY CHAIN COSTING (ABC MODEL)
# ------------------------------------------------------------------------------
elif nav_option == "3. Supply Chain Costing (ABC Model)":
    st.subheader("Section 3: Activity-Based Supply Chain Costing & Value Leakage")
    st.write("Tracking 1 Metric Ton (1,000 kg) of post-consumer plastic waste across supply chain nodes in Mumbai.")

    abc_data = pd.DataFrame({
        "Supply Chain Node": ["Tier 0: Segregation", "Tier 1: Collection", "Tier 2: Aggregation", "Tier 3: Baling/Traders", "Tier 4: Recycling"],
        "Actor Entity": ["Informal Waste Picker", "Micro-Dealer (Chota Kabadiwala)", "Sub-Wholesaler (Bada Kabadiwala)", "Bulk Aggregator / Broker", "Registered PWP & PIBO"],
        "Scrap Price Paid (INR/kg)": [12.00, 18.00, 26.00, 36.00, 48.00],
        "Gross Scrap Value / MT": ,
        "EPR Credit Captured / MT": ,
        "Net Value Capture Share (%)": [7.74, 11.61, 17.03, 23.94, 39.68]
    })

    st.dataframe(abc_data, use_container_width=True)

    st.markdown("### Value Capture Share Breakdown across Tiers")
    st.bar_chart(abc_data.set_index("Supply Chain Node")["Net Value Capture Share (%)"])

    st.warning("⚠️ **Key Finding:** Informal waste pickers perform 94% of physical occupational labor but capture only **7.74%** of the gross ₹51,500 total market value created per MT.")

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
        st.markdown("---")
        st.markdown(f"""
        <div class="receipt-box">
            <h3 style="text-align: center; color: #1E3A8A;">OFFICIAL SOCIAL ORIGIN LEDGER CERTIFICATE</h3>
            <p style="text-align: center;"><em>Issued under MoEFCC Plastic Waste Management Rules & SEBI BRSR Core Assurance</em></p>
            <hr>
            <p><strong>Corporate Entity:</strong> {company_name}</p>
            <p><strong>Compliance Period:</strong> {cert_period}</p>
            <p><strong>Certified Polymer Volume:</strong> {tonnage} Metric Tons (MT)</p>
            <p><strong>Total Direct Worker Remittance:</strong> ₹{(tonnage * 5474.28):,.2f}</p>
            <p><strong>Hyperledger Ledger Root Hash:</strong> 0x9f8b7a6c5d4e3f2a1b0c9d8e7f6a5b4c3d2e1f0a</p>
            <hr>
            <p><strong>Audit Guarantee:</strong> 100% of frontline informal collectors verified via Aadhaar-seeded Jan Dhan UPI micro-escrow receipts. Zero unverified scale fraud or predatory intermediary rent extraction detected.</p>
            <p style="text-align: right;"><strong>Central Audit Stamp:</strong> CPCB/PWM/BRSR-ASSURED/2026</p>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #6B7280;'>Avishkar Research Convention Monograph Prototype | Banking, Accounting & Finance (BAF) Track</div>", unsafe_allow_html=True)
    

       

    
        
        




    
