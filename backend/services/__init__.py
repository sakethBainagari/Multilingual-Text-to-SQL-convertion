"""Services package – heavy imports (sentence-transformers) are lazy."""


def __getattr__(name):
    """Lazy-load services to avoid importing heavy ML libraries on every access."""
    _map = {
        "DatabaseService": "backend.services.database",
        "SQLGeneratorService": "backend.services.sql_generator",
        "SimilarityService": "backend.services.similarity",
        "VisualizationEngine": "backend.services.visualizer",
        "EntityRecognizer": "backend.services.entity_recognizer",
        "ExportService": "backend.services.export_service",
    }
    if name in _map:
        import importlib
        mod = importlib.import_module(_map[name])
        return getattr(mod, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "DatabaseService",
    "SQLGeneratorService",
    "SimilarityService",
    "VisualizationEngine",
    "EntityRecognizer",
    "ExportService",
]
