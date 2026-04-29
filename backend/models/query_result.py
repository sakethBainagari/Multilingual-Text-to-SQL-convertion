"""Data models for the NL-to-SQL system."""

from dataclasses import dataclass, field
from typing import Optional
import pandas as pd


@dataclass
class QueryResult:
    """Data class for query results."""

    success: bool
    data: Optional[pd.DataFrame]
    sql_query: str
    execution_time: float
    error_message: Optional[str] = None
    visualization_path: Optional[str] = None

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    @property
    def row_count(self) -> int:
        """Return the number of rows in the result data."""
        if self.data is not None and not self.data.empty:
            return len(self.data)
        return 0

    def to_dict(self) -> dict:
        """Serialize the result to a JSON-friendly dictionary."""
        result = {
            "success": self.success,
            "sql_query": self.sql_query,
            "execution_time": self.execution_time,
            "row_count": self.row_count,
            "data": self.data.to_dict("records") if self.data is not None else None,
        }
        if self.error_message:
            result["error"] = self.error_message
        if self.visualization_path:
            result["visualization_path"] = self.visualization_path
        return result
