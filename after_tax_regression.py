# after_tax_regression.py
"""
Train a regression model to predict AFTER-TAX RETURN from
simulated portfolio + tax profile features.

- We simulate a dataset with:
  - pre_tax_return (annual)
  - turnover
  - yield
  - ordinary tax rate
  - long-term capital gains rate
  - NIIT
  - state tax rate
  - % tax-deferred
  - % tax-exempt

- We compute a "true" after-tax return with a simple formula + noise.
- Then we train a LinearRegression model to approximate that mapping.
"""

from typing import Dict, Any

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error


def _simulate_after_tax_data(
    n_samples: int = 2000,
    random_state: int = 42,
) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)

    # Core portfolio characteristics
    # Pre-tax total return between roughly -30% and +30%
    pre_tax_return = np.clip(rng.normal(loc=0.07, scale=0.10, size=n_samples), -0.30, 0.30)
    # Turnover between 10% and 150%
    turnover = rng.uniform(0.10, 1.50, size=n_samples)
    # Yield between 0% and 5%
    yield_pct = rng.uniform(0.00, 0.05, size=n_samples)

    # Tax profile
    ord_rate = rng.uniform(0.24, 0.37, size=n_samples)     # ordinary income
    ltcg_rate = rng.uniform(0.15, 0.20, size=n_samples)    # long-term capital gains
    niit = np.full(n_samples, 0.038)                       # NIIT fixed for simplicity
    state_rate = rng.uniform(0.00, 0.10, size=n_samples)   # state

    # Account mix
    tax_deferred = rng.uniform(0.00, 0.50, size=n_samples)
    tax_exempt = rng.uniform(0.00, 0.30, size=n_samples)
    # Ensure we don't exceed 100% (simple cap)
    total_tax_adv = tax_deferred + tax_exempt
    over_1 = total_tax_adv > 0.90
    tax_deferred[over_1] *= 0.90 / total_tax_adv[over_1]
    tax_exempt[over_1] *= 0.90 / total_tax_adv[over_1]

    taxable_share = 1.0 - (tax_deferred + tax_exempt)

    # Mix of income vs capital gains
    cap_gains_share = np.clip(0.5 + 0.3 * (rng.random(n_samples) - 0.5), 0.0, 1.0)

    # Base effective tax rate on the taxable portion
    rate_income = ord_rate + niit + state_rate
    rate_gains = ltcg_rate + niit + state_rate
    blended_rate = cap_gains_share * rate_gains + (1.0 - cap_gains_share) * rate_income

    # Turnover amplifies how much of pre-tax return is realized in the current year
    realization_factor = np.clip(0.3 + 0.7 * turnover, 0.0, 2.0)

    effective_tax_rate = np.clip(taxable_share * blended_rate * realization_factor, 0.0, 0.80)

    # "True" after-tax return with a tiny bit of noise
    noise = rng.normal(loc=0.0, scale=0.005, size=n_samples)
    after_tax_return = pre_tax_return * (1.0 - effective_tax_rate) + noise

    df = pd.DataFrame(
        {
            "pre_tax_return": pre_tax_return,
            "turnover": turnover,
            "yield": yield_pct,
            "ord_rate": ord_rate,
            "ltcg_rate": ltcg_rate,
            "niit": niit,
            "state_rate": state_rate,
            "tax_deferred": tax_deferred,
            "tax_exempt": tax_exempt,
            "taxable_share": taxable_share,
            "effective_tax_rate": effective_tax_rate,
            "after_tax_return": after_tax_return,
        }
    )
    return df


def run_after_tax_regression(
    n_samples: int = 2000,
    random_state: int = 42,
) -> Dict[str, Any]:
    """
    Simulate an after-tax dataset, train a linear regression model,
    and return metrics + a small sample of predictions.

    Returns a dict with:
        - n_samples
        - n_features
        - test_size
        - test_r2
        - test_mae
        - sample_df: pandas DataFrame with a few example rows
    """
    df = _simulate_after_tax_data(n_samples=n_samples, random_state=random_state)

    feature_cols = [
        "pre_tax_return",
        "turnover",
        "yield",
        "ord_rate",
        "ltcg_rate",
        "niit",
        "state_rate",
        "tax_deferred",
        "tax_exempt",
        "taxable_share",
        "effective_tax_rate",
    ]
    X = df[feature_cols]
    y = df["after_tax_return"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    # Build a small sample table for display
    sample = X_test.copy()
    sample["true_after_tax_return"] = y_test
    sample["pred_after_tax_return"] = y_pred
    sample = sample.head(10).reset_index(drop=True)

    return {
        "n_samples": int(df.shape[0]),
        "n_features": int(X.shape[1]),
        "test_size": int(X_test.shape[0]),
        "test_r2": float(r2),
        "test_mae": float(mae),
        "sample_df": sample,
    }


if __name__ == "__main__":
    results = run_after_tax_regression()
    print(
        f"After-tax regression demo: R^2 = {results['test_r2']:.3f}, "
        f"MAE = {results['test_mae']:.4f}"
    )
    print()
    print(results["sample_df"])