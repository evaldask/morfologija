VOWELS = 'aąeęėiįyouųū'
FRON_VOWELS = 'iįyeęė'
BACK_VOWELS = 'aąouųū'


def iter_vowels(chars):
    vowels = []
    for c in chars:
        vowel = c in VOWELS
        if vowel:
            vowels.append(c)
        else:
            yield ''.join(vowels)
            vowels = []
    if vowels:
        yield ''.join(vowels)


def split_sounds(word):
    last = ''
    for char in word:
        if char in {'z', 'ž'} and last == 'd':
            yield last + char
            last = ''
            continue
        if last:
            yield last
        last = char
    if last:
        yield last
