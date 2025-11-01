import polars as pl
from .base import PolicyAdapter
from .registry import register
from .utils import (
    POLICY_COLS, clean_policy_number, upper_trim, to_date_any, to_number
)

@register("healthsherpa")
class HealthSherpaAdapter(PolicyAdapter):
    def to_canonical_df(self, df: pl.DataFrame, source_name: str) -> pl.DataFrame:
        out = (
            df.with_columns([
                clean_policy_number(
                    pl.coalesce([pl.col("issuer_assigned_policy_id"),
                                 pl.col("issuer_assigned_subscriber_id"),
                                 pl.col("ffm_app_id")])
                ).alias("policy_number"),
                upper_trim(
                    pl.coalesce([pl.col("issuer_assigned_primary_member_id"),
                                 pl.col("ffm_subscriber_id")])
                ).alias("member_id"),
                upper_trim(
                    pl.coalesce([pl.col("plan_hios_id"), pl.col("plan")])
                ).alias("plan_code"),
                upper_trim(pl.col("plan_name")).alias("variant"),
                upper_trim(pl.col("issuer")).alias("company"),
                pl.lit(None, dtype=pl.Utf8).alias("broker"),
                upper_trim(pl.col("state")).alias("state"),
                to_date_any(pl.col("effective_date")).alias("effective_date"),
                to_date_any(pl.coalesce([pl.col("expiration_date"), pl.col("date_cancelled")])).alias("termination_date"),
                to_date_any(pl.coalesce([pl.col("submission_date"), pl.col("application_creation_date")])).alias("sales_date"),
                to_number(pl.coalesce([pl.col("premium"), pl.col("gross_premium")])).alias("premium"),
                pl.lit("USD").alias("currency"),
                pl.lit(source_name).alias("source"),
                upper_trim(pl.col("ffm_app_id")).alias("external_id"),
            ])
            .select(POLICY_COLS)
        )
        return out
