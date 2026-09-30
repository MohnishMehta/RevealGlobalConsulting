import os
import requests

from dotenv import load_dotenv

load_dotenv()

CENSUS_API_KEY = os.getenv("CENSUS_API_KEY")

if CENSUS_API_KEY is None:
    raise RuntimeError("CENSUS_API_KEY is not set")


def fetch_census_imports(
    hs_code: str,
    year: int,
    month: int
):
    url = "https://api.census.gov/data/timeseries/intltrade/imports/hs"

    params = {
        "get": "CTY_CODE,CTY_NAME,I_COMMODITY_SDESC,GEN_VAL_MO",
        "time": f"{year}-{month:02d}",
        "I_COMMODITY": hs_code,
        "key": CENSUS_API_KEY
    }

    response = requests.get(url, params=params)

    response.raise_for_status()

    return response.json()