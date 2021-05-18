# -*- coding: utf-8 -*-

from collections import OrderedDict

CURSUS_LIST = [
    ("CPG", "Cycle Préparatoire Généraliste"),
    ("CIR", "Cycle Informatique et Réseaux"),
    ("CNB", "Cycle Numérique et Biologique"),
    ("CENT", "Cycle Économie Numérique et Technologies"),
    ("EST", "Cycle Environnement, Science et Technologies"),
    ("BIAST", "Cycle Biologie, Agronomie, Sciences et Technologies"),
    ("CPII", "Cycle Préparatoire intégré ISA"),
    ("ADI", "Adimaker"),
    ("CPI", "Cycle Préparatoire International"),
    ("CPA", "Cycle Préparatoire Adimaker"),
    ("CI1", "Cycle Ingénieur 1ère Année"),
    ("CI2", "Cycle Ingénieur 2ème Année"),
    ("CI3", "Cycle Ingénieur 3ème Année"),
    ("OTH", "Other")
]

# Nicely titled (and translatable) cursus names.
CURSUS_DICT = OrderedDict(CURSUS_LIST)

# List of cursus suitable for use in forms
SELECT_CURSUS_LIST = [("", "")] + CURSUS_LIST


def get_cursus():
    return CURSUS_DICT


def lookup_cursus_code(cursus_code):
    return CURSUS_DICT.get(cursus_code)
