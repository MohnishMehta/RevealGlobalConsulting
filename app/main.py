import os
import requests

from fastapi import FastAPI
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

app = FastAPI()

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

if CENSUS_API_KEY is None:
    raise RuntimeError("CENSUS_API_KEY is not set")

@app.get("/")
def read_root():
    return {"message": "Reveal Global Consulting API"}

@app.get("/imports")
def get_imports(hs_code: str, year: int, month: int):

    url = "https://api.census.gov/data/timeseries/intltrade/imports/hs"

    params = {
        "get": "CTY_CODE,CTY_NAME,I_COMMODITY_SDESC,GEN_VAL_MO",
        "time": f"{year}-{month:02d}",
        "I_COMMODITY": hs_code,
        "key": CENSUS_API_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    data = response.json()

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

    exclude_groups = [
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

    df = df[~df["country"].isin(exclude_groups)]

    total_imports = df["value_usd"].sum()

    df["share_pct"] = (df["value_usd"] / total_imports) * 100

    df = df.sort_values(by="share_pct", ascending=False)

    print(df)

    return df.to_dict(orient="records")


    
    