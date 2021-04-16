import json
import os

from pkg_resources import resource_stream

from plover.oslayer.config import CONFIG_DIR
from plover_stroke import BaseStroke

from plover_melani import system


class Stroke(BaseStroke):
    pass

Stroke.setup(system.KEYS, system.IMPLICIT_HYPHEN_KEYS,
             system.NUMBER_KEY, system.NUMBERS)


META_ATTACH = '{^}'


class Theory:

    def __init__(self, fragments=None):
        self._combos = {}
        self._max_combos_len = 0
        self._word_parts = {}
        self._max_word_part_len = 0
        if fragments is None:
            fragments_filename = os.path.join(CONFIG_DIR, 'melani_orthography.json')
            if os.path.exists(fragments_filename):
                with open(fragments_filename, 'rb') as fp:
                    fragments = json.loads(fp.read().decode('utf-8'))
            else:
                with resource_stream('plover_melani', 'dictionaries/melani_orthography.json') as fp:
                    fragments = json.loads(fp.read().decode('utf-8'))
        for steno, translation in fragments.items():
            stroke = Stroke.from_steno(steno)
            assert stroke not in self._combos
            self._combos[stroke] = translation
            self._max_combos_len = max(len(combo) for combo in self._combos) if self._combos else 0
        for combo, part in self._combos.items():
            if part.endswith(META_ATTACH):
                part = part[:-3]
            else:
                part = part + ' '
            if part in self._word_parts:
                self._word_parts[part] += (combo,)
            else:
                self._word_parts[part] = (combo,)
        for part, combo_list in self._word_parts.items():
            # We want left combos to be given priority over right ones,
            # e.g. 'R-' over '-R' for 'r'.
            self._word_parts[part] = sorted(combo_list)
        if self._word_parts:
            self._max_word_part_len = max(len(part) for part in self._word_parts)
        else:
            self._max_word_part_len = 0

    def translate_stroke(self, stroke):
        if not self._combos:
            raise KeyError
        keys = list(stroke.keys())
        text = ''
        while keys:
            combo = Stroke(keys[0:self._max_combos_len])
            while combo:
                if combo in self._combos:
                    part = self._combos[combo]
                    text += part
                    break
                combo -= combo.last()
            if not combo:
                raise KeyError
            keys = keys[len(combo):]
        attach_start = text.startswith(META_ATTACH)
        attach_end = text.endswith(META_ATTACH)
        text = text.replace(META_ATTACH, '')
        if attach_start:
            text = META_ATTACH + text
        if attach_end:
            text = text + META_ATTACH
        return text

    def strokes_to_text(self, stroke_list):
        text = ''
        attach_next = True
        for s in stroke_list:
            part = self.translate_stroke(s)
            if not attach_next and not part.startswith(META_ATTACH):
                text += ' '
            attach_next = part.endswith(META_ATTACH)
            text += part.replace(META_ATTACH, '')
        if not attach_next:
            text += ' '
        return text

    def strokes_from_text(self, text):
        if not text:
            return []
        if text[-1] in 'ieao':
            text = text + ' '
        leftover_text = text
        stroke_list = []
        part_list = []
        while len(leftover_text) > 0:
            # Find candidate parts.
            combo_list = []
            part = leftover_text[0:self._max_word_part_len]
            while len(part) > 0:
                combo_list.extend(self._word_parts.get(part, ()))
                part = part[:-1]
            if len(combo_list) == 0:
                return ()
            # First try to extend current stroke.
            part = None
            if stroke_list:
                stroke = stroke_list[-1]
                for combo in combo_list:
                    if stroke.is_prefix(combo):
                        # Check if we're not changing the translation.
                        combo_part = self.strokes_to_text((combo,))
                        wanted = self.strokes_to_text((stroke,)) + combo_part
                        result = self.strokes_to_text((stroke + combo,))
                        if wanted != result:
                            continue
                        part = combo_part
                        stroke_list[-1] += combo
                        part_list[-1] += part
                        break
            # Start a new stroke
            if part is None:
                combo = combo_list[0]
                part = self.strokes_to_text((combo,))
                stroke_list.append(combo)
                part_list.append(part)
            assert len(part) > 0
            leftover_text = leftover_text[len(part):]
        assert len(stroke_list) == len(part_list)
        return stroke_list

# vim: foldmethod=marker
