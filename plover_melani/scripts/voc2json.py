from collections import namedtuple, OrderedDict
import csv
import json
import re
import sys

from plover_melani.theory import Stroke, Theory


def warning(fmt, *args):
    sys.stderr.write('warning: ' + (fmt % args) + '\n')


class StrokeList(tuple):

    def __new__(cls, steno):
        if not isinstance(steno, str):
            return tuple.__new__(cls, steno)
        for old, new in (
            ('\\', '/'),
            ('$', '#'),
        ):
            steno = steno.replace(old, new)
        stroke_list = []
        for stroke in steno.split('/'):
            keys = []
            for k in stroke:
                if k in '#*':
                    pass
                elif k in 'SPCTHVRIA':
                    k = k + '-'
                elif k in 'EOcsthprieao':
                    k = '-' + k
                else:
                    raise Exception('invalid key: %s' % k)
                keys.append(k)
            stroke_list.append(Stroke(keys))
        return tuple.__new__(cls, stroke_list)

    def __str__(self):
        return '/'.join(str(s) for s in self)


class Translation(namedtuple('Translation', 'text word_finished add_space')):

    def __new__(cls, text, word_finished=None, add_space=None):
        if word_finished is not None:
            return super(Translation, cls).__new__(cls, text, word_finished, add_space)
        for old, new in (
            ('&dw;' , '{-}'         ), # undo
            ('&1uc;', '{-|}'        ),
            ('&amp;', '&'           ),
            ('&cr;' , '{#Return}'   ),
            ('&lc;' , '{MODE:RESET}'), # lowercase
            ('&rb;' , '{^}'         ),
            ('&sp;' , ' '           ),
            ('&uc;' , '{MODE:CAPS}' ), # UPPERCASE
        ):
            text = text.replace(old, new)
        if '&+i;' in text:
            word_finished = True
            text = text.replace('&+i;', '')
        text = re.sub(r'&var;\|([^|]*)\|([^|]*)\|([^|]*)\|', cls._replace_var, text)
        if text.endswith(' '):
            add_space = True
            word_finished = True
            text = text[:-1]
            if not text:
                text = '{ }'
        elif text.endswith(' {-|}'):
            add_space = True
            word_finished = True
            text = text[:-5] + '{-|}'
        else:
            add_space = False
        return super(Translation, cls).__new__(cls, text, word_finished, add_space)

    @staticmethod
    def _replace_var(match):
        else_translation = match.group(1)
        match_candidates = match.group(2).split()
        match_translation = match.group(3)
        text = '{=(?i)'
        if match_translation.endswith(' ') and else_translation.endswith(' '):
            add_space = True
            match_translation = match_translation[:-1]
            else_translation = else_translation[:-1]
        else:
            add_space = False
        if add_space:
            text += ' '
        match_candidates_by_length = []
        for c in sorted(match_candidates, key=lambda s: (len(s), s)):
            prefix = c[:-1]
            last_char = c[-1]
            if (
                match_candidates_by_length and
                prefix == match_candidates_by_length[-1][0]
            ):
                match_candidates_by_length[-1][1].append(last_char)
            else:
                match_candidates_by_length.append((prefix, [last_char]))
        match_candidates_by_length.sort(key=lambda k: k[0])
        match_candidates = []
        for prefix, char_list in match_candidates_by_length:
            assert char_list
            if len(char_list) > 1:
                match = '%s[%s]' % (re.escape(prefix),
                                     ''.join(re.escape(c)
                                              for c in char_list))
            else:
                match = re.escape(prefix + char_list[0])
            match_candidates.append(match)
        text += '(%s)/%s/%s}' % (
            '|'.join(match_candidates),
            match_translation,
            else_translation,
        )
        if add_space:
            text += ' '
        return text

    def __str__(self):
        s = self.text
        if not self.add_space:
            s += '{^}'
            if self.word_finished:
                s += '{$}'
        s = s.replace('{-|}{^}{$}', '{^}{$}{-|}')
        return s


