import polars as pl
from .base import PolicyAdapter
from .registry import register
from .utils import (
    POLICY_COLS, clean_policy_number, upper_trim, to_date_any, to_number, lit_company
)

@register("molina")
class MolinaAdapter(PolicyAdapter):
    def to_canonical_df(self, df: pl.DataFrame, source_name: str) -> pl.DataFrame:
        out = (
            df.with_columns([
                clean_policy_number(
                    pl.coalesce([pl.col("Subscriber_ID"), pl.col("HIX_ID")])
                ).alias("policy_number"),
                upper_trim(pl.col("HIX_ID")).alias("member_id"),
                upper_trim(pl.col("Product")).alias("plan_code"),
                pl.lit(None, dtype=pl.Utf8).alias("variant"),
                lit_company("Molina").alias("company"),
                pl.lit(None, dtype=pl.Utf8).alias("broker"),
                upper_trim(pl.col("State")).alias("state"),
                to_date_any(pl.col("Effective_date")).alias("effective_date"),
                to_date_any(pl.coalesce([pl.col("End_Date"), pl.col("Scheduled_Term_Date")])).alias("termination_date"),
                to_date_any(pl.col("Application_Date")).alias("sales_date"),
                to_number(pl.coalesce([pl.col("Member_Premium"), pl.col("Total_Premium")])).alias("premium"),
                pl.lit("USD").alias("currency"),
                pl.lit(source_name).alias("source"),
                upper_trim(pl.col("Subscriber_ID")).alias("external_id"),
            ])
            .select(POLICY_COLS)
        )
        return out
