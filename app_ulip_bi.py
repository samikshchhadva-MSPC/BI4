

from __future__ import annotations
# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="ULIP Benefit Illustration – MVP", layout="wide")
st.title("ULIP Benefit Illustration – MVP (Wealth Ultima)")


with st.sidebar:
st.header("Inputs")
entry_age = st.number_input("Entry age (years)", min_value=0, max_value=75, value=35)
gender = st.selectbox("Gender", ["male", "female"], index=0)
ap = st.number_input("Annual Premium (INR)", min_value=12000, step=1000, value=100000)
term = st.number_input("Policy Term (years)", min_value=10, max_value=40, value=20)
ppt = st.number_input("Premium Paying Term (years)", min_value=5, max_value=40, value=10)


# SA multiple minimums
min_mult = PRODUCT.min_sa_multiple_upto49 if entry_age <= 49 else PRODUCT.min_sa_multiple_50plus
sa_mult = st.number_input(f"Sum Assured Multiple (>= {min_mult}× AP)", min_value=float(min_mult), value=float(min_mult))


mode = st.selectbox("Premium Mode", ["annual", "monthly"], index=0)


st.markdown("---")
st.subheader("Return scenarios (gross)")
r4 = st.number_input("Scenario A: Gross p.a. (default 4%)", min_value=0.0, max_value=0.20, value=0.04, step=0.005, format="%0.3f")
r8 = st.number_input("Scenario B: Gross p.a. (default 8%)", min_value=0.0, max_value=0.25, value=0.08, step=0.005, format="%0.3f")


run_btn = st.button("Run Illustration")


if run_btn:
inp = Inputs(entry_age=entry_age, gender=gender, annual_premium=ap, policy_term_years=term, ppt_years=ppt, sa_multiple=sa_mult, mode=mode)
df4 = run_projection(inp, r4)
df8 = run_projection(inp, r8)


# Combine for display
bi = df4[["PolicyYear", "PremiumIn", "FundValue", "DeathBenefit"]].copy()
bi.rename(columns={"FundValue": "Fund@4%", "DeathBenefit": "Death@4%"}, inplace=True)
bi["Fund@8%"] = df8["FundValue"].values
bi["Death@8%"] = df8["DeathBenefit"].values


# Maturity RIY approximation
total_prem = min(ppt, term) * ap
riy4 = 0.08 - compute_riy(bi.loc[bi.index[-1], "Fund@4%"], total_prem, term)
riy8 = 0.08 - compute_riy(bi.loc[bi.index[-1], "Fund@8%"], total_prem, term)


st.subheader("Benefit Illustration (Simplified)")
st.caption("Figures in INR. Charges and taxes approximated for demo. Compare with official BI.")
st.dataframe(bi.style.format({
"PremiumIn": "{:,.0f}",
"Fund@4%": "{:,.0f}",
"Death@4%": "{:,.0f}",
"Fund@8%": "{:,.0f}",
"Death@8%": "{:,.0f}",
}))


st.markdown("### Reduction in Yield (rough)")
col1, col2 = st.columns(2)
col1.metric("Approx. RIY @ 4% scenario", f"{max(0.0, riy4)*100:.2f}%")
col2.metric("Approx. RIY @ 8% scenario", f"{max(0.0, riy8)*100:.2f}%")


# Download CSV
csv = bi.to_csv(index=False).encode("utf-8")
st.download_button("Download BI (CSV)", data=csv, file_name="wealh_ultima_bi_mvp.csv", mime="text/csv")


else:
st.info("Set inputs on the left and click **Run Illustration**.")


st.markdown("---")
st.markdown(
"**Next steps you can add**: STP/SMP/SWP logic, loyalty/booster additions, top-ups, partial withdrawals, multiple funds with distinct FMCs, proper RIY per IRDAI Annexure for Linked products, and the official BI table layout..")

