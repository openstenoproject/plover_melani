from plover_melani.theory import Theory


def test_strokes_from_empty_text():
    theory = Theory()
    assert theory.strokes_from_text('') == []
