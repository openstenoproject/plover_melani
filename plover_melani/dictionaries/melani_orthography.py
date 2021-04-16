from plover_melani.theory import Stroke, Theory


theory = Theory()

# Required interface for Plover "Python" dictionary. {{{

LONGEST_KEY = 1

def lookup(key):
    assert len(key) <= LONGEST_KEY
    try:
        stroke_list = [Stroke(s) for s in key]
    except ValueError as e:
        raise KeyError from e
    translation = ''
    for stroke in stroke_list:
        translation += theory.translate_stroke(stroke)
    return translation

def reverse_lookup(text):
    stroke_list = theory.strokes_from_text(text)
    if not stroke_list:
        return []
    return [tuple(str(s) for s in stroke_list)]

# }}}

# vim: foldmethod=marker
