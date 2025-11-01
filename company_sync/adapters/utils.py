import polars as pl

# Contrato canónico (orden esperado por etl.stg_policy)
POLICY_COLS = [
    "policy_number","member_id","plan_code","variant",
    "company","broker","state",
    "effective_date","termination_date","sales_date",
    "premium","currency","source","external_id"
]

def upper_trim(e: pl.Expr) -> pl.Expr:
    return e.cast(pl.Utf8, strict=False).str.strip_chars().str.to_uppercase()

def clean_policy_number(e: pl.Expr) -> pl.Expr:
    return e.cast(pl.Utf8, strict=False).str.replace_all(r"\s+", "").str.to_uppercase()

def to_date_any(e: pl.Expr, fmts=("%Y-%m-%d","%m/%d/%Y","%d/%m/%Y","%m-%d-%Y","%d-%m-%Y")) -> pl.Expr:
    # intenta secuencialmente varios formatos
    out = pl.lit(None, dtype=pl.Date)
    for fmt in fmts:
        out = pl.when(out.is_null()).then(e.str.strptime(pl.Date, fmt=fmt, strict=False)).otherwise(out)
    return out

def to_number(e: pl.Expr) -> pl.Expr:
    return (
        e.cast(pl.Utf8, strict=False)
         .str.replace_all(r"[\$,]", "")
         .str.strip_chars()
         .cast(pl.Float64, strict=False)
    )

def lit_company(name: str) -> pl.Expr:
    return pl.lit(name.upper())
