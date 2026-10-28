"""Full-state checkpoint/evaluation extension of the byte-bound S1 Segment.

Evaluation restores RNG and model mode; it cannot influence best/patience/schedule.
The segment state is committed BEFORE evaluation. Restart completes a pending eval
before constructing the next training iterator. Completed per-step logs are immutable.
"""
import os
from pathlib import Path
import shutil
import sys
import time

from common import atomic, bound, cadence, read, sha, spec

PANELS = ('seal04_dev', 'seal04_test', 'harvest_dev', 'harvest_test')


def evaluate_panel(model, data, references, codec, device, *, decode=True):
    import torch
    from train.data import ManifestDataset, make_loader
    from train.model import amp_dtype_for, autocast_ctx, masked_forward
    from train.cer import greedy_decode_line
    from bench.score import aggregate
    ds = ManifestDataset(data, codec.version, codec.n_classes - 1, 'reserved')
    loader, sampler = make_loader(ds, 64, shuffle=False)
    criterion = torch.nn.CTCLoss(blank=0, zero_infinity=True)
    loss_sum, n = 0., 0
    predictions, pairs = [], []
    with torch.no_grad():
        model.eval()
        for indices, batch in zip(sampler, loader):
            with autocast_ctx(device, amp_dtype_for(device)):
                output = masked_forward(model, batch['images'].to(device), batch['input_lengths'])
            lp = output.float().cpu()
            loss = criterion(lp.transpose(0, 1), batch['targets'], batch['input_lengths'], batch['target_lengths'])
            if not torch.isfinite(loss):
                raise ValueError('nonfinite checkpoint evaluation loss')
            loss_sum += float(loss) * len(indices)
            n += len(indices)
            if decode:
                ids = lp.argmax(-1)
                for i, index in enumerate(indices):
                    row = data[index]
                    hyp = greedy_decode_line(ids[i, :int(batch['input_lengths'][i])].tolist(), codec)
                    predictions.append(dict(id=row['line_id'], hyp=hyp))
                    pairs.append((dict(text=references[row['line_id']]), hyp))
    if n != len(data) or (decode and len({r['id'] for r in predictions}) != n):
        raise ValueError('incomplete/duplicate eval coverage')
    if not decode:
        return dict(ctc_loss=loss_sum / n, loss_sum_target_normalized=loss_sum, rows=n,
                    loss='same fp32 CPU CTCLoss(blank=0,zero_infinity=True,mean); sample-weighted dataset mean'), []
    return dict(ctc_loss=loss_sum / n, loss_sum_target_normalized=loss_sum, rows=n,
                loss='same fp32 CPU CTCLoss(blank=0,zero_infinity=True,mean); sample-weighted dataset mean',
                score=aggregate(pairs), predictions=predictions,
                scorer='unchanged S1 SEAL02 o1-metrics/v1 aggregate; literal per-codepoint NFD'), predictions


