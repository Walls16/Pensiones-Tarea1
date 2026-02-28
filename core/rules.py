# core/rules.py
def find_rate(df, salario):
    row = df[
        (df["sbc_min"] <= salario) &
        (salario <= df["sbc_max"])
    ]

    if row.empty:
        raise ValueError("Salario fuera de rango")

    return float(row.iloc[0]["tasa"])