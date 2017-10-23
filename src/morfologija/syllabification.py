import collections

from .sounds import VOWELS
from .sounds import split_sounds

S = set('szšž')
T = set('pbtdkgcč') | {'dz', 'dž'}
R = set('lmnrvj')

STRULES = {'STR', 'ST', 'SR', 'TR'}

Template = collections.namedtuple('Template', 'template example')

SYLLABIFICATION_TEMPLATES = [
    Template(template='*s-dešimt*', example=['trisdešimt', 'keturiasdešimt']),
]


def tostr(sound):
    if sound in S:
        return 'S'
    if sound in T:
        return 'T'
    if sound in R:
        return 'R'
    return '?'


#def compile_template(tmpl):
#    regex = ''
#    if tmpl.template.startswith('*'):
#
#
#
#_compiled_templates = None
#def compile_templates():
#    global _compiled_templates
#    if _compiled_templates is None:
#        _compiled_templates = [
#            compile_template(tmpl) for tmpl in SYLLABIFICATION_TEMPLATES
#        ]
#    return _compiled_templates
#
#
#def apply_template(word):
#    for template in SYLLABIFICATION_TEMPLATES:
#        t


def syllabificate(word):
    syllables = []
    consonants = []
    syllable = ''
    STR = ''
    is_vowel = False
    for sound in split_sounds(word):
        if sound in VOWELS and is_vowel:
            syllable += sound
        elif sound in VOWELS:
            carry_consonants = (
                (consonants and len(syllables) == 0) or
                (len(consonants) == 1) or
                (STR in STRULES)
            )
            if carry_consonants:
                syllables.append(syllable)
                syllable = ''.join(consonants)
            elif len(STR) > 2 and STR[-2:] in STRULES:
                syllable += ''.join(consonants[:-2])
                syllables.append(syllable)
                syllable = ''.join(consonants[-2:])
            elif len(STR) > 1:
                syllable += ''.join(consonants[:-1])
                syllables.append(syllable)
                syllable = ''.join(consonants[-1:])
            else:
                syllable += ''.join(consonants)
                syllables.append(syllable)
                syllable = ''
            STR = ''
            consonants = []
            syllable += sound
        else:
            STR += tostr(sound)
            consonants.append(sound)
            if len(STR) > 3:
                syllable += consonants.pop(0)
                STR = STR[1:]
        is_vowel = sound in VOWELS
    if syllable:
        syllables.append(syllable + ''.join(consonants))
    elif consonants and syllables:
        syllables[-1] += ''.join(consonants)
    return list(filter(None, syllables))
