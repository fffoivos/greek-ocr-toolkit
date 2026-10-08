"""Recorded source parsers and explicit node discovery/acquisition entry points."""
from .discovery import parse_source, discovery_command, run_discovery, http_client
from .parliament import refetch_pdf_cache, stage_parliament
from .web_render import PageRecord, render_pages, records_from_dom, records_from_pdf, degrade_twins, page_records
from .web_sources import source_catalog, source_pages, mastodon_post_html
__all__ = ['parse_source', 'discovery_command', 'run_discovery', 'http_client', 'refetch_pdf_cache', 'stage_parliament',
           'PageRecord', 'render_pages', 'records_from_dom', 'records_from_pdf', 'degrade_twins', 'page_records',
           'source_catalog', 'source_pages', 'mastodon_post_html']
