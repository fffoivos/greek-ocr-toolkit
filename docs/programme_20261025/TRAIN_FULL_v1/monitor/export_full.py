#!/usr/bin/env python3
"""Read-only Stage C dashboard snapshot; standalone Python 3.6 stdlib only.

Input files are opened only in read mode. Temporary files and replacements are
confined to --out, which must be outside --runs. No sealed-package imports.
"""
import argparse
import csv
import datetime
import json
import os
from pathlib import Path
import re
import tempfile
import time


TOTAL_DRAWN_LINES = 12691632
PANELS = ('harvest_dev', 'seal04_dev', 'harvest_test', 'seal04_test')
LOSS_FIELDS = ('run', 'width', 'step', 'drawn_lines', 'train_loss_at_step',
               'harvest_dev_loss', 'seal04_dev_loss', 'harvest_test_loss',
               'seal04_test_loss', 'checkpoint_sha256')
CER_FIELDS = ('run', 'width', 'step', 'drawn_lines', 'instrument', 'nfd_atom_cer',
              'nfc_char_cer', 'diacritic_insensitive_cer', 'exact_line_rate', 'rows')
STATUS_FIELDS = ('run', 'width', 'total_drawn_lines', 'total_updates', 'latest_step',
                 'latest_drawn_lines', 'pct_complete', 'loss_points_done',
                 'loss_points_total', 'cer_evals_done', 'epoch_rows', 'last_epoch',
                 'val_cer', 'complete', 'last_update_utc', 'segment_count',
                 'yield_count', 'segment_trace_rows')


def read_json(path):
    """Reopen once after a torn/replaced JSON file; otherwise skip it."""
    for attempt in range(2):
        try:
            with path.open('r', encoding='utf-8') as stream:
                value = json.load(stream)
                mtime = os.fstat(stream.fileno()).st_mtime
            if isinstance(value, dict):
                return value, mtime
            return {}, None
        except FileNotFoundError:
            return {}, None
        except (OSError, ValueError, UnicodeError):
            if attempt == 0:
                time.sleep(0.01)
    return {}, None


def journal(path):
    """Only newline-terminated records are committed JSONL points."""
    try:
        with path.open('rb') as stream:
            mtime = os.fstat(stream.fileno()).st_mtime
            for line in stream:
                if not line.endswith(b'\n'):
                    break
                try:
                    value = json.loads(line.decode('utf-8'))
                except (ValueError, UnicodeError):
                    continue
                if isinstance(value, dict):
                    yield value, mtime
    except OSError:
        return


def files(folder, pattern):
    try:
        return sorted(folder.glob(pattern))
    except OSError:
        return []


def step_of(value):
    step = value.get('step')
    return step if isinstance(step, int) and not isinstance(step, bool) and step >= 0 else None


def named_width(name):
    match = re.match(r'^w(1(?:\.0)?|1\.5|2(?:\.0)?)-(?:full|control|requeue)$', name)
    return float(match.group(1)) if match else None


def run_configs(runs):
    """Discover pending runs too; rebase copied PLAN references locally."""
    plan, _ = read_json(runs.parent / 'PLAN.json')
    entries = {e['name']: e for e in plan.get('runs', [])
               if isinstance(e, dict) and named_width(e.get('name', '')) is not None}
    names = set(entries)
    names.update(p.name for p in files(runs, '*') if p.is_dir() and named_width(p.name) is not None)
    names.update(p.stem for p in files(runs.parent / 'configs', '*.json')
                 if named_width(p.stem) is not None)
    result = []
    for name in sorted(names, key=lambda n: (named_width(n), n)):
        entry = entries.get(name, {})
        config, _ = read_json(runs.parent / 'configs' / (name + '.json'))
        if not config:
            config, _ = read_json(runs / name / 'config.json')
        # Stage C config references are specs; only read a local configs file,
        # never an absolute remote path retained in a copied smoke tree.
        if not config and isinstance(entry.get('config'), dict):
            config, _ = read_json(runs.parent / 'configs' / Path(entry['config']['path']).name)
        result.append((name, config))
    return result


