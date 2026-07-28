"""
Data cleaning: reshapes the raw Qualtrics export into four tidy,
per-condition datasets (Scarcity, Social Proof, Compromise, Decoy),
each with a binary group indicator (treatment/control) and the
recorded product choice.

Mapping (confirmed by matching resulting proportions against the
values reported in the dissertation's logistic regression appendices):
    Wireless Earbuds columns -> Scarcity condition
    Power Bank columns       -> Social Proof condition
    Smart TV columns         -> Compromise condition
    Smart Phone columns      -> Decoy condition
In each product's pair of columns, the first (no suffix) column is
the treatment block; the second (".1" suffix) column is the control
block, per Qualtrics' block-level display logic.
"""
import pandas as pd

RAW_PATH = "Raw_Data.xlsx"


def load_raw():
    df = pd.read_excel(RAW_PATH, sheet_name="Sheet1")
    # First row after the header is Qualtrics' internal ImportId metadata row, not a response
    df = df.iloc[1:].reset_index(drop=True)
    return df


def build_condition(df, treat_col, control_col, target_choice):
    """Stack a product's treatment/control columns into one tidy frame.

    target_choice: the option label counted as the outcome of interest
    (1 = chose target_choice, 0 = chose a different valid option).
    """
    treat = df[[treat_col]].rename(columns={treat_col: "choice"}).dropna()
    treat["group"] = "treatment"

    control = df[[control_col]].rename(columns={control_col: "choice"}).dropna()
    control["group"] = "control"

    stacked = pd.concat([treat, control], ignore_index=True)
    stacked["choice"] = stacked["choice"].astype(str).str.strip()
    stacked["chose_target"] = (stacked["choice"] == target_choice).astype(int)
    stacked["treated"] = (stacked["group"] == "treatment").astype(int)
    return stacked


def build_all_conditions():
    df = load_raw()
    cols = df.columns.tolist()

    earbuds_t, earbuds_c = cols[1], cols[2]
    powerbank_t, powerbank_c = cols[3], cols[4]
    tv_t, tv_c = cols[5], cols[6]
    phone_t, phone_c = cols[7], cols[8]

    conditions = {
        "Scarcity": build_condition(df, earbuds_t, earbuds_c, "Wireless Earbuds B"),
        "Social Proof": build_condition(df, powerbank_t, powerbank_c, "Power Bank B"),
        "Compromise": build_condition(df, tv_t, tv_c, "Smart TV B"),
        # Decoy analyses selection of the asymmetrically dominant option, Product A
        "Decoy": build_condition(df, phone_t, phone_c, "Smart Phone A"),
    }
    return conditions


if __name__ == "__main__":
    conditions = build_all_conditions()
    for name, d in conditions.items():
        print(f"\n{name}: n={len(d)}")
        print(d.groupby("group")["chose_target"].agg(["mean", "count"]))
