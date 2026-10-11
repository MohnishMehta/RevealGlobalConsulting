from fastapi import APIRouter

from app.analytics.trade import (
    analyze_month,
    calculate_country_exposure,
    calculate_dependency_change,
    calculate_growth,
    clean_trade_data
)
from app.database.crud import (
    get_trade_records,
    records_to_month_result,
    save_trade_records
)
from app.database.database import SessionLocal
from app.services.census import fetch_census_imports


router = APIRouter()


@router.get("/imports")
def get_imports(
    hs_code: str,
    start_year: int,
    start_month: int,
    end_year: int,
    end_month: int,
    country: str = "CANADA"
):
    current_year = start_year
    current_month = start_month
    all_results = []

    db = SessionLocal()

    while current_year < end_year or (
        current_year == end_year and current_month <= end_month
    ):

        existing_records = get_trade_records(
            db,
            hs_code,
            current_year,
            current_month
        )

        if existing_records:
            print("Using database")

            month_result = records_to_month_result(
                existing_records,
                current_year,
                current_month
            )

        else:
            print("Calling Census API")

            data = fetch_census_imports(
                hs_code,
                current_year,
                current_month
            )

            df = clean_trade_data(data)

            month_result = analyze_month(
                df,
                current_year,
                current_month
            )

            save_trade_records(
                db,
                hs_code,
                current_year,
                current_month,
                month_result["suppliers"]
            )

        all_results.append(month_result)

        current_month += 1

        if current_month == 13:
            current_month = 1
            current_year += 1

    db.close()

    all_results = calculate_growth(all_results)

    country_exposure = calculate_country_exposure(
        all_results,
        country
    )

    dependency_change = calculate_dependency_change(
        country_exposure
    )

    return {
        "hs_code": hs_code,
        "start": f"{start_year}-{start_month:02d}",
        "end": f"{end_year}-{end_month:02d}",
        "country": country.upper(),
        "country_exposure": country_exposure,
        "dependency_change_pct_points": dependency_change,
        "results": all_results
    }