from sqlalchemy import BigInteger, Column, Float, Integer, String, UniqueConstraint

from app.database.database import Base


class TradeRecord(Base):
    __tablename__ = "trade_records"

    __table_args__ = (
        UniqueConstraint(
            "hs_code",
            "country",
            "year",
            "month",
            name="uq_trade_record"
        ),
    )

    id = Column(Integer, primary_key=True)
    hs_code = Column(String, nullable=False)
    country = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    value_usd = Column(BigInteger, nullable=False)
    share_pct = Column(Float, nullable=False)