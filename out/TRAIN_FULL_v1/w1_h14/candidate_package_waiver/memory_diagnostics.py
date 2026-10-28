"""Read-only Linux job-cgroup + aggregate lane-tree PSS diagnostics.

Unavailable/racing counters are recorded, never invented or used to alter training.
A smoke readout reports actual counters, including unlimited limits and
unavailable measurements explicitly; diagnostics never select/stop a model.
"""
import os
from pathlib import Path
import re
import threading
import time
from common import atomic


def cgroups(proc=Path('/proc'), job_id=None):
    memberships = [r.split(':', 2) for r in (proc/'self/cgroup').read_text().splitlines()]
    mounts = [r.split() for r in (proc/'self/mountinfo').read_text().splitlines()]
    found = []
    for fields in mounts:
        sep = fields.index('-')
        fs, options = fields[sep+1], fields[sep+3]
        if fs not in ('cgroup2', 'cgroup') or (fs == 'cgroup' and 'memory' not in options.split(',')):
            continue
        member = next((r[2] for r in memberships if
            (fs == 'cgroup2' and r[0] == '0') or (fs == 'cgroup' and 'memory' in r[1].split(','))), None)
        if member is None:
            continue
        root, mount = Path(fields[3]), Path(fields[4])
        try:
            current = mount / Path(member).relative_to(root)
        except ValueError:
            continue
        while current == mount or mount in current.parents:
            is_job = bool(job_id and re.search(r'(?:^|[_.-])job[_-]'+re.escape(str(job_id))+r'(?:[_.-]|$)', current.name))
            found.append((current, fs, is_job))
            if current == mount:
                break
            current = current.parent
    return found


def read_cgroup(path, version, is_job=False):
    result = dict(path=str(path), version=version, job_scope=is_job)
    files = ('memory.peak', 'memory.max', 'memory.current', 'memory.events') if version == 'cgroup2' else (
        'memory.max_usage_in_bytes', 'memory.limit_in_bytes', 'memory.usage_in_bytes',
        'memory.failcnt', 'memory.oom_control')
    result['raw'], result['errors'] = {}, {}
    for name in files:
        try:
            result['raw'][name] = (path/name).read_text().strip()
        except OSError as e:
            result['errors'][name] = str(e)
    raw = result['raw']
    if version == 'cgroup2':
        for name in ('peak', 'max', 'current'):
            value = raw.get('memory.'+name)
            result[name+'_bytes'] = int(value) if value and value.isdigit() else value
        result['events'] = {k:int(v) for k,v in (r.split() for r in raw.get('memory.events','').splitlines())}
    else:
        for name, key in [('peak','max_usage_in_bytes'), ('max','limit_in_bytes'), ('current','usage_in_bytes')]:
            value = raw.get('memory.'+key)
            result[name+'_bytes'] = int(value) if value and value.isdigit() else None
        result['events'] = {k:int(v) for k,v in (r.split() for r in raw.get('memory.oom_control','').splitlines())}
        result['failcnt'] = raw.get('memory.failcnt')
    return result


def tree_pss(pid, proc=Path('/proc')):
    todo, seen, records, errors = [pid], set(), [], []
    while todo:
        current = todo.pop()
        if current in seen:
            continue
        seen.add(current)
        try:
            children = (proc/str(current)/'task'/str(current)/'children').read_text().split()
            todo.extend(map(int,children))
            values = (proc/str(current)/'smaps_rollup').read_text().splitlines()
            pss = next(int(r.split()[1])*1024 for r in values if r.startswith('Pss:'))
            records.append(dict(pid=current, pss_bytes=pss))
        except (OSError, StopIteration, ValueError) as e:
            errors.append(dict(pid=current,error=str(e)))
    return dict(root_pid=pid, processes=records, pss_bytes=sum(r['pss_bytes'] for r in records), errors=errors)


class MemoryMonitor:
    def __init__(self, output, allocation, *, interval=30., proc=Path('/proc')):
        self.output, self.allocation, self.proc = Path(output), dict(allocation), proc
        self.interval, self.samples, self.errors = interval, [], []
        self.lock, self.stop = threading.Lock(), threading.Event()
        self.thread = None
        self.path = self.output/('MEMORY_%s_%s_%d.json' %
            (allocation['job_id'], allocation['restart_count'], time.time_ns()))

    def sample(self, reason):
        with self.lock:
            item = dict(reason=reason, unix=time.time(), tree=tree_pss(os.getpid(),self.proc), cgroups=[])
            try:
                item['cgroups'] = [read_cgroup(*c) for c in cgroups(self.proc,self.allocation['job_id'])]
            except (OSError, ValueError) as e:
                item['cgroup_error'] = str(e)
            self.samples.append(item)
            atomic(self.path, dict(schema='TRAIN_FULL-memory-v1',allocation=self.allocation,
                samples=self.samples, note='PSS sum over live lane descendants; job counters shared across batch/step cgroups; unavailable counters explicit'))

    def start(self):
        self.sample('start')
        def loop():
            while not self.stop.wait(self.interval):
                try:
                    self.sample('periodic')
                except Exception as e:
                    self.errors.append(repr(e))
        self.thread = threading.Thread(target=loop,daemon=True)
        self.thread.start()

    def close(self):
        self.stop.set()
        if self.thread:
            self.thread.join()
        self.sample('end')
        if self.errors:
            data = __import__('json').loads(self.path.read_text())
            data['monitor_errors'] = self.errors
            atomic(self.path,data)
        return self.path


def summarize(paths):
    from common import bound, read, spec
    reports = [read(bound(s)) for s in paths]
    samples = [s for r in reports for s in r['samples']]
    jobs = [g for s in samples for g in s['cgroups'] if g['job_scope']]
    complete = [s for s in samples if s['tree']['processes'] and not s['tree']['errors']]
    peaks = [g['peak_bytes'] for g in jobs if isinstance(g.get('peak_bytes'),int)]
    limits = [g['max_bytes'] for g in jobs if isinstance(g.get('max_bytes'),int)]
    problems = [r.get('monitor_errors',[]) for r in reports if r.get('monitor_errors')]
    if not jobs:
        problems.append('job scope not visible in cgroup hierarchy')
    if not complete:
        problems.append('no complete process-tree PSS sample')
    if any(g['errors'] or 'oom_kill' not in g['events'] for g in jobs):
        problems.append('some job counters unavailable; inspect raw receipts')
    if not any(s['reason']=='end' for s in samples):
        problems.append('end sample unavailable')
    peak = max(peaks) if peaks else None
    limit = min(limits) if limits else None
    events = {k:max((g['events'][k] for g in jobs if k in g['events']),default=None)
              for k in ('oom','oom_kill')}
    return dict(receipts=paths, capture_status='PARTIAL' if problems else 'COMPLETE',
        diagnostic_problems=problems, job_peak_bytes=peak, job_limit_bytes=limit,
        job_limits_observed=sorted({str(g.get('max_bytes')) for g in jobs}),
        job_headroom_bytes=limit-peak if peak is not None and limit is not None else None,
        events_max=events, aggregate_pss_bytes_max=max((s['tree']['pss_bytes'] for s in complete),default=None),
        complete_pss_samples=len(complete), total_samples=len(samples),
        capacity_qualified=False, limitation='short smoke only; full-size epoch/long-lived loader headroom remains unmeasured; unlimited/inaccessible limits do not prove enforcement')
