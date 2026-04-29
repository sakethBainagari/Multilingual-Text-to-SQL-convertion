"""FAISS-based similarity index for caching and matching queries."""

import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Optional heavy imports --------------------------------------------------
try:
    from sentence_transformers import SentenceTransformer

    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    SentenceTransformer = None  # type: ignore[assignment,misc]
    HAS_SENTENCE_TRANSFORMERS = False

try:
    import faiss

    HAS_FAISS = True
except ImportError:
    faiss = None  # type: ignore[assignment]
    HAS_FAISS = False


class SimilarityService:
    """Vector-similarity cache using FAISS + sentence-transformers.

    Uses cosine similarity (via Inner Product on normalised embeddings)
    for reliable 0-1 scoring.
    """

    def __init__(
        self,
        model_name: str = "paraphrase-multilingual-MiniLM-L12-v2",
        index_path: str = "data/query_cache.faiss",
        metadata_path: str = "data/query_metadata.json",
    ):
        if not HAS_SENTENCE_TRANSFORMERS or not HAS_FAISS:
            raise RuntimeError(
                "sentence-transformers / faiss not installed; similarity disabled"
            )

        self.model = SentenceTransformer(model_name)
        self.index = None
        self.query_cache: Dict = {}
        self.embeddings: list = []
        self.queries: list = []
        self.index_path = index_path
        self.metadata_path = metadata_path

        Path("data").mkdir(exist_ok=True)
        self._load_from_disk()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load_from_disk(self) -> None:
        """Load metadata and *always* rebuild the FAISS index to guarantee
        consistency (avoids stale / corrupted index files)."""
        try:
            if os.path.exists(self.metadata_path):
                with open(self.metadata_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                    self.queries = data.get("queries", [])
                    self.query_cache = data.get("query_cache", {})

                # De-duplicate queries (same normalised form → keep latest)
                self._deduplicate_queries()

                # Always rebuild the FAISS index from stored queries
                self._rebuild_index()
                logger.info(
                    "[OK] Loaded & rebuilt index for %d cached queries",
                    len(self.queries),
                )
            else:
                logger.info("No existing query cache found – will create new one")
        except Exception as exc:
            logger.warning("Failed to load query cache: %s", exc)
            self.index = None
            self.queries = []
            self.query_cache = {}

    def _rebuild_index(self) -> None:
        """Re-embed every stored query and build a fresh FAISS IP index."""
        if not self.queries:
            self.index = None
            return

        texts = [q.get("normalized_query", q["natural_query"]) for q in self.queries]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        embeddings = np.asarray(embeddings, dtype="float32")

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)   # Inner-Product = cosine for unit vecs
        self.index.add(embeddings)
        self.embeddings = list(embeddings)

    def _deduplicate_queries(self) -> None:
        """Keep only the latest entry per normalised query form."""
        seen: Dict[str, int] = {}
        unique: list = []
        for q in self.queries:
            key = q.get("normalized_query", q["natural_query"]).strip().lower()
            if key in seen:
                # Replace earlier entry with the more recent one
                unique[seen[key]] = q
            else:
                seen[key] = len(unique)
                unique.append(q)
        if len(unique) < len(self.queries):
            logger.info(
                "[DEDUP] Reduced cache from %d → %d entries",
                len(self.queries),
                len(unique),
            )
        self.queries = unique

    def _save_to_disk(self) -> None:
        try:
            if self.index is not None:
                faiss.write_index(self.index, self.index_path)
                metadata = {
                    "queries": self.queries,
                    "query_cache": self.query_cache,
                    "last_updated": datetime.now().isoformat(),
                }
                with open(self.metadata_path, "w", encoding="utf-8") as fh:
                    json.dump(metadata, fh, indent=2, ensure_ascii=False)
                logger.debug("[SAVE] Saved %d queries to disk", len(self.queries))
        except Exception as exc:
            logger.error("Failed to save query cache: %s", exc)

    # ------------------------------------------------------------------
    # Normalisation
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_for_embedding(query: str) -> str:
        """Replace numbers with ``<NUM>`` so numeric-only differences still match."""
        return re.sub(r"\d+(?:\.\d+)?", "<NUM>", query)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def add_query(self, query: str, sql: str, result_metadata: Dict) -> None:
        """Add a successful query to the index and persist.

        Skips duplicates (same normalised form already cached).
        """
        normalized = self._normalize_for_embedding(query)
        norm_key = normalized.strip().lower()

        # Skip if already cached (de-dup)
        for existing in self.queries:
            if existing.get("normalized_query", "").strip().lower() == norm_key:
                # Update SQL/metadata for existing entry instead of adding duplicate
                existing["sql_query"] = sql
                existing["metadata"] = result_metadata
                existing["timestamp"] = datetime.now().isoformat()
                self.query_cache[query] = {"sql": sql, "metadata": result_metadata}
                self._save_to_disk()
                logger.debug("[DEDUP] Updated existing cache entry for: %s", query[:60])
                return

        embedding = self.model.encode([normalized], normalize_embeddings=True)

        if self.index is None:
            dimension = embedding.shape[1]
            self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embedding)
        self.embeddings.append(embedding[0])
        self.queries.append(
            {
                "natural_query": query,
                "normalized_query": normalized,
                "sql_query": sql,
                "metadata": result_metadata,
                "timestamp": datetime.now().isoformat(),
            }
        )
        self.query_cache[query] = {"sql": sql, "metadata": result_metadata}
        self._save_to_disk()

    def find_similar(
        self, query: str, k: int = 5, threshold: float = 0.85
    ) -> List[Dict]:
        """Find similar cached queries above *threshold* (cosine similarity 0-1)."""
        if self.index is None or len(self.queries) == 0:
            return []

        normalized = self._normalize_for_embedding(query)
        logger.debug("[FIND] Searching with normalized query: %s", normalized)

        embedding = self.model.encode([normalized], normalize_embeddings=True)
        scores, indices = self.index.search(embedding, min(k, len(self.queries)))

        results: List[Dict] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue  # FAISS returns -1 for empty slots
            similarity = float(max(0.0, min(1.0, score)))  # clamp to [0,1]
            logger.debug(
                "score=%.4f  similarity=%.4f  threshold=%.4f",
                score,
                similarity,
                threshold,
            )
            if similarity >= threshold:
                results.append(
                    {
                        "query": self.queries[idx],
                        "similarity": similarity,
                        "distance": float(1 - similarity),
                    }
                )
                logger.info(
                    "[MATCH] %s (%.1f%%)",
                    self.queries[idx]["natural_query"][:50],
                    similarity * 100,
                )

        if not results:
            best = float(max(0, scores[0][0])) if len(scores[0]) else 0
            logger.info(
                "[NO-MATCH] No matches above %d%% (best: %.1f%%)",
                int(threshold * 100),
                best * 100,
            )
        return results

    # ------------------------------------------------------------------
    # Entity swapping
    # ------------------------------------------------------------------

    def swap_entities(
        self, original_query: str, new_query: str, original_sql: str
    ) -> Dict:
        """Smart entity swapping between an original cached query and a new query.

        Returns dict with keys:
            adapted_sql, swapped, structural_change, message
        """
        orig_lower = original_query.lower()
        new_lower = new_query.lower()
        sql_upper = original_sql.upper()

        # Detect structural differences
        struct_kw_orig = set(
            re.findall(
                r"\b(show|display|get|select|list|find|count|sum|avg|max|min"
                r"|group by|order by|limit|join)\b",
                orig_lower,
            )
        )
        struct_kw_new = set(
            re.findall(
                r"\b(show|display|get|select|list|find|count|sum|avg|max|min"
                r"|group by|order by|limit|join)\b",
                new_lower,
            )
        )

        col_pattern = (
            r"\b(name|age|salary|department|email|phone|id|hire_date|experience)\b"
        )
        orig_cols = set(re.findall(col_pattern, orig_lower))
        new_cols = set(re.findall(col_pattern, new_lower))
        has_column_change = orig_cols != new_cols and len(new_cols) > 0
        has_agg_change = bool(struct_kw_orig - struct_kw_new or struct_kw_new - struct_kw_orig)

        # --- NEW: detect filter / comparison additions ---
        filter_pattern = (
            r"\b(more than|less than|greater than|greater|less|equal to|equals?"
            r"|between|above|below|at least|at most|not equal"
            r"|higher than|lower than|over|under|exceeds?|where|having)\b"
        )
        orig_filters = set(re.findall(filter_pattern, orig_lower))
        new_filters = set(re.findall(filter_pattern, new_lower))
        added_filters = new_filters - orig_filters

        # If the new query adds filter conditions but the cached SQL has
        # no WHERE / HAVING clause, entity-swapping cannot help – the SQL
        # structure itself needs to change.
        has_filter_addition = (
            bool(added_filters)
            and "WHERE" not in sql_upper
            and "HAVING" not in sql_upper
        )
        if has_filter_addition:
            logger.info(
                "[STRUCT] Filter addition detected: new filters %s, "
                "original SQL has no WHERE",
                added_filters,
            )

        structural_change = has_column_change or has_agg_change or has_filter_addition

        # Extract numbers & strings
        orig_nums = re.findall(r"(\d+(?:\.\d+)?)", original_query)
        new_nums = re.findall(r"(\d+(?:\.\d+)?)", new_query)
        orig_strs = [
            s[0] or s[1]
            for s in re.findall(r"'([^']*)'|\"([^\"]*)\"", original_query)
        ]
        new_strs = [
            s[0] or s[1]
            for s in re.findall(r"'([^']*)'|\"([^\"]*)\"", new_query)
        ]

        adapted_sql = original_sql
        swapped = False

        # Swap numbers
        if orig_nums and new_nums:
            for o, n in zip(orig_nums, new_nums):
                if o != n:
                    new_sql = re.sub(r"\b" + re.escape(o) + r"\b", n, adapted_sql, count=1)
                    if new_sql == adapted_sql:
                        new_sql = re.sub(re.escape(o), n, adapted_sql, count=1)
                    adapted_sql = new_sql
                    swapped = True
                    logger.info("[SWAP] %s -> %s", o, n)

        # Swap strings
        if orig_strs and new_strs:
            for o, n in zip(orig_strs, new_strs):
                if o != n:
                    adapted_sql = adapted_sql.replace(f"'{o}'", f"'{n}'")
                    adapted_sql = adapted_sql.replace(f'"{o}"', f'"{n}"')
                    adapted_sql = adapted_sql.replace(
                        f"UPPER('{o}')", f"UPPER('{n}')"
                    )
                    swapped = True
                    logger.info("[SWAP] '%s' -> '%s'", o, n)

        if structural_change:
            message = "[WARN] Structural change detected – recommend generating new SQL"
        elif swapped:
            message = "[OK] Entities swapped successfully"
        else:
            message = "No entities to swap"

        return {
            "adapted_sql": adapted_sql,
            "swapped": swapped,
            "structural_change": structural_change,
            "message": message,
        }

    # ------------------------------------------------------------------
    # Cache management helpers
    # ------------------------------------------------------------------

    def clear_cache(self) -> None:
        """Wipe the in-memory cache and delete persisted files."""
        self.index = None
        self.queries = []
        self.query_cache = {}
        self.embeddings = []
        for path in (self.index_path, self.metadata_path):
            if os.path.exists(path):
                os.remove(path)
        logger.info("Similarity cache cleared")

    def get_cache_stats(self) -> Dict:
        """Return basic statistics about the cache."""
        return {
            "total_queries": len(self.queries),
            "index_exists": self.index is not None,
        }
