"""Actual drawn-line cadence, including S1's shuffled partial batch.

Planning uses the exact frozen assembler/sampler, with local RNGs only. It neither
decodes images nor changes the epoch draw order. Final is included once.
"""
def plan(trainer, runtime, pools, epochs, epoch_rows, bs, every):
    from train.data import PackedWidthBatchSampler
    if min(epochs, epoch_rows, bs, every) < 1:
        raise ValueError('positive loss cadence/horizon required')
    components = runtime['components']
    groups = [pools[c['name']] for c in components]
    fractions = [c['fraction'] for c in components]
    draws, step, points = 0, 0, []
    for epoch in range(1, epochs + 1):
        rr, _ = trainer.assemble(groups, fractions, runtime['seed'], epoch,
                                 epoch_rows, exact_rows=True)
        sampler = PackedWidthBatchSampler([r['width'] for r in rr], bs,
                                         seed=runtime['seed'], shuffle=True)
        sampler.set_epoch(epoch)
        for indices in sampler:
            before = draws
            draws += len(indices)
            step += 1
            if draws // every > before // every:
                points.append(dict(step=step, drawn_lines=draws,
                    thresholds=list(range((before // every + 1) * every,
                                          draws // every * every + 1, every))))
    if not points or points[-1]['step'] != step:
        points.append(dict(step=step, drawn_lines=draws, thresholds=[]))
    return dict(every_drawn_lines=every, includes_final=True, points=points,
                steps=[p['step'] for p in points], count=len(points),
                total_drawn_lines=draws, total_updates=step,
                policy='actual real+synthetic draws; frozen shuffled partial batches; final once')
