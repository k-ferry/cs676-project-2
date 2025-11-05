# PM Priya (Power User) — 20251025-141824
**Scenario:** First look (discovery + immediate reaction)

## Feature (brief)
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

## Assumptions
Mix: US 40% / Intl 20% / FI 15% / AltsHF 5% / AltsPE 10% / AltsRE 5%  / Cash 5%
Turnover 40%, Yield 2%, Horizon 1y
Lots: FIFO, HarvestLosses: ON, Reinvest: Yes
Tax: Ord 37%, LTCG 20%, NIIT 3%, State 6%
Acct: Tax-Deferred 20%, Tax-Exempt 0%

## Transcript
- **User**: Evaluate this feature and assumptions.

        === FEATURE ===
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

        === ASSUMPTION SUMMARY ===
        Mix: US 40% / Intl 20% / FI 15% / AltsHF 5% / AltsPE 10% / AltsRE 5%  / Cash 5%
Turnover 40%, Yield 2%, Horizon 1y
Lots: FIFO, HarvestLosses: ON, Reinvest: Yes
Tax: Ord 37%, LTCG 20%, NIIT 3%, State 6%
Acct: Tax-Deferred 20%, Tax-Exempt 0%

        === SCENARIO ===
        First look (discovery + immediate reaction)

        Task: Provide 3 specific issues (tag each with one of:
        usability, copy, trust, speed, a11y, discoverability),
        2 concrete suggestions, and 1 follow-up question.
- **PM Priya (Power User)**: 1. **Usability Issue**: The feature requires users to input a lot of assumptions, which can be overwhelming. Simplifying the input process or providing default values could enhance user experience. 

2. **Trust Issue**: The explainability panel needs to clearly articulate how the tax drag is calculated. Users may not trust the outputs if they don't understand the underlying logic. 

3. **Speed Issue**: The number of inputs may slow down the process, especially for users on mobile devices. Reducing the number of required fields or allowing for bulk input could improve speed. 

**Suggestions**: 
1. Implement a guided setup for the assumptions, where users can gradually input their data with tooltips explaining each field. 
2. Add a summary screen before finalizing inputs, allowing users to review and adjust their assumptions easily. 

**Follow-up Question**: How do we plan to ensure that the outputs are easily interpretable for users with varying levels of financial literacy?
- **User**: Add one NEW issue (tagged: usability/copy/trust/speed/a11y/discoverability), one NEW suggestion, and one concise follow-up question. Answer in plain text (no JSON).
- **PM Priya (Power User)**: (no content)
- **User**: Add one NEW issue (tagged: usability/copy/trust/speed/a11y/discoverability), one NEW suggestion, and one concise follow-up question. Answer in plain text (no JSON).
- **PM Priya (Power User)**: **New Discoverability Issue**: The feature lacks clear guidance on how to access the explainability panel, which may lead to users missing out on important insights. 

**New Suggestion**: Add a tooltip or a help icon next to the output section that directs users to the explainability panel for further details. 

**Follow-up Question**: What measures are in place to ensure that users are aware of all available features within the tool?
- **User**: Add one NEW issue (tagged: usability/copy/trust/speed/a11y/discoverability), one NEW suggestion, and one concise follow-up question. Answer in plain text (no JSON).
- **PM Priya (Power User)**: **New Speed Issue**: The loading time for the tax impact preview may be too long, especially with complex portfolios, leading to user frustration. 

**New Suggestion**: Optimize the backend calculations to ensure faster response times, possibly by caching common scenarios. 

**Follow-up Question**: What performance benchmarks are we aiming for with this feature?

## Ratings
- Clarity: 3/5
- Confidence: 3/5
- Likelihood: 3/5

## Notes / Actionables
- [ ]
- [ ]
