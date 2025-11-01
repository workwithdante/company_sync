import polars as pl
from .base import PolicyAdapter
from .registry import register
from .utils import (
    POLICY_COLS, clean_policy_number, upper_trim, to_date_any, to_number, lit_company
)

@register("oscar")
class OscarAdapter(PolicyAdapter):
    def to_canonical_df(self, df: pl.DataFrame, source_name: str) -> pl.DataFrame:
        out = (
            df.with_columns([
                clean_policy_number(pl.col("Member ID")).alias("policy_number"),
                upper_trim(pl.col("Member ID")).alias("member_id"),
                upper_trim(pl.col("Plan")).alias("plan_code"),
                upper_trim(pl.col("Enrollment type")).alias("variant"),
                lit_company("Oscar").alias("company"),
                pl.lit(None, dtype=pl.Utf8).alias("broker"),
                upper_trim(pl.col("State")).alias("state"),
                to_date_any(pl.col("Coverage start date")).alias("effective_date"),
                to_date_any(pl.col("Coverage end date")).alias("termination_date"),
                pl.lit(None, dtype=pl.Date).alias("sales_date"),
                to_number(pl.col("Premium amount")).alias("premium"),
                pl.lit("USD").alias("currency"),
                pl.lit(source_name).alias("source"),
                upper_trim(pl.col("Member ID")).alias("external_id"),
            ])
            .select(POLICY_COLS)
        )
        return out
