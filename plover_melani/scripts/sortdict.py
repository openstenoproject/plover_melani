from collections import OrderedDict
from io import open
import json
import sys

from plover_melani.theory import Stroke, Theory


def run():
    theory = Theory()
    if len(sys.argv) == 1:
        print('usage: %s [-s] DICTIONARIES..')
        return
    if sys.argv[1] == '-s':
        strip = True
        args = sys.argv[2:]
    else:
        strip = False
        args = sys.argv[1:]
    for filename in args:
        with open(filename, encoding='utf-8') as fp:
            dictionary = dict(
                (tuple(Stroke(s) for s in k.split('/')), v)
                for k, v in json.load(fp).items()
            )
        if strip:
            for stroke_list, translation in list(dictionary.items()):
                if len(stroke_list) != 1:
                    continue
                try:
                    orthographic_translation = theory.translate_stroke(stroke_list[0])
                except KeyError:
                    continue
                if orthographic_translation == translation:
                    del dictionary[stroke_list]
        sorted_dictionary = OrderedDict(
            ('/'.join(str(s) for s in k), v)
            for k, v in sorted(dictionary.items())
        )
        contents = json.dumps(sorted_dictionary,
                              indent=0,
                              sort_keys=False,
                              ensure_ascii=False,
                              separators=(',', ': '))
        with open(filename, 'wb') as fp:
            fp.write(contents.encode('utf-8'))


if __name__ == '__main__':
    run()
