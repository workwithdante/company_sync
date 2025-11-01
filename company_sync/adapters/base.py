from abc import ABC, abstractmethod
import polars as pl

class PolicyAdapter(ABC):
    @abstractmethod
    def to_canonical_df(self, df: pl.DataFrame, source_name: str) -> pl.DataFrame:
        """Devuelve un DataFrame Polars con las columnas del contrato Policy."""
        ...