def loss_records(folder):
    points = {}
    for value, mtime in journal(folder / 'loss_eval.jsonl'):
        step = step_of(value)
        if step is not None and isinstance(value.get('instruments'), dict):
            points[step] = (value, mtime)
    # The atomic per-point file can precede the journal append. Prefer it and
    # its own mtime; journal rows remain usable if a file is temporarily torn.
    for path in files(folder / 'loss_eval', 'step-*.json'):
        value, mtime = read_json(path)
        step = step_of(value)
        if step is not None and isinstance(value.get('instruments'), dict):
            points[step] = (value, mtime)
    return points


def epochs(folder):
    result = []
    try:
        with (folder / 'train_log.csv').open('r', encoding='utf-8', newline='') as stream:
            # Ignore a concurrently appended partial epoch row.
            lines = (line for line in stream if line.endswith('\n'))
            for row in csv.DictReader(lines):
                if row.get('epoch') and row.get('step') and row.get('val_cer'):
                    result.append(row)
    except (OSError, UnicodeError, csv.Error):
        pass
    return result


def pooled_dev(instruments):
    """Stage B objective: sum NFD-atom edits / sum reference units."""
    try:
        panels = [instruments[name] for name in ('harvest_dev', 'seal04_dev')]
        scores = [p['score']['cer']['nfd_atom'] for p in panels]
        units = sum(s['reference_units'] for s in scores)
        if units <= 0:
            return None
        return {'nfd_atom_cer': sum(s['edits'] for s in scores) / units,
                'rows': sum(p['rows'] for p in panels)}
    except (KeyError, TypeError):
        return None


