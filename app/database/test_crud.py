from app.database.database import SessionLocal
from app.database.crud import get_trade_records, save_trade_records


db = SessionLocal()

fake_suppliers = [
    {
        "country": "CANADA",
        "value_usd": 50000000,
        "share_pct": 41.5
    },
    {
        "country": "NORWAY",
        "value_usd": 20000000,
        "share_pct": 16.6
    }
]

save_trade_records(
    db,
    "7502",
    2025,
    1,
    fake_suppliers
)

records = get_trade_records(
    db,
    "7502",
    2025,
    1
)

for record in records:
    print(
        record.hs_code,
        record.country,
        record.year,
        record.month,
        record.value_usd,
        record.share_pct
    )

db.close()