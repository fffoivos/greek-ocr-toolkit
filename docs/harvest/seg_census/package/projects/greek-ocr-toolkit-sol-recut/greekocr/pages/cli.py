"""Directory entry point; image inputs and layout regions are explicit."""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from .api import process_book, process_page
from .layout import read_layout
from .options import GEOMETRY_OUTPUTS, OUTPUT_NAMES, OutputOptions, PageOptions


def add_parser(commands):
    parser = commands.add_parser('pages', help='analyse a directory of page images')
    parser.add_argument('directory', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--tables', action='store_true', help='use supplied or local Docling image layout')
    parser.add_argument('--layout', type=Path, help='directory of PAGE.json layout records')
    parser.add_argument('--orientation', action='store_true', help='parked experimental orientation')
    parser.add_argument('--join-lines', action='store_true')
    parser.add_argument('--granularity', choices=('default', 'rows', 'pieces'), default='default')
    parser.add_argument('--statistics', action='store_true')
    parser.add_argument('--discounted', choices=('keep', 'drop'), default='keep')
    parser.add_argument('--strict-geometry', action='store_true', help='reject invalid active line ribbons')
    parser.add_argument('--outputs', nargs='+', choices=sorted(OUTPUT_NAMES), default=None)
    parser.add_argument('--book-id', help='treat this directory as one book; enables book aggregation')
    parser.add_argument('--page-size', nargs=2, type=float, metavar=('WIDTH', 'HEIGHT'))


def run(args):
    if not args.directory.is_dir():
        raise ValueError(f'Image directory does not exist: {args.directory}')
    paths = sorted(p for p in args.directory.iterdir() if p.is_file() and p.suffix.lower() in ('.png', '.jpg', '.jpeg', '.tif', '.tiff'))
    if not paths:
        raise ValueError('No supported page images in directory')
    if len({p.stem for p in paths}) != len(paths):
        raise ValueError('Duplicate filename stems would overwrite outputs')
    if args.layout is not None and not args.tables:
        raise ValueError('--layout requires --tables')
    files = frozenset(args.outputs) if args.outputs is not None else GEOMETRY_OUTPUTS | (
        {'statistics'} if args.statistics else set()) | ({'delivery'} if args.join_lines else set()) | (
        {'orientation'} if args.orientation else set()) | (
        {'rows'} if args.join_lines and args.granularity == 'rows' else set())
    options = PageOptions(tables=args.tables, orientation=args.orientation, join_lines=args.join_lines,
                          granularity=args.granularity, statistics=args.statistics, discounted=args.discounted,
                          strict_geometry=args.strict_geometry,
                          outputs=OutputOptions(args.out, files))
    regions = None
    if args.layout is not None:
        regions = {}
        for path in paths:
            with Image.open(path) as im:
                regions[path.stem] = read_layout(args.layout / f'{path.stem}.json', im.size)
    if args.book_id:
        result = process_book(paths, book_id=args.book_id, options=options, table_regions=regions,
                              page_size=args.page_size)
        return dict(pages=len(result.pages), book_id=result.book_id, files=result.files,
                    page_files={p.page_key: p.files for p in result.pages},
                    joining={p.page_key: dict(complete=p.complete, blocked_rows=p.blocked_rows)
                             for p in result.pages} if args.join_lines else None)
    completed = []
    for path in paths:
        result = process_page(path, options=options, table_regions=regions[path.stem] if regions is not None else None,
                              page_size=args.page_size)
        completed.append(dict(page_key=result.page_key, lines=len(result.lines), pieces=len(result.pieces),
                              files=result.files, complete=result.complete, blocked_rows=result.blocked_rows))
    return dict(pages=len(completed), results=completed)
