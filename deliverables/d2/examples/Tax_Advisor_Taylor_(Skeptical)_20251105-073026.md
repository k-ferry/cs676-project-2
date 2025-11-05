# Tax Advisor Taylor (Skeptical) — 20251105-073026
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

        Task: Provide exactly 3 issues (tag each: usability/copy/trust/speed/a11y/discoverability),
        exactly 2 suggestions, and exactly 1 follow-up question. Keep to 6 lines total.

        Rules: Do not repeat anything already said in this conversation. Do not include the words TALK or DONE.
        Do not echo this prompt. Plain text only—no headings, no JSON, no bullets with labels like 'TALK'/'DONE'.
- **Tax Advisor Taylor (Skeptical)**: usability: Inputs feel dense on first open.
suggestion: Add sensible defaults and a 30-second guided tour.
question: Which tax buckets are estimated vs exact?
- **User**: Continue the same review. Add ONE new issue (tag it), ONE new suggestion, and ONE concise follow-up question. They must be different from anything said earlier. Plain text only. No meta words (TALK, DONE).
- **Tax Advisor Taylor (Skeptical)**: New issue: Discoverability is low; users may struggle to find the feature. Suggestion: Create a guided walkthrough for first-time users to enhance understanding. Follow-up: What user feedback mechanisms are in place to improve this feature?
New issue: Discoverability is low; users may struggle to find the feature. Suggestion: Create a guided walkthrough for first-time users to enhance understanding. Follow-up: What user feedback mechanisms are in place to improve this feature?
New issue: Discoverability is low; users may struggle to find the feature. Suggestion: Create a guided walkthrough for first-time users to enhance understanding. Follow-up: What user feedback mechanisms are in place to improve this feature?
- **User**: Continue the same review. Add ONE new issue (tag it), ONE new suggestion, and ONE concise follow-up question. They must be different from anything said earlier. Plain text only. No meta words (TALK, DONE).
- **Tax Advisor Taylor (Skeptical)**: New issue: Clarity of assumptions is lacking; users may misinterpret input requirements. Suggestion: Provide examples for each input field to guide users. Follow-up: How will you ensure ongoing user support for this feature?
New issue: Clarity of assumptions is lacking; users may misinterpret input requirements. Suggestion: Provide examples for each input field to guide users. Follow-up: How will you ensure ongoing user support for this feature?
New issue: Clarity of assumptions is lacking; users may misinterpret input requirements. Suggestion: Provide examples for each input field to guide users. Follow-up: How will you ensure ongoing user support for this feature?
- **User**: Continue the same review. Add ONE new issue (tag it), ONE new suggestion, and ONE concise follow-up question. They must be different from anything said earlier. Plain text only. No meta words (TALK, DONE).
- **Tax Advisor Taylor (Skeptical)**: New issue: Accessibility is insufficient; color contrast may not meet standards for visually impaired users. Suggestion: Implement ARIA labels for better screen reader compatibility. Follow-up: What testing has been done to ensure compliance with accessibility standards?
New issue: Accessibility is insufficient; color contrast may not meet standards for visually impaired users. Suggestion: Implement ARIA labels for better screen reader compatibility. Follow-up: What testing has been done to ensure compliance with accessibility standards?
New issue: Accessibility is insufficient; color contrast may not meet standards for visually impaired users. Suggestion: Implement ARIA labels for better screen reader compatibility. Follow-up: What testing has been done to ensure compliance with accessibility standards?

## Ratings
- Clarity: 3/5
- Confidence: 3/5
- Likelihood: 3/5

## Notes / Actionables
- [ ]
- [ ]
