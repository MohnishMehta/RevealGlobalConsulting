from sqlalchemy.orm import Session

from app.database.models import TradeRecord


def get_trade_records(
    db: Session,
    hs_code: str,
    year: int,
    month: int
):
    return (
        db.query(TradeRecord)
        .filter(
            TradeRecord.hs_code == hs_code,
            TradeRecord.year == year,
            TradeRecord.month == month
        )
        .all()
    )


def save_trade_records(
    db: Session,
    hs_code: str,
    year: int,
    month: int,
    suppliers: list[dict]
):
    records = []

    for supplier in suppliers:
        record = TradeRecord(
            hs_code=hs_code,
            country=supplier["country"],
            cty_code=supplier["CTY_CODE"],
            commodity=supplier["commodity"],
            year=year,
            month=month,
            value_usd=supplier["value_usd"],
            share_pct=supplier["share_pct"]
        )

        records.append(record)

    db.add_all(records)
    db.commit()

    return records


def records_to_month_result(
    records: list[TradeRecord],
    year: int,
    month: int
):
    suppliers = []

    for record in records:
        suppliers.append({
            "CTY_CODE": record.cty_code,
            "country": record.country,
            "commodity": record.commodity,
            "value_usd": record.value_usd,
            "time": f"{year}-{month:02d}",
            "hs_code": record.hs_code,
            "share_pct": record.share_pct
        })

    total_imports = sum(
        record.value_usd
        for record in records
    )

    suppliers.sort(
        key=lambda supplier: supplier["value_usd"],
        reverse=True
    )

    hhi = sum(
        ((record.value_usd / total_imports) * 100) ** 2
        for record in records
    )

    return {
        "year": year,
        "month": month,
        "total_imports": total_imports,
        "hhi": round(hhi, 2),
        "suppliers": suppliers
    }