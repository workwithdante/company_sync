import polars as pl
from .base import PolicyAdapter
from .registry import register
from .utils import (
    POLICY_COLS, clean_policy_number, upper_trim, to_date_any, to_number, lit_company
)

@register("ambetter")
class AmbetterAdapter(PolicyAdapter):
    def to_canonical_df(self, df: pl.DataFrame, source_name: str) -> pl.DataFrame:
        out = (
            df.with_columns([
                clean_policy_number(pl.col("Policy Number")).alias("policy_number"),
                upper_trim(pl.col("Exchange Subscriber ID")).alias("member_id"),
                upper_trim(pl.col("Plan Name")).alias("plan_code"),
                pl.lit(None, dtype=pl.Utf8).alias("variant"),
                lit_company("Ambetter").alias("company"),
                upper_trim(pl.col("Broker Name")).alias("broker"),
                upper_trim(pl.col("State")).alias("state"),
                to_date_any(pl.col("Policy Effective Date")).alias("effective_date"),
                to_date_any(pl.col("Policy Term Date")).alias("termination_date"),
                to_date_any(pl.col("Broker Effective Date")).alias("sales_date"),
                to_number(pl.col("Monthly Premium Amount")).alias("premium"),
                pl.lit("USD").alias("currency"),
                pl.lit(source_name).alias("source"),
                upper_trim(pl.col("Exchange Subscriber ID")).alias("external_id"),
            ])
            .select(POLICY_COLS)
        )
        return out
