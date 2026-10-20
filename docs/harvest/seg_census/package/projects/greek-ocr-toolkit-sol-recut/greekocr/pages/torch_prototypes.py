"""Opt-in Q5 array experiments; never imported by the production page API.

CPU geometry and decisions retain Q4 semantics. Float32 fits/resampling are
experiments, not drop-in exact replacements. See scripts/pages/benchmark_q5.py.
Torch is imported only when a backend is explicitly constructed.
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy import ndimage as ndi

from . import font
from .lines import PIXEL_EDGE_HALF_STEP, STRIP_BASELINE_XH, STRIP_HEIGHT_XH


class TorchArrays:
    """Small, bounded batches on an explicitly requested torch device."""

    def __init__(self, device="cpu", batch_size=16):
        if device not in ("cpu", "mps", "cuda"):
            raise ValueError("device must be cpu, mps or cuda")
        if batch_size < 1:
            raise ValueError("batch_size must be positive")
        import torch
        self.torch = torch
        self.device = torch.device(device)
        self.batch_size = batch_size
        # Allocation is intentional: never silently fall back to another device.
        torch.ones(1, device=self.device).add_(1).cpu()
        self.synchronize()

    def synchronize(self):
        if self.device.type == "mps":
            self.torch.mps.synchronize()
        elif self.device.type == "cuda":
            self.torch.cuda.synchronize(self.device)

    def tensor(self, value):
        return self.torch.as_tensor(np.asarray(value, dtype=np.float32), device=self.device)

    def morphology_batch(self, calls):
        """Q4 rectangular morphology; batch only identical shapes and kernels.

        Each call is (bool mask, (height, width), closing). Two separable
        extrema passes avoid a quadratic rectangular pooling window. Explicit
        zero padding and different even-size origins match Q4/OpenCV.
        """
        f = self.torch.nn.functional
        groups = defaultdict(list)
        output = [None] * len(calls)
        for i, (mask, shape, closing) in enumerate(calls):
            groups[(mask.shape, tuple(shape), closing)].append(i)
        for (_, shape, closing), indices in groups.items():
            for start in range(0, len(indices), self.batch_size):
                ids = indices[start:start+self.batch_size]
                x = self.tensor(np.stack([calls[i][0] for i in ids]))[:, None]

                def extrema(value, erode):
                    for dim, size in enumerate(shape):
                        anchor = size//2 if erode else (size-1)//2
                        pad = (0, 0, anchor, size-1-anchor) if dim == 0 else (anchor, size-1-anchor, 0, 0)
                        kernel = (size, 1) if dim == 0 else (1, size)
                        padded = f.pad(value, pad, value=0)
                        value = -f.max_pool2d(-padded, kernel, stride=1) if erode else f.max_pool2d(padded, kernel, stride=1)
                    return value

                x = extrema(extrema(x, not closing), closing)
                values = x[:, 0].cpu().numpy().astype(bool)
                for i, value in zip(ids, values):
                    output[i] = value
        return output

    def smooth_batch(self, calls):
        """Batch local WLS knots across independent guide corrections.

        Inputs are (xs, residuals, integer grid, xheight). Padding has zero
        weight. The three IRLS iterations and regularizers are Q4's. The
        2x2 solve uses its Schur complement, avoiding backend-specific linalg
        fallback. Interpolation and Gaussian smoothing remain SciPy/float64.
        """
        t = self.torch
        output = [None] * len(calls)
        # Shape buckets reduce ragged padding. Bound the contact/knots product
        # as well as the line count, including unusually wide/dense lines.
        order = sorted(range(len(calls)), key=lambda i: (len(calls[i][0]), len(calls[i][2])))
        cursor = 0
        while cursor < len(order):
            ids = []
            max_n = max_k = 0
            for i in order[cursor:cursor+self.batch_size]:
                xs, _, grid, xh = calls[i]
                n, k = len(xs), max(2, round(len(grid)/xh)+1)
                if ids and (len(ids)+1)*max(max_n, n)*max(max_k, k) > 1_000_000:
                    break
                ids.append(i)
                max_n, max_k = max(max_n, n), max(max_k, k)
            cursor += len(ids)
            # A single exceptional line is tiled by knots below.
            x = np.zeros((len(ids), max_n), np.float32)
            y = np.zeros_like(x)
            valid = np.zeros_like(x)
            knots = np.zeros((len(ids), max_k), np.float32)
            xheights = np.empty((len(ids), 1, 1), np.float32)
            exact_knots = []
            for j, i in enumerate(ids):
                xs, ys, grid, xh = calls[i]
                ks = np.linspace(grid[0], grid[-1], max(2, round(len(grid)/xh)+1))
                exact_knots.append(ks)
                x[j, :len(xs)], y[j, :len(xs)], valid[j, :len(xs)] = xs-grid[0], ys, 1
                knots[j, :len(ks)] = ks-grid[0]
                xheights[j] = xh
            tx, ty, tv = self.tensor(x)[:, None], self.tensor(y)[:, None], self.tensor(valid)[:, None]
            th = self.tensor(xheights)
            pieces = []
            tile = max(1, 1_000_000//max(1, len(ids)*max_n))
            for lo in range(0, max_k, tile):
                dx = (tx-self.tensor(knots[:, lo:lo+tile])[:, :, None])/th
                weight = t.clamp(1-(dx.abs()/font.LOCAL_FIT_RADIUS_XH)**3, min=0)**3 * tv
                gaussian = t.exp(-font.GAUSSIAN_EXPONENT_FACTOR*(dx/font.LOCAL_FIT_RADIUS_XH)**2)*tv
                weight = t.where((weight > font.MIN_LOCAL_WEIGHT).sum(-1, keepdim=True) < 3, gaussian, weight)
                c0, c1 = t.zeros_like(dx[:, :, :1]), t.zeros_like(dx[:, :, :1])
                for _ in range(3):
                    residual = ty-c0-dx*c1
                    robust = t.clamp(font.ROBUST_RESIDUAL_XH*th/t.clamp(residual.abs(), min=font.SOLVE_EPSILON), max=1)
                    ww = weight*robust
                    a = ww.sum(-1, keepdim=True)+font.SOLVE_EPSILON
                    mu = (ww*dx).sum(-1, keepdim=True)/a
                    centered = dx-mu
                    # Centered normal equations retain the original intercept
                    # ridge exactly while avoiding subtraction of near-equal
                    # second moments for sparse, extrapolated contacts.
                    d = (ww*centered*centered).sum(-1, keepdim=True)+font.SOLVE_EPSILON*mu*mu+font.SLOPE_RIDGE
                    r0 = (ww*ty).sum(-1, keepdim=True)
                    c1 = (ww*centered*ty).sum(-1, keepdim=True)/d
                    c0 = r0/a-mu*c1
                pieces.append(c0[:, :, 0].cpu().numpy())
            fitted = np.concatenate(pieces, axis=1)
            for j, i in enumerate(ids):
                _, _, grid, xh = calls[i]
                ks = exact_knots[j]
                output[i] = ndi.gaussian_filter1d(np.interp(grid, ks, fitted[j, :len(ks)]), max(1., font.GUIDE_SMOOTH_XH*xh))
        return output

    def straighten_batch(self, gray, lines, *, xheight=32, pixel_budget=1_000_000):
        """One page upload, bounded packed bilinear gathers for its line batch.

        The CPU supplies exact float64 source coordinates, integer neighbors,
        fractions and the Q4 outside/envelope predicate. Keeping those decisions
        on the CPU avoids normalized-grid and float32 coordinate rounding at
        page edges. The GPU computes all bilinear pixel values in a packed batch.
        This also avoids repeating the entire page once per line.
        """
        if not isinstance(xheight, (int, np.integer)) or xheight <= 0:
            raise ValueError("xheight must be a positive integer")
        if pixel_budget < 1:
            raise ValueError("pixel_budget must be positive")
        t = self.torch
        h, w = gray.shape
        page = self.tensor(gray).flatten()
        output = []
        # Form one packed batch at a time. A long strip can be tiled without
        # changing its source coordinates or integer output width.
        pending, lengths, shapes = [], [], []
        count = 0

        def flush():
            if not pending:
                return
            coords = [np.concatenate([p[k] for p in pending]) for k in range(5)]
            x, y, fx, fy, outside = coords
            ix = t.as_tensor(x, device=self.device, dtype=t.int64)
            iy = t.as_tensor(y, device=self.device, dtype=t.int64)
            tx, ty = self.tensor(fx), self.tensor(fy)
            right, down = t.clamp(ix+1, max=w-1), t.clamp(iy+1, max=h-1)
            value = ((page[iy*w+ix]*(1-tx)+page[iy*w+right]*tx)*(1-ty)
                     +(page[down*w+ix]*(1-tx)+page[down*w+right]*tx)*ty)
            value = t.where(t.as_tensor(outside, device=self.device), 255., value)
            result = value.clamp(0, 255).to(t.uint8).cpu().numpy()
            offset = 0
            for length in lengths:
                output.append(result[offset:offset+length].copy())
                offset += length
            pending.clear()
            lengths.clear()

        part_counts = []
        for line in lines:
            scale = xheight/line.xheight
            width = max(1, int(np.ceil((line.x1-line.x0)*scale)))
            xs = np.clip(line.x0+(np.arange(width)+PIXEL_EDGE_HALF_STEP)/scale-PIXEL_EDGE_HALF_STEP, line.x0, line.x1-1)
            grid = np.arange(line.x0, line.x1)
            base = np.interp(xs, grid, line.baseline)
            local = np.interp(xs, grid, line.baseline-line.meanline)
            offsets = (np.arange(STRIP_HEIGHT_XH*xheight)-STRIP_BASELINE_XH*xheight)/xheight
            yy = base[None]+offsets[:, None]*local[None]
            xx = np.broadcast_to(xs, yy.shape)
            top, bottom = np.interp(xs, grid, line.top), np.interp(xs, grid, line.bottom)
            outside = (yy < 0) | (yy > h-1) | (xx < 0) | (xx > w-1) | (yy < top) | (yy >= bottom)
            cx, cy = np.clip(xx, 0, w-1), np.clip(yy, 0, h-1)
            ix, iy = np.floor(cx).astype(np.int64), np.floor(cy).astype(np.int64)
            arrays = [v.ravel() for v in (ix, iy, cx-ix, cy-iy, outside)]
            shapes.append(yy.shape)
            parts = 0
            for lo in range(0, yy.size, pixel_budget):
                length = min(pixel_budget, yy.size-lo)
                if pending and (count+length > pixel_budget or len(pending) >= self.batch_size):
                    flush()
                    count = 0
                pending.append([v[lo:lo+length] for v in arrays])
                lengths.append(length)
                count += length
                parts += 1
            part_counts.append(parts)
        flush()
        result, pos = [], 0
        for parts, shape in zip(part_counts, shapes):
            result.append(np.concatenate(output[pos:pos+parts]).reshape(shape))
            pos += parts
        return result
