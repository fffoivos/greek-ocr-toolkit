"""Shared numerical observations, without per-page cache state.

Each function returns newly owned arrays. A resize at unchanged dimensions also
copies, matching OpenCV. Callers may mutate their output without changing input.
Paper-relative contrast has one arithmetic implementation; threshold calibration
and observation windows remain explicit caller hypotheses.
"""
import cv2
import numpy as np


def resize(image, size, interpolation=cv2.INTER_AREA):
    return cv2.resize(image, tuple(map(int, size)), interpolation=interpolation)


def paper(image, width, *, method):
    width = int(width)
    if method == 'mean':
        return cv2.boxFilter(image, cv2.CV_32F, (width, width))
    if method == 'closing':
        return cv2.morphologyEx(image, cv2.MORPH_CLOSE, np.ones((width, width), np.uint8))
    if method == 'median':
        return cv2.medianBlur(image, width).astype(np.float32)
    raise ValueError(method)


def ink(image, width, *, method, threshold, arithmetic):
    p = paper(image, width, method=method)
    delta = p.astype(np.float32) - image
    if arithmetic == 'relative':
        threshold = threshold * np.maximum(p, 1)
    elif arithmetic != 'dn':
        raise ValueError(arithmetic)
    return (delta > threshold).astype(np.uint8)


def components(mask):
    return cv2.connectedComponentsWithStats(mask, 8)
