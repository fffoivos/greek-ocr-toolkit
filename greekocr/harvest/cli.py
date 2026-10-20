"""Explicit Anemi-only H1 pilot command."""
from pathlib import Path
from .pipeline import DEFAULT_SOURCE

def add_parser(commands):
    p = commands.add_parser('harvest', help='internal Anemi sample; ≤500 lines, ≤1000 Google calls')
    sub = p.add_subparsers(dest='harvest_command', required=True)
    p = sub.add_parser('pilot')
    p.add_argument('--stage', choices=('prepare','sample','label','report','all'), default='all')
    p.add_argument('--out', type=Path, default=Path('docs/records/harvest/pilot_v1'))
    p.add_argument('--big', type=Path, default=Path('docs/harvest/harvest_big/t13c'))
    p.add_argument('--stack-export', type=Path, default=Path('docs/harvest/pilot/_stack_52cee3b'))
    p.add_argument('--source-repo', type=Path, default=DEFAULT_SOURCE)
    p.add_argument('--anemi', type=Path, default=Path('docs/harvest/harvest_big/anemi_wave3_sample_t13c'))
    p.add_argument('--proposal', type=Path, default=DEFAULT_SOURCE/'docs/evidence/o4c/anemi_wave3_proposal.json')
    p.add_argument('--max-new-pages', type=int)
    p.add_argument('--sample-max', type=int, default=500)
    p.add_argument('--cap-usd', type=float, default=3)

def run(a):
    from .pipeline import prepare, sample, label
    if not 0 < a.cap_usd <= 3: raise ValueError('cap must be >0 and <=3 USD')
    if not 1 <= a.sample_max <= 500: raise ValueError('sample-max must be 1..500')
    if a.stage in ('prepare','all'): prepare(a.out,a.big,a.stack_export,a.source_repo,a.anemi,a.max_new_pages,a.proposal)
    if a.stage in ('sample','all'): sample(a.out,a.big,a.sample_max)
    if a.stage in ('label','all'): label(a.out,a.cap_usd)
    if a.stage in ('report','all'):
        from .report import report
        return report(a.out)
    return {'stage':a.stage,'out':str(a.out)}
