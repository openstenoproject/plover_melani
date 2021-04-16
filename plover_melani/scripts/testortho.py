import sys

from plover_melani.theory import Stroke, Theory


theory = Theory()

# Main entry-point for testing. {{{

def run():
    if len(sys.argv) > 1 and sys.argv[1] == '/':
        # steno -> text.
        for steno in sys.argv[2:]:
            stroke_list = [Stroke(s) for s in steno.split('/')]
            try:
                text = theory.strokes_to_text(stroke_list)
            except KeyError:
                text = steno
            print(text, end='')
        print()
    else:
        # text -> steno.
        for text in sys.argv[1:]:
            stroke_list = theory.strokes_from_text(text)
            steno = '/'.join(str(s) for s in stroke_list)
            print(steno, end='')
        print()


if __name__ == '__main__':
    run()

# }}}

# vim: foldmethod=marker