def load_database(filename, model=1, filter_out_number_strokes=True):

    combos_fragments = {}
    prefix_dictionary = {}
    suffix_dictionary = {}

    def add_fragment(stroke_list, translation):
        if len(stroke_list) != 1:
            warning('ignoring multiple strokes combo fragment for %s: %s',
                    stroke_list, translation)
            return
        stroke = stroke_list[0]
        assert stroke not in combos_fragments or combos_fragments[stroke] == translation
        combos_fragments[stroke] = translation

    def add_prefix(stroke_list, translation):
        if prefix_dictionary.get(stroke_list, translation) != translation:
            warning('duplicate prefix dictionary entry for %s: %s, '
                    'already present %s, ignoring',
                    stroke_list, translation, prefix_dictionary[stroke_list])
        else:
            prefix_dictionary[stroke_list] = translation

    def add_suffix(stroke_list, translation):
        if suffix_dictionary.get(stroke_list, translation) != translation:
            warning('duplicate suffix dictionary entry for %s: %s, '
                    'already present %s, ignoring',
                    stroke_list, translation, suffix_dictionary[stroke_list])
        else:
            suffix_dictionary[stroke_list] = translation

    with open(filename) as fp:
        reader = csv.reader(fp)
        assert len(next(reader)) == 5
        for row in reader:
            row = [str(cell, 'UTF-8') for cell in row]
            steno = row[0]
            text1 = row[1]
            text2 = row[2]
            readonly = int(row[3]) != 0
            stroke_list = StrokeList(steno)
            translation1 = Translation(text1) if text1 else None
            translation2 = Translation(text2) if text2 else None
            if filter_out_number_strokes and len(stroke_list) == 1:
                stroke = stroke_list[0]
                if (stroke & '#') != 0 and (stroke & ~Stroke('#SPTVIOctpi')) == 0:
                    if translation1 is not None:
                        assert re.match(r'^\d+$', translation1.text)
                    if translation2 is not None:
                        assert re.match(r'^\d+$', translation2.text)
                    continue
            # print('%d %-20s %-50.50s %-50.50s' % (
            #     1 if readonly else 0, stroke_list,
            #     translation1, translation2))
            if model == 1:
                if readonly == 0:
                    if translation1 is not None:
                        add_suffix(stroke_list, translation1)
                    if translation2 is not None:
                        add_fragment(stroke_list, translation2)
                else:
                    if translation1 is not None:
                        add_prefix(stroke_list, translation1)
                    if translation2 is not None:
                        add_fragment(stroke_list, translation2)
            elif model == 2:
                if translation1 is not None:
                    add_prefix(stroke_list, translation1)
                if translation2 is not None:
                    add_fragment(stroke_list, translation2)
    return combos_fragments, prefix_dictionary, suffix_dictionary


def save_dictionary(dictionary, filename):
    utf_dict = OrderedDict(
        (str(k).encode('utf-8'), str(v).encode('utf-8'))
        for k, v in sorted(dictionary.items())
    )
    with open(filename, 'w') as fp:
        json.dump(utf_dict, fp,
                  indent=0,
                  sort_keys=False,
                  ensure_ascii=False,
                  separators=(',', ': '))


def run():
    args = sys.argv[1:]
    assert len(args) <= 1
    if args:
        database = args[0]
    else:
        database = 'voc-it.csv'
    fragments, prefixes, suffixes = load_database(database)
    for steno in set(prefixes.keys()) & set(suffixes.keys()):
        if prefixes[steno] == suffixes[steno]:
            del prefixes[steno]
    # Remove suffixes available through the orthographic dictionary.
    theory = Theory(dict(fragments))
    for steno, translation in suffixes.items():
        if len(steno) != 1:
            continue
        try:
            orthographic_translation = theory.translate_stroke(steno[0])
        except KeyError:
            continue
        if orthographic_translation == translation:
            del suffixes[steno]
    print('%u fragments' % len(fragments))
    # for stroke, translation in fragments.items():
    #     print('%s: %s' % (stroke, translation))
    print('%u prefixes' % len(prefixes))
    # for stroke, translation in prefixes.items():
    #     print('%s: %s' % (stroke, translation))
    print('%u suffixes' % len(suffixes))
    # for stroke, translation in suffixes.items():
    #     print('%s: %s' % (stroke, translation))
    # print
    briefs = {
        StrokeList((Stroke(0),) + tuple(steno)): translation
        for steno, translation
        in prefixes.items()
    }
    # fragments = {
    #     StrokeList((steno,)) : translation
    #     for steno, translation
    #     in fragments.items()
    # }
    briefs.update(suffixes)
    save_dictionary(fragments, 'melani_fragments.json')
    save_dictionary(briefs, 'melani_briefs.json')


if __name__ == '__main__':
    run()
