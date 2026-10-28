"""Only the test harness imports this. Real trainer/data/CTC, tiny mocked model."""
import argparse
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import run

original = run.install


def mock_install(*args, **kwargs):
    if os.environ.get('TEST_INTERRUPT_LOSS_MARKER'):
        from full_hook import evaluate_panel
        def interrupted(*values, **options):
            marker = Path(os.environ['TEST_INTERRUPT_LOSS_MARKER'])
            if not options.get('decode', True) and not marker.exists():
                import random
                import numpy as np
                import torch
                random.random(); np.random.rand(); torch.rand(3)
                values[0].eval()
                marker.write_text('unfinished loss eval; RNG/mode must restore')
                raise RuntimeError('test interrupted unfinished loss eval')
            return evaluate_panel(*values, **options)
        kwargs['evaluator'] = interrupted
    trainer, runtime = original(*args, **kwargs)
    trainer._runtime()
    import torch

    class Toy(torch.nn.Module):
        def __init__(self, n):
            super().__init__()
            self.dropout = torch.nn.Dropout(.2)
            self.projection = torch.nn.Linear(1, n)

        def forward(self, x):
            # Preserve a real stochastic forward and real CTC backward.
            features = x.mean(2).transpose(1, 2)[:, ::4, :]
            return self.projection(self.dropout(features)).log_softmax(-1)

    trainer.build_arm = lambda head, arch, codec, **kwargs: Toy(codec.n_classes)
    return trainer, runtime


run.install = mock_install
# Test harness only: compare normal periodic evaluation against final-only, or
# fail/kill inside an unfinished loss evaluation. Production exposes no override.
import loss_cadence
original_plan = loss_cadence.plan
def test_plan(*args, **kwargs):
    if os.environ.get('TEST_LOSS_EVERY'):
        args = (*args[:-1], int(os.environ['TEST_LOSS_EVERY']))
    return original_plan(*args, **kwargs)
loss_cadence.plan = test_plan

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--runtime', required=True)
    p.add_argument('--out', required=True)
    a = p.parse_args()
    raise SystemExit(run.execute(a.runtime, a.out, mock=True))