def snapshot_run(runs, name, config):
    folder = runs / name
    width = named_width(name)
    base = {'run': name, 'width': width}
    cadence, _ = read_json(folder / 'LOSS_CADENCE.json')
    live, _ = read_json(folder / 'LIVE.json')
    trace, _ = read_json(folder / 'SEGMENT_TRACE.json')
    losses = loss_records(folder)
    epoch_log = epochs(folder)
    draws = {p['step']: p['drawn_lines'] for p in cadence.get('points', [])
             if step_of(p) is not None and p.get('drawn_lines') is not None}
    for step, (value, _) in losses.items():
        if value.get('drawn_lines') is not None:
            draws[step] = value['drawn_lines']
    if step_of(live) is not None and live.get('drawn_lines') is not None:
        draws[live['step']] = live['drawn_lines']
    trace_step = trace.get('global_step')
    if isinstance(trace_step, int) and trace.get('draw_position') is not None:
        draws[trace_step] = trace['draw_position']

    loss_rows = []
    for step, (value, _) in sorted(losses.items()):
        row = dict(base, step=step, drawn_lines=value.get('drawn_lines', draws.get(step)),
                   train_loss_at_step=value.get('train_loss_at_step'),
                   checkpoint_sha256=value.get('checkpoint', {}).get('sha256'))
        for panel in PANELS:
            row[panel + '_loss'] = value['instruments'].get(panel, {}).get('ctc_loss')
        loss_rows.append(row)

    cer_rows, cer_steps = [], set()
    for path in files(folder / 'eval', 'step-*.json'):
        value, _ = read_json(path)
        step = step_of(value)
        instruments = value.get('instruments')
        if step is None or not isinstance(instruments, dict) or not instruments:
            continue
        cer_steps.add(step)
        common = dict(base, step=step, drawn_lines=draws.get(step))
        for panel in sorted(instruments):
            instrument = instruments[panel]
            score = instrument.get('score', {})
            metrics = score.get('cer', {})
            cer_rows.append(dict(common, instrument=panel, rows=instrument.get('rows'),
                nfd_atom_cer=metrics.get('nfd_atom', {}).get('rate'),
                nfc_char_cer=metrics.get('nfc_char', {}).get('rate'),
                diacritic_insensitive_cer=metrics.get('diacritic_insensitive', {}).get('rate'),
                exact_line_rate=score.get('exact_line_rate')))
        pool = pooled_dev(instruments)
        if pool is not None:
            cer_rows.append(dict(common, instrument='pooled_dev', **pool))
    cer_rows.sort(key=lambda row: (row['step'], row['instrument']))

    # Fallbacks mirror the full PLAN: eight epochs, epoch_rows=2*real,
    # adopted batch sizes 256/256/64. Smoke/config/cadence override these.
    parameters = config.get('parameters', {})
    total_draws = cadence.get('total_drawn_lines', config.get('target_drawn_lines', TOTAL_DRAWN_LINES))
    batch_size = parameters.get('bs', 64 if width == 2.0 else 256)
    epoch_count = parameters.get('epochs', 8)
    epoch_size = parameters.get('epoch_rows', TOTAL_DRAWN_LINES // 8)
    total_updates = cadence.get('total_updates', config.get('total_updates',
        epoch_count * ((epoch_size + batch_size - 1) // batch_size)))
    every = config.get('loss_every_drawn_lines', 50000)
    loss_total = cadence.get('count', (total_draws + every - 1) // every)
    observed_steps = set(losses) | cer_steps
    if step_of(live) is not None:
        observed_steps.add(live['step'])
    if isinstance(trace_step, int):
        observed_steps.add(trace_step)
    for row in epoch_log:
        try:
            observed_steps.add(int(row['step']))
        except ValueError:
            pass
    latest_step = max(observed_steps) if observed_steps else 0
    latest_draws = draws.get(latest_step, 0 if latest_step == 0 else None)
    mtimes = [mtime for _, mtime in losses.values() if mtime is not None]
    last_update = (datetime.datetime.fromtimestamp(max(mtimes), datetime.timezone.utc)
                   .isoformat().replace('+00:00', 'Z')) if mtimes else None
    status = dict(base, total_drawn_lines=total_draws, total_updates=total_updates,
        latest_step=latest_step, latest_drawn_lines=latest_draws,
        pct_complete=100.0 * latest_draws / total_draws if latest_draws is not None and total_draws else None,
        loss_points_done=len(losses), loss_points_total=loss_total,
        cer_evals_done=len(cer_steps), epoch_rows=len(epoch_log),
        last_epoch=epoch_log[-1]['epoch'] if epoch_log else None,
        val_cer=epoch_log[-1]['val_cer'] if epoch_log else None,
        complete='true' if (folder / 'COMPLETE.json').is_file() else 'false',
        last_update_utc=last_update, segment_count=len(files(folder, 'STARTUP_*.json')),
        yield_count=len(files(folder, 'YIELD_*.json')),
        segment_trace_rows=len(trace['trace']) if isinstance(trace.get('trace'), list) else None)
    return loss_rows, cer_rows, status


def write_csv(path, fields, rows):
    """Replace a complete CSV atomically on the output filesystem."""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='',
                dir=str(path.parent), prefix='.' + path.name + '.', suffix='.tmp', delete=False) as stream:
            temporary = stream.name
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, str(path))
    finally:
        if temporary is not None and os.path.exists(temporary):
            os.unlink(temporary)


def export(runs, out):
    runs, out = Path(runs).resolve(), Path(out).resolve()
    if out == runs or runs in out.parents:
        raise ValueError('--out must be outside --runs (including symlink targets)')
    if not runs.is_dir() and not (runs.parent / 'PLAN.json').is_file() and not (runs.parent / 'configs').is_dir():
        raise ValueError('--runs does not exist and no sibling PLAN.json/configs are available')
    configs = run_configs(runs)
    # A run subdirectory itself can be a symlink outside the container.
    for name, _ in configs:
        source = (runs / name).resolve()
        if out == source or source in out.parents:
            raise ValueError('--out must be outside --runs and every resolved run directory')
    loss_rows, cer_rows, status_rows = [], [], []
    for name, config in configs:
        loss, cer, status = snapshot_run(runs, name, config)
        loss_rows.extend(loss)
        cer_rows.extend(cer)
        status_rows.append(status)
    out.mkdir(parents=True, exist_ok=True)
    write_csv(out / 'full_loss.csv', LOSS_FIELDS, loss_rows)
    write_csv(out / 'full_cer.csv', CER_FIELDS, cer_rows)
    write_csv(out / 'full_status.csv', STATUS_FIELDS, status_rows)
    return len(loss_rows), len(cer_rows), len(status_rows)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runs', required=True, help='directory containing Stage C run subdirectories')
    parser.add_argument('--out', required=True, help='CSV output directory outside --runs')
    args = parser.parse_args(argv)
    try:
        counts = export(args.runs, args.out)
    except (OSError, ValueError) as error:
        parser.exit(1, 'export_full: %s\n' % error)
    print('Exported %d loss rows, %d CER rows, %d status rows.' % counts)
    return 0


if __name__ == '__main__':
    main()
