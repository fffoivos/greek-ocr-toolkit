"""Smooth white-gap projection, independent of the historical row model."""
from scipy.ndimage import maximum_filter1d, minimum_filter1d, gaussian_filter1d
import numpy as np

def smooth_corridor(nominal,low,high,h):
    """Piecewise-linear shared gap with neighbourhood obstacle envelopes.

    A radius of half a body turns pixel notches into finite shoulders. When a
    tall initial occupies that shoulder, the adjacent band goes around it.
    """
    width=max(1,round(h/2))
    low=maximum_filter1d(low,width,axis=-1,mode='nearest')
    high=minimum_filter1d(high,width,axis=-1,mode='nearest')
    gap=np.clip(gaussian_filter1d(nominal,max(1,h/3),axis=-1),low,high)
    return gap,low>high
