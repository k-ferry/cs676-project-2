# PM Priya (Power User) — 20251025-133304
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
- **PM Priya (Power User)**: {'action': {'type': 'DONE', 'content': '', 'target': ''}, 'cognitive_state': {'goals': 'Evaluate the feature and assumptions for the After-Tax Return / Tax-Impact Preview, focusing on usability, trust, speed, and accessibility.', 'context': ['Feature evaluation for After-Tax Return / Tax-Impact Preview', 'Assumptions provided for the evaluation task'], 'attention': "The feature's complexity and the need for clarity in user inputs and outputs.", 'emotions': 'Impatient with the complexity of the inputs and the need for a more streamlined user experience.'}}
- **User**: Add one NEW issue (tagged: usability/copy/trust/speed/a11y/discoverability), one NEW suggestion, and one concise follow-up question. Answer in plain text (no JSON).
- **PM Priya (Power User)**: {'action': {'type': 'DONE', 'content': '', 'target': ''}, 'cognitive_state': {'goals': 'Add a new issue, suggestion, and follow-up question regarding the After-Tax Return / Tax-Impact Preview feature.', 'context': ['Feature evaluation for After-Tax Return / Tax-Impact Preview', 'Assumptions provided for the evaluation task'], 'attention': 'The need for improved usability and user guidance in the feature.', 'emotions': 'Frustrated with the current complexity and eager for enhancements.'}}
- **User**: Add one NEW issue (tagged: usability/copy/trust/speed/a11y/discoverability), one NEW suggestion, and one concise follow-up question. Answer in plain text (no JSON).
- **PM Priya (Power User)**: {'action': {'type': 'DONE', 'content': '', 'target': ''}, 'cognitive_state': {'goals': 'Add a new issue, suggestion, and follow-up question regarding the After-Tax Return / Tax-Impact Preview feature.', 'context': ['Feature evaluation for After-Tax Return / Tax-Impact Preview', 'Assumptions provided for the evaluation task'], 'attention': "The need for improved trust and transparency in the feature's calculations.", 'emotions': 'Concerned about user trust and the accuracy of the information provided.'}}
- **User**: Add one NEW issue (tagged: usability/copy/trust/speed/a11y/discoverability), one NEW suggestion, and one concise follow-up question. Answer in plain text (no JSON).
- **PM Priya (Power User)**: {'action': {'type': 'DONE', 'content': '', 'target': ''}, 'cognitive_state': {'goals': 'Add a new issue, suggestion, and follow-up question regarding the After-Tax Return / Tax-Impact Preview feature.', 'context': ['Feature evaluation for After-Tax Return / Tax-Impact Preview', 'Assumptions provided for the evaluation task'], 'attention': 'The need for improved discoverability of key features in the tool.', 'emotions': 'Frustrated with the current layout and eager for enhancements.'}}

## Ratings
- Clarity: 3/5
- Confidence: 3/5
- Likelihood: 3/5

## Notes / Actionables
- [ ]
- [ ]
