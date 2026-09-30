import pandas as pd

EXCLUDE_GROUPS = [
    "TOTAL FOR ALL COUNTRIES",
    "EUROPEAN UNION",
    "NORTH AMERICA",
    "EUROPE",
    "AFRICA",
    "PACIFIC RIM COUNTRIES",
    "ASIA",
    "USMCA (NAFTA)",
    "OECD",
    "NATO",
    "EURO AREA",
    "APEC",
    "ASEAN"
]

def analyze_month(df, year, month):
    total_imports = df["value_usd"].sum()

    if total_imports == 0:
        return {
            "year": year,
            "month": month,
            "total_imports": 0,
            "hhi": 0,
            "suppliers": []
        }

    df["share_pct"] = (
        df["value_usd"] / total_imports
    ) * 100

    df = df.sort_values(
        by="share_pct",
        ascending=False
    )

    hhi = (df["share_pct"] ** 2).sum()

    df["share_pct"] = df["share_pct"].round(2)
    hhi = round(hhi, 2)

    return {
        "year": year,
        "month": month,
        "total_imports": int(total_imports),
        "hhi": hhi,
        "suppliers": df.to_dict(orient="records")
    }

def clean_trade_data(data):
    headers = data[0]
    rows = data[1:]

    df = pd.DataFrame(rows, columns=headers)

    df["GEN_VAL_MO"] = pd.to_numeric(df["GEN_VAL_MO"])

    df = df.rename(columns={
        "I_COMMODITY_SDESC": "commodity",
        "GEN_VAL_MO": "value_usd",
        "CTY_NAME": "country",
        "I_COMMODITY": "hs_code"
    })

    df = df[~df["country"].isin(EXCLUDE_GROUPS)]

    df = df[
        ~df["CTY_CODE"].str.contains("XXX", na=False)
        & ~df["CTY_CODE"].str.startswith("00", na=False)
        & (df["CTY_CODE"] != "-")
    ]

    return df

def calculate_growth(all_results):
    if all_results:
        all_results[0]["growth_pct"] = None

    for i in range(1, len(all_results)):
        previous_total = all_results[i - 1]["total_imports"]
        current_total = all_results[i]["total_imports"]

        if previous_total == 0:
            growth_pct = None
        else:
            growth_pct = (
                (current_total - previous_total)
                / previous_total
            ) * 100

        all_results[i]["growth_pct"] = (
            round(growth_pct, 2)
            if growth_pct is not None
            else None
        )

    return all_results


def calculate_country_exposure(all_results, country):
    country_exposure = []

    for result in all_results:
        country_share = 0

        for supplier in result["suppliers"]:
            if supplier["country"].upper() == country.upper():
                country_share = supplier["share_pct"]
                break

        country_exposure.append({
            "year": result["year"],
            "month": result["month"],
            "share_pct": country_share
        })

    return country_exposure


def calculate_dependency_change(country_exposure):
    dependency_change = None

    if len(country_exposure) >= 2:
        dependency_change = round(
            country_exposure[-1]["share_pct"]
            - country_exposure[0]["share_pct"],
            2
        )

    return dependency_change