def segment_class(base, runtime, pools, evaluator=evaluate_panel, panels=PANELS):
    class FullSegment(base):
        def __init__(self, args, trainer, model, opt, sched, receipt):
            super().__init__(args, trainer, model, opt, sched, receipt)
            self.last_training_loss = (self.saved['losses'][-1]
                if self.saved and self.saved['losses'] else None)
            self.total = sum(receipt['training_schedule']['epoch_batches'])
            if self.total != args.epochs * ((args.epoch_rows + args.bs - 1) // args.bs):
                raise ValueError('actual S1 sampler horizon differs from sealed packed-tail recipe')
            self.every = args.full_every
            self.loss_points = {p['step']: p for p in args.loss_plan['points']}
            self.timing = dict(samples=0, seconds=0., max_seconds=0.)
            self.timing_path = self.path.parent / ('BATCH_TIMING_%d.json' % time.time_ns())
            self.tick = time.monotonic()
            self.c_first_note = True
            self.timed_epoch = None
            if self.saved:
                # Every crossed point has a pre-eval durable segment. Only that
                # last point can be unfinished; earlier missing records refuse.
                from loss_journal import append_point
                for step in self.loss_points:
                    if step > self.saved['global_step']:
                        continue
                    log = self.path.parent / 'loss_eval' / ('step-%09d.json' % step)
                    if log.exists():
                        prior = read(log)
                        if prior['runtime_sha256'] != runtime['_sha256']:
                            raise ValueError('loss log belongs to another runtime')
                        append_point(self.path.parent / 'loss_eval.jsonl', log)
                    elif step < self.saved['global_step']:
                        raise ValueError('missing historical loss evaluation')
                if self.saved['global_step'] in self.loss_points:
                    self.checkpoint_loss(self.saved['global_step'])
            if (self.saved and (self.saved['global_step'] in args.cer_steps if getattr(args, 'stage_c', False) else cadence(self.saved['global_step'], self.total, self.every))
                    and (self.saved['global_step'] < self.total or self.saved['batch_position'] == 0)):
                self.checkpoint_eval(self.saved['global_step'])
            self.tick = time.monotonic()

        def note(self, epoch, position, indices, rows, loss, step):
            self.last_training_loss = float(loss)
            # Match S1 timing qualification's synchronized measurements in the
            # smoke. Production keeps the original asynchronous execution.
            if self.args.full_smoke and self.t.torch.cuda.is_available():
                self.t.torch.cuda.synchronize(next(self.model.parameters()).device)
            now = time.monotonic()
            if self.timed_epoch == epoch:
                duration = now - self.tick
                self.timing['samples'] += 1
                self.timing['seconds'] += duration
                self.timing['max_seconds'] = max(self.timing['max_seconds'], duration)
            self.timed_epoch = epoch
            self.tick = now
            super().note(epoch, position, indices, rows, loss, step)
            if getattr(self.args, 'stage_c', False) and (self.args.full_smoke or step % self.args.durable_every == 0):
                atomic(self.path.parent / 'LIVE.json', dict(step=step, drawn_lines=self.draws,
                    job_id=os.environ.get('SLURM_JOB_ID'), restart_count=int(os.environ.get('SLURM_RESTART_COUNT', '0'))))
            if getattr(self.args, 'stage_c', False) and self.c_first_note:
                self.c_first_note = False
                started = float(os.environ.get('TF_C_STARTED_UNIX', time.time()))
                atomic(self.path.parent / ('STARTUP_%s_%s.json' % (os.environ.get('SLURM_JOB_ID'),
                    os.environ.get('SLURM_RESTART_COUNT', '0'))), dict(first_step=step,
                    worker_started_unix=started, first_update_unix=time.time(),
                    seconds=time.time()-started, includes='GPU init, data/model setup, cursor recovery, first update'))
            point = self.loss_points.get(step)
            if point and point['drawn_lines'] != self.draws:
                raise ValueError('actual training draws differ from loss cadence plan')

        def full_due(self, step):
            if getattr(self.args, 'stage_c', False):
                return (step in self.loss_points or step in self.args.cer_steps
                        or step - self.last_save >= self.args.durable_every)
            return step in self.loss_points or (step < self.total and step % self.every == 0)

        def stop(self, step):
            if getattr(self.args, 'stage_c', False):
                path = os.environ.get('TF_C_STOP')
                if path and Path(path).exists():
                    self.request_stop()
            return super().stop(step)

        def iterator(self, loader, epoch, cursor):
            if not getattr(self.args, 'stage_c', False) or not cursor:
                return super().iterator(loader, epoch, cursor)
            # PNG decoding is RNG-free (frozen ManifestDataset contract). Skip
            # indices before constructing workers, rather than decoding an
            # already-consumed epoch prefix on every preemption.
            from torch.utils.data import DataLoader
            batches = list(loader.batch_sampler)[cursor:]
            kw = dict(batch_sampler=batches, collate_fn=loader.collate_fn,
                num_workers=loader.num_workers, pin_memory=loader.pin_memory)
            if loader.num_workers:
                kw.update(persistent_workers=True, prefetch_factor=loader.prefetch_factor)
            resumed = DataLoader(loader.dataset, **kw)
            iterator = iter(resumed)
            if self.saved and self.saved['iterator_created']:
                self.restore_rng(self.saved['rng'])
            return iterator

        def save(self, epoch, position, step, *rest):
            started = time.monotonic()
            super().save(epoch, position, step, *rest)
            if getattr(self.args, 'stage_c', False):
                # Include directory publication in durability, and measure
                # cheap checkpoint cost separately from expensive evaluations.
                fd = os.open(self.path.parent, os.O_RDONLY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
                atomic(self.path.parent / 'CHECKPOINT_COST.json', dict(step=step,
                    seconds=time.monotonic()-started, bytes=self.path.stat().st_size))
            if step in self.loss_points:
                self.checkpoint_loss(step)
            # At the final update use the completed-epoch commit (CSV/best/last
            # already present), rather than the preceding last-batch cursor.
            due = (step in self.args.cer_steps if getattr(self.args, 'stage_c', False)
                   else cadence(step, self.total, self.every))
            if due and (step < self.total or position == 0):
                self.checkpoint_eval(step)
            atomic(self.timing_path, dict(**self.timing,
                mean_update_seconds=self.timing['seconds'] / self.timing['samples'] if self.timing['samples'] else None,
                excludes='checkpoint/evaluation; first batch of each epoch/startup excluded',
                runtime_sha256=runtime['_sha256']))
            self.tick = time.monotonic()

        def checkpoint_loss(self, step):
            from loss_journal import append_point
            from train.cer import load_codec
            log = self.path.parent / 'loss_eval' / ('step-%09d.json' % step)
            model_sha = self.t.checkpoint_state_sha256(self.model.state_dict())
            if log.exists():
                prior = read(log)
                if (prior['runtime_sha256'] != runtime['_sha256'] or prior['step'] != step
                        or prior['drawn_lines'] != self.draws or prior['model_sha256'] != model_sha):
                    raise ValueError('existing loss evaluation binding changed')
            else:
                rng, mode = self.rng(), self.model.training
                started = time.monotonic()
                try:
                    codec = load_codec(self.args.codec)
                    device = next(self.model.parameters()).device
                    results = {}
                    for name in panels:
                        result, predictions = evaluator(self.model, pools[name], runtime['references'][name],
                                                         codec, device, decode=False)
                        if predictions or 'score' in result or result['rows'] != len(pools[name]):
                            raise ValueError('loss-only evaluator decoded or changed coverage')
                        results[name] = result
                    atomic(log, dict(schema='TRAIN_FULL-loss-eval-v1', step=step,
                        drawn_lines=self.draws, thresholds=self.loss_points[step]['thresholds'],
                        train_loss_at_step=self.last_training_loss,
                        model_sha256=model_sha, runtime_sha256=runtime['_sha256'], instruments=results,
                        elapsed_seconds=time.monotonic() - started,
                        test_policy='report_only; never selection/stopping/parameter adjustment'))
                finally:
                    self.restore_rng(rng)
                    self.model.train(mode)
            append_point(self.path.parent / 'loss_eval.jsonl', log)
            if runtime.get('mock') and os.environ.get('TRAIN_FULL_TEST_PAUSE_LOSS_STEP') == str(step):
                atomic(self.path.parent / 'TEST_PAUSED.json', dict(step=step, loss_only=True))
                import signal
                signal.pause()

        def checkpoint_eval(self, step):
            target = self.path.parent / 'checkpoints' / ('step-%09d.pt' % step)
            log = self.path.parent / 'eval' / ('step-%09d.json' % step)
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                tmp = target.with_suffix('.pt.tmp')
                shutil.copyfile(self.path, tmp)
                tmp.replace(target)
            state = self.t.torch.load(target, map_location='cpu', weights_only=False)
            if state['global_step'] != step or state['state_sha256'] != self.t.checkpoint_state_sha256(state):
                raise ValueError('invalid archived evaluation checkpoint')
            if log.exists():
                prior = read(log)
                if prior['checkpoint']['sha256'] != sha(target) or prior['runtime_sha256'] != runtime['_sha256']:
                    raise ValueError('existing eval has a changed checkpoint/data binding')
                for entry in prior['prediction_files'].values():
                    bound(entry)
                return
            rng = self.rng()
            mode = self.model.training
            started = time.monotonic()
            results, prediction_files = {}, {}
            try:
                from train.cer import load_codec
                from common import write_rows
                codec = load_codec(self.args.codec)
                device = next(self.model.parameters()).device
                log.parent.mkdir(parents=True, exist_ok=True)
                for name in panels:
                    result, predictions = evaluator(self.model, pools[name], runtime['references'][name], codec, device)
                    result.pop('predictions', None)
                    results[name] = result
                    pred = log.parent / ('step-%09d-%s.predictions.jsonl' % (step, name))
                    # An interrupted evaluation may leave only this deterministic output.
                    tmp = pred.with_suffix('.jsonl.tmp')
                    with tmp.open('w') as f:
                        import json
                        for r in predictions:
                            f.write(json.dumps(r, ensure_ascii=False) + '\n')
                    tmp.replace(pred)
                    prediction_files[name] = spec(pred)
                atomic(log, dict(schema='TRAIN_FULL-checkpoint-eval-v1', step=step,
                    checkpoint=spec(target), state_sha256=state['state_sha256'],
                    runtime_sha256=runtime['_sha256'], instruments=results,
                    prediction_files=prediction_files, elapsed_seconds=time.monotonic() - started,
                    test_policy='report_only; never checkpoint selection, stopping, or parameter adjustment'))
            finally:
                self.restore_rng(rng)
                self.model.train(mode)
            if (runtime.get('mock') and os.environ.get('TRAIN_FULL_TEST_PAUSE_STEP') == str(step)):
                # Test-only hard-kill witness, after a genuinely durable state/eval.
                atomic(self.path.parent / 'TEST_PAUSED.json', dict(step=step))
                import signal
                signal.pause()
    return FullSegment
