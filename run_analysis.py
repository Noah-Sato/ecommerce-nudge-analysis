"""
Reproduces the dissertation's core statistical analysis in Python:
a binary logistic regression of product choice on treatment status
for each of the four behavioural conditions, with likelihood-ratio
test, odds ratio, and average marginal effects (the Python
equivalent of Stata's `logit` + `margins`).
"""
import math
import pandas as pd
from scipy.stats import norm, chi2
from clean_data import build_all_conditions


def analyse_condition(name, data):
    # Binary logistic regression with a single binary regressor is a saturated
    # 2x2 model, so the MLE has an exact closed form identical to what
    # statsmodels/Stata's `logit` would return - no iterative fitting needed.
    n11 = ((data["treated"] == 1) & (data["chose_target"] == 1)).sum()
    n10 = ((data["treated"] == 1) & (data["chose_target"] == 0)).sum()
    n01 = ((data["treated"] == 0) & (data["chose_target"] == 1)).sum()
    n00 = ((data["treated"] == 0) & (data["chose_target"] == 0)).sum()

    n1, n0 = n11 + n10, n01 + n00
    treatment_rate, control_rate = n11 / n1, n01 / n0

    # Log-odds ratio (treated coefficient) and its Woolf/MLE standard error
    coef = math.log((n11 * n00) / (n10 * n01))
    se = math.sqrt(1 / n11 + 1 / n10 + 1 / n01 + 1 / n00)
    z = coef / se
    p_value = 2 * (1 - norm.cdf(abs(z)))
    odds_ratio = math.exp(coef)

    # Likelihood-ratio test vs. the null (intercept-only) model
    p_pooled = (n11 + n01) / (n1 + n0)
    ll_null = (n11 + n01) * math.log(p_pooled) + (n10 + n00) * math.log(1 - p_pooled)
    ll_full = (n11 * math.log(treatment_rate) + n10 * math.log(1 - treatment_rate)
               + n01 * math.log(control_rate) + n00 * math.log(1 - control_rate))
    lr_chi2 = 2 * (ll_full - ll_null)
    lr_p = 1 - chi2.cdf(lr_chi2, df=1)

    # Average marginal effect: in a saturated model this is exactly the
    # difference in predicted probabilities between groups (Stata's `margins`
    # for a binary regressor with no other covariates gives the same figure).
    ame_val = treatment_rate - control_rate
    ame_se = math.sqrt(treatment_rate * (1 - treatment_rate) / n1 + control_rate * (1 - control_rate) / n0)
    ame_z = ame_val / ame_se
    ame_p = 2 * (1 - norm.cdf(abs(ame_z)))
    ame = {"dy/dx": ame_val, "Pr(>|z|)": ame_p}

    print(f"\n{'='*60}\n{name}  (n={len(data)})\n{'='*60}")
    print(f"Control group target-choice rate:   {control_rate:.1%}")
    print(f"Treatment group target-choice rate: {treatment_rate:.1%}")
    print(f"Percentage-point difference:        {(treatment_rate-control_rate)*100:.1f} pp")
    print(f"\nLogit coefficient (treated):  {coef:.4f}")
    print(f"p-value:                      {p_value:.4f}")
    print(f"Odds ratio exp(coef):         {odds_ratio:.2f}")
    print(f"Likelihood ratio chi2:        {lr_chi2:.2f}  (p = {lr_p:.4f})")
    print(f"\nAverage marginal effect (dy/dx): {ame['dy/dx']:.4f}  (p = {ame['Pr(>|z|)']:.4f})")

    return {
        "condition": name, "n": len(data),
        "control_rate": control_rate, "treatment_rate": treatment_rate,
        "coef": coef, "p_value": p_value, "odds_ratio": odds_ratio,
        "lr_chi2": lr_chi2, "lr_p": lr_p,
        "ame": ame["dy/dx"], "ame_p": ame["Pr(>|z|)"],
    }


if __name__ == "__main__":
    conditions = build_all_conditions()
    results = [analyse_condition(name, data) for name, data in conditions.items()]

    summary = pd.DataFrame(results).set_index("condition")
    summary.to_csv("results_summary.csv")
    print("\n\nSaved results_summary.csv")
    print(summary.round(3))
