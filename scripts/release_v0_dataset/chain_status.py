"""Private durable progress for the login-node chain; no input hashing on login nodes."""
import argparse
import json
import os
import sqlite3
from pathlib import Path
from .common import atomic_json, digest, canonical


def write_status(builder, status):
    db = builder.store.db
    # A forward-only vector: committed row cursors + stage completions + closed shards.
    state = dict(done=db.execute('SELECT stage FROM done ORDER BY stage').fetchall(),
                 ingest=db.execute('SELECT stage,ordinal FROM ingest_cursor ORDER BY stage').fetchall(),
                 units=db.execute('SELECT stage,ordinal FROM resume_units ORDER BY stage').fetchall(),
                 original=[])
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='original_payload_cursor'").fetchone():
        state['original'] = db.execute('SELECT source,path,ordinal,done FROM original_payload_cursor ORDER BY source,path').fetchall()
    if db.execute("SELECT 1 FROM sqlite_master WHERE name='finish_steps'").fetchone():
        state['finishing'] = db.execute('SELECT stage FROM finish_steps ORDER BY stage').fetchall()
    state['shards'] = [(p.name, json.loads(p.read_text()).get('rows')) for p in sorted((builder.work / 'batches').glob('*.json'))]
    ledger = builder.work / 'readback/accept.sqlite'
    if ledger.exists():
        with sqlite3.connect(f'file:{ledger}?mode=ro', uri=True) as readback:
            state['readback'] = readback.execute('SELECT k,j FROM readback_units ORDER BY k').fetchall()
            if readback.execute("SELECT 1 FROM sqlite_master WHERE name='original_payload_cursor'").fetchone():
                state['readback_original'] = readback.execute('SELECT * FROM original_payload_cursor ORDER BY source,path').fetchall()
    final = (builder.work / 'FINAL.json').is_file() and (
        not getattr(builder, 'require_readback', False) or (builder.work / 'READBACK.json').is_file())
    atomic_json(builder.work / 'RUN_STATUS.json', dict(status=status, job_id=os.environ.get('SLURM_JOB_ID'), binding=builder.binding,
                progress=digest(canonical(state)), final=final))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('work', type=Path)
    p.add_argument('--job-id')
    a = p.parse_args()
    value = json.loads((a.work / 'RUN_STATUS.json').read_text())
    if a.job_id and value.get('job_id') != a.job_id:
        raise SystemExit('stale RUN_STATUS job id')
    print(value['status'], value.get('progress') or 'none', int(value.get('final', False)))


if __name__ == '__main__':
    main()
