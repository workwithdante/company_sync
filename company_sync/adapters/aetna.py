import polars as pl
from .base import PolicyAdapter
from .registry import register
from .utils import (
    POLICY_COLS, clean_policy_number, upper_trim, to_date_any, to_number, lit_company
)

@register("aetna")
class AetnaAdapter(PolicyAdapter):
    def to_canonical_df(self, df: pl.DataFrame, source_name: str) -> pl.DataFrame:
        out = (
            df.with_columns([
                clean_policy_number(pl.col("Issuer Assigned ID")).alias("policy_number"),
                upper_trim(pl.col("Exchange Assigned ID")).alias("member_id"),
                upper_trim(pl.col("Member Plan ID")).alias("plan_code"),
                upper_trim(pl.col("Metal Tier")).alias("variant"),
                lit_company("Aetna").alias("company"),
                pl.lit(None, dtype=pl.Utf8).alias("broker"),
                upper_trim(pl.col("State")).alias("state"),
                to_date_any(pl.col("Plan Effective Date")).alias("effective_date"),
                pl.lit(None, dtype=pl.Date).alias("termination_date"),
                pl.lit(None, dtype=pl.Date).alias("sales_date"),
                to_number(pl.col("Monthly Premium")).alias("premium"),
                pl.lit("USD").alias("currency"),
                pl.lit(source_name).alias("source"),
                upper_trim(pl.col("Exchange Assigned ID")).alias("external_id"),
            ])
            .select(POLICY_COLS)
        )
        return out
