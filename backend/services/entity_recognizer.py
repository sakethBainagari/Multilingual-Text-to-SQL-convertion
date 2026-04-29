"""Entity recognition from natural language queries."""

import re
from typing import Dict, List


class EntityRecognizer:
    """Recognise entities (tables, columns, values, operators) in NL queries."""

    def __init__(self):
        self.entity_patterns = {
            "table_names": r"\b(?:table|from|into|update|join)\s+(\w+)\b",
            "column_names": (
                r"\b(?:select|where|order by|group by)"
                r"\s+([a-zA-Z_]\w*(?:\s*,\s*[a-zA-Z_]\w*)*)"
            ),
            "numeric_values": r"\b\d+(?:\.\d+)?\b",
            "string_values": r"'([^']*)'|\"([^\"]*)\"",
            "operators": r"\b(?:=|!=|<|>|<=|>=|like|in|between)\b",
            "aggregations": r"\b(?:sum|avg|count|max|min|group by)\b",
        }

    def extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract entities from a natural language query."""
        entities: Dict[str, List[str]] = {}
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, query, re.IGNORECASE)
            entities[entity_type] = [m for m in matches if m]
        return entities

    def map_to_schema(self, entities: Dict, schema: Dict) -> Dict:
        """Map extracted entities to the database schema."""
        mapped: Dict[str, list] = {}
        if "table_names" in entities:
            mapped["tables"] = [
                t
                for t in entities["table_names"]
                if t.lower() in [s.lower() for s in schema.keys()]
            ]
        return mapped
