"""Offline, additive owner sheets and independent blind adjudication.

Historical replay specs preserve their original protocol. New decks require two
independent readers and a separately mapped tiebreak for disagreements.
"""
from .deck import build_deck
from .owner_sheet import render
