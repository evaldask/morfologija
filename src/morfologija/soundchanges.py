from .utils import first
from .sounds import iter_vowels
from .sounds import BACK_VOWELS



def affricate(left, right):
    left_ending = left[-1]
    changes = {'d': 'dž', 't': 'č'}
    vowels = (first(iter_vowels(right)) or '')[:2]
    triggers = ['i' + s for s in BACK_VOWELS]
    if left_ending in ('d', 't') and vowels in triggers:
        return left[:-len(left_ending)] + changes[left_ending]
    else:
        return left


def affrication(stem, suffixes):
    if len(suffixes) > 1:
        left, right = suffixes[-2], suffixes[-1]
        left = affricate(left, right)
        suffixes[-2] = left
    elif len(suffixes) == 1:
        left, right = stem, suffixes[0]
        left = affricate(left, right)
        stem = left
    return stem, suffixes
