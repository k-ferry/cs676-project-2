# Feature: After-Tax Return / Tax-Impact Preview (Portfolio Reporting)

**Inputs the user can set (assumptions):**
- Asset mix: %US Equity, %Intl Equity, %Fixed Income (muni/taxable), %Alts PE, %Alts HF, %Alts RE, %Cash
- Strategy: active vs passive; turnover %; yield %; distribution frequency
- Holding period: short vs long gains split; lot selection (FIFO/Specific ID)
- Tax profile: filing status; marginal ordinary & LTCG rates; NIIT; state tax; loss carryforwards
- Accounts: % tax-deferred / tax-exempt
- Horizon: 1y / 3y / 5y / 10y
- Actions: rebalance, harvest losses (on/off), realize gains, reinvest vs cash out

**Outputs:**
- Pre-tax vs after-tax return; tax drag %; estimated taxes by bucket (Ordinary/LTCG/NIIT/State)
- Explainability panel: “What drove the tax drag?” with a simple waterfall narrative
