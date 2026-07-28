"""Bar chart of control vs. treatment target-choice rates for all four
behavioural conditions, annotated with significance from run_analysis.py."""
import pandas as pd
import matplotlib.pyplot as plt

summary = pd.read_csv("results_summary.csv", index_col="condition")
order = ["Social Proof", "Compromise", "Decoy", "Scarcity"]
summary = summary.loc[order]

fig, ax = plt.subplots(figsize=(8, 5))
x = range(len(summary))
width = 0.35

bars_control = ax.bar([i - width/2 for i in x], summary["control_rate"] * 100,
                       width, label="Control", color="#8C9EB2")
bars_treat = ax.bar([i + width/2 for i in x], summary["treatment_rate"] * 100,
                     width, label="Treatment", color="#1F3864")

for i, (idx, row) in enumerate(summary.iterrows()):
    sig = "*" if row["p_value"] < 0.05 else "n.s."
    y = max(row["control_rate"], row["treatment_rate"]) * 100 + 4
    ax.text(i, y, sig, ha="center", fontsize=11,
            fontweight="bold" if sig == "*" else "normal")

ax.set_xticks(list(x))
ax.set_xticklabels(order)
ax.set_ylabel("Target option choice rate (%)")
ax.set_title("Effect of behavioural nudges on product choice\n(* = significant at p<0.05, n.s. = not significant)")
ax.set_ylim(0, 100)
ax.legend()
fig.tight_layout()
fig.savefig("results_chart.png", dpi=150)
print("Saved results_chart.png")
