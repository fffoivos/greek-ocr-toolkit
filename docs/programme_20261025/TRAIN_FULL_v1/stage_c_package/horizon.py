"""Resolve a sealed recipe against the audited unique real TRAIN population."""
import math
from common import schedule


def resolve(recipe, train_rows, choice='full'):
    if not isinstance(train_rows, int) or train_rows < 1:
        raise ValueError('positive audited unique real train count required')
    if choice not in ('full', 's1-literal', 'longer'):
        raise ValueError('unknown horizon recipe: ' + choice)
    epochs = 12 if choice == 'longer' else recipe['parameters']['epochs']
    epoch_rows = 428872 if choice == 's1-literal' else 2 * train_rows
    steps_per_epoch = math.ceil(epoch_rows / recipe['parameters']['bs'])
    updates = epochs * steps_per_epoch
    return dict(choice=choice, default=choice == 'full', epochs=epochs,
        unique_real_train=train_rows, epoch_rows=epoch_rows,
        steps_per_epoch=steps_per_epoch, total_updates=updates,
        mixed_draws=epochs * epoch_rows, real_draws=epochs * epoch_rows // 2,
        checkpoint_steps=schedule(updates, recipe['evaluation_every_updates']),
        onecycle_total_steps=updates, synthetic_fraction=.5)


def verify_full_pass(components, pool_sizes, train_rows):
    """Use the frozen S1 largest-remainder calculation; change no draw rule."""
    exact = [2 * train_rows * c['fraction'] / math.fsum(c['fraction'] for c in components)
             for c in components]
    counts = [math.floor(x) for x in exact]
    for i in sorted(range(len(counts)), key=lambda i: (-(exact[i] - counts[i]), i))[:2 * train_rows - sum(counts)]:
        counts[i] += 1
    for c, count in zip(components, counts):
        if c['kind'] == 'real' and count != pool_sizes[c['name']]:
            raise ValueError('full real pass conflicts with unchanged S1 source quotas: ' + c['name'])
    if sum(n for c, n in zip(components, counts) if c['kind'] == 'synthetic') != train_rows:
        raise ValueError('full pass does not retain exact half synthetic')
    return dict(component_draws={c['name']: n for c, n in zip(components, counts)},
                real_pass='one shuffled permutation of each unique real TRAIN pool per epoch')
