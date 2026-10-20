"""Real-line acquisition, reviewed partitioning, extraction and import."""
from .adjudicate import adjudicate_file, adjudicate_lines
from .extract import extract_lines
from .importers import import_dataset, import_real_shards, native_rows
from .partition import DocumentPartition, build_partition, resolve_exclusions
__all__ = ['adjudicate_file', 'adjudicate_lines', 'extract_lines', 'import_dataset', 'import_real_shards',
           'native_rows', 'DocumentPartition', 'build_partition', 'resolve_exclusions']
