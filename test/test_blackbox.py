# -*- coding: utf-8 -*-

import re

from plover import log, system
from plover.registry import registry
from plover_build_utils.testing import CaptureOutput, blackbox_test
import plover_build_utils.testing


log.set_level(log.DEBUG)


class ExtendedCaptureOutput(CaptureOutput):

    LAST_WORD_RX = re.compile(r'([-+]?\d[\.\d]*|[\w]+|[^\s\w]+|^)\s*$', re.UNICODE)

    def send_key_combination(self, c):
        self.instructions.append(('c', c))
        c = c.lower()
        if c == 'control_l(backspace)':
            m = self.LAST_WORD_RX.search(self.text)
            if m is not None:
                self.text = self.text[:m.start()]

plover_build_utils.testing.CaptureOutput = ExtendedCaptureOutput


@blackbox_test
class TestsBlackbox:

    @classmethod
    def setup_class(cls):
        registry.update()
        system.setup('Melani')

    def test_numbers(self):
        r'''
        "15/SE/COhro": "XV secolo",
        "16/SE/COhro": "XVI secolo",

        15/SE/COhro/16/SE/COhro  " XV secolo XVI secolo"
        '''

    def test_conditionals_1(self):
        r'''
        "hri": "{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/agli/ai}",
        "Oc": "oc{^}",
        "CHi": "chi",
        "THEi": "dei",
        "STI": "sti{^}",
        "VAhri": "vali",

        hri   " ai"
        Oc    " agli oc"
        CHi   " agli occhi"
        hri   " agli occhi ai"
        THEi  " agli occhi agli dei"
        hri   " agli occhi agli dei ai"
        STI   " agli occhi agli dei agli sti"
        VAhri " agli occhi agli dei agli stivali"
        '''

    def test_conditionals_2(self):
        r'''
        "hri": "{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/agli/ai}",
        "Oc": "oc{^}",
        "CHi": "chi",
        "THEi": "dei",
        "STI": "sti{^}",
        "VAhri": "vali",

        :spaces_after
        hri   "ai "
        Oc    "agli oc"
        CHi   "agli occhi "
        hri   "agli occhi ai "
        THEi  "agli occhi agli dei "
        hri   "agli occhi agli dei ai "
        STI   "agli occhi agli dei agli sti"
        VAhri "agli occhi agli dei agli stivali "
        '''

    def test_conditionals_3(self):
        r'''
        'C*e':"c'è",
        'CHRAre':"mare",
        'Cct':" {^\n^}{MODE:RESET}{^}{$}{-|}",
        'Hhr':"nel",
        'PE':"pe{^}",
        'ROs':"ros{^}",
        'SCe':"sce",
        'So':"so",
        'h':"un",
        'hri':"{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/agli/ai}",

        Hhr/CHRAre/C*e/h/PE/SCe/ROs/So/Cct/hri/Cct/Hhr/CHRAre/C*e/h/PE/SCe/ROs/So '''\
                r'''" nel mare c'è un pesce rosso\nAi\nNel mare c'è un pesce rosso"
        '''

    def test_conditionals_4(self):
        r'''
        'C*e':"c'è",
        'CHRAre':"mare",
        'Cct':" {^\n^}{MODE:RESET}{^}{$}{-|}",
        'Hhr':"nel",
        'PE':"pe{^}",
        'ROs':"ros{^}",
        'SCe':"sce",
        'So':"so",
        'h':"un",
        'hri':"{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/agli/ai}",

        :spaces_after
        Hhr/CHRAre/C*e/h/PE/SCe/ROs/So/Cct/hri/Cct/Hhr/CHRAre/C*e/h/PE/SCe/ROs/So '''\
                r'''"nel mare c'è un pesce rosso\nAi\nNel mare c'è un pesce rosso "
        '''

    def test_conditionals_5(self):
        r'''
        'hri':"{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/agli/ai}",
        'Chri':"{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/cogli/coi}",
        'hri':"{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/agli/ai}",
        'Ci':"ci",

        hri/Chri/hri/Ci  " ai cogli ai ci"
        '''

    def test_conditionals_6(self):
        r'''
        'hri':"{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/agli/ai}",
        'Chri':"{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/cogli/coi}",
        'hri':"{=(?i)([8aeiouxy]|11|dei|gn|ps|s[bcdfglmnpqrtv]|z)/agli/ai}",
        'Ci':"ci",

        :spaces_after
        hri/Chri/hri/Ci  "ai cogli ai ci "
        '''

    def test_conditionals_7(self):
        r'''
        "cp": "{=(?i)(ce|l|fat|[gm]u|nat|pr|po[sr]|prim|ri)/ante/anti}{^}",
        "HAto": "nato",

        :spaces_after
        cp/HAto  "antenato "
        '''

    def test_conditionals_8(self):
        r'''
        "PTVc": "{=(?i)(i|e)/banch/banc}{^}",
        "IEre": "iere",

        PTVc/IEre  " banchiere"
        '''

    def test_conditionals_9(self):
        r'''
        "/R": "{=(?i)(g|a|bu|ce|e|g|l|m|pa|t|vi|volt)/archi/arci}{^}",
        "TEt": "tet",

        R/TEt  " architet"
        '''

    def test_undo_1(self):
        r'''
        "Ocs": "og{^}",
        "PCi": "gi",
        "C*e": "c'è",
        "CHROhr": "mol{^}",
        "To": "to",
        "SOhro": "solo",
        "*": "=undo",
        "SOhre": "sole",

        :spaces_after
        Ocs/PCi/C*e/CHROhr/To  "oggi c'è molto "
        *                      "oggi c'è mol"
        '''

    def test_undo_2(self):
        r'''
        "Ocs": "og{^}",
        "PCi": "gi",
        "C*e": "c'è",
        "CHROhr": "mol{^}",
        "To": "to",
        "SOhro": "solo",
        "*": "{^}{$}{#Control_L(BackSpace)}",
        "SOhre": "sole",

        :spaces_after
        Ocs/PCi/C*e/CHROhr/To  "oggi c'è molto "
        *                      "oggi c'è "
        '''

    def test_delete_last_word1(self):
        r'''
        "Ocs/PCi": "oggi",
        "C*e": "c'è",
        "CHROhr/To": "molto",
        "SOhro": "solo",
        "*": "{^}{$}{#Control_L(BackSpace)}",
        "SOhre": "sole",

        Ocs/PCi/C*e/CHROhr/To/SOhro  " oggi c'è molto solo"
        *                            " oggi c'è molto "
        SOhre                        " oggi c'è molto sole"
        '''

    def test_delete_last_word2(self):
        r'''
        "Ocs/PCi": "oggi",
        "C*e": "c'è",
        "CHROhr/To": "molto",
        "SOhro": "solo",
        "*": "{^}{$}{#Control_L(BackSpace)}",
        "SOhre": "sole",

        :spaces_after
        Ocs/PCi/C*e/CHROhr/To/SOhro  "oggi c'è molto solo "
        *                            "oggi c'è molto "
        SOhre                        "oggi c'è molto sole "
        '''

    def test_delete_last_word3(self):
        r'''
        "Ocs/PCi": "oggi",
        "C*e": "c'è",
        "CHRO": "mo{^}",
        "*": "{^}{$}{#Control_L(BackSpace)}",
        "CHROhr/To": "molto",

        Ocs/PCi/C*e/CHRO  " oggi c'è mo"
        *                 " oggi c'è "
        CHROhr/To         " oggi c'è molto"
        '''

    def test_delete_last_word4(self):
        r'''
        "Ocs/PCi": "oggi",
        "C*e": "c'è",
        "CHRO": "mo{^}",
        "*": "{^}{$}{#Control_L(BackSpace)}",
        "CHROhr/To": "molto",

        :spaces_after
        Ocs/PCi/C*e/CHRO  "oggi c'è mo"
        *                 "oggi c'è "
        CHROhr/To         "oggi c'è molto "
        '''

    def test_delete_redo_1(self):
        r'''
        "Ocs": "og{^}",
        "PCi": "gi",
        "C*e": "c'è",
        "CHROhr": "mol{^}",
        "To": "to",
        "SOhro": "solo",
        "*": "=undo",
        "SOhre": "sole",

        Ocs/PCi/C*e/CHROhr/To/SOhro  " oggi c'è molto solo"
        *                            " oggi c'è molto"
        SOhre                        " oggi c'è molto sole"
        '''

    def test_delete_redo_2(self):
        r'''
        "Ocs": "og{^}",
        "PCi": "gi",
        "C*e": "c'è",
        "CHROhr": "mol{^}",
        "To": "to",
        "SOhro": "solo",
        "*": "=undo",
        "SOhre": "sole",

        :spaces_after
        Ocs/PCi/C*e/CHROhr/To/SOhro  "oggi c'è molto solo "
        *                            "oggi c'è molto "
        SOhre                        "oggi c'è molto sole "
        '''

    def test_delete_redo_3(self):
        r'''
        "Ocs": "og{^}",
        "PCi": "gi",
        "C*e": "c'è",
        "CHROhr": "mol{^}",
        "To": "to",
        "SO": "so{^}",
        "HRo": "lo",
        "*": "=undo",
        "SOhre": "sole",

        :spaces_after
        Ocs/PCi/C*e/CHROhr/To/SO/HRo  "oggi c'è molto solo "
        */*                           "oggi c'è molto "
        SOhre                         "oggi c'è molto sole "
        '''

    def test_extraneous_spaces_1(self):
        r'''
        'S*i':"sì",
        'VR*':"{^},",
        'Ce':"ce",
        'HR*':"l'{^}{$}",
        'ho':"ho",
        'TEOt':"tut{^}",
        'Oo':"{#Control_L(Shift_L(y))}",
        "*": "=undo",
        'Tt*':"tutt'{^}{$}",
        'Ora':"ora",
        'P*':"{^}.{-|}",

        S*i/VR*/Ce/HR*/ho/TEOt/Oo/*/Tt*/Ora/P*  " sì, ce l'ho tutt'ora."
        '''

    def test_extraneous_spaces_2(self):
        r'''
        'S*i':"sì",
        'VR*':"{^},",
        'Ce':"ce",
        'HR*':"l'{^}{$}",
        'ho':"ho",
        'TEOt':"tut{^}",
        'Oo':"{#Control_L(Shift_L(y))}",
        "*": "=undo",
        'Tt*':"tutt'{^}{$}",
        'Ora':"ora",
        'P*':"{^}.{-|}",

        :spaces_after
        S*i/VR*/Ce/HR*/ho/TEOt/Oo/*/Tt*/Ora/P*  "sì, ce l'ho tutt'ora. "
        '''
