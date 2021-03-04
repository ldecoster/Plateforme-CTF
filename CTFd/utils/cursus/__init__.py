# -*- coding: utf-8 -*-

from collections import OrderedDict

CURSUS_LIST = [
    ("CPG", "Cycle Préparatoire Genéraliste"),
    ("CIR", "Cycle Informatique et Réseaux"),
    ("CNB", "Cycle Numerique et Biologique"),
    ("CENT","Cycle Economie Numerique et Technologies"),
    ("EST", "Cycle Environement, Science et Technologies"),
    ("BIAST","Cycle Biologie ,Agronomie,Sciences et Technologies"),
    ("CPII", "Cycle Preparatoire integré ISA"),
    ("ADI", "Adimaker"),
    ("CPI", "Cycle Preparatoire International"),
    ("CPA", "Cycle Preparatoire Adimaker"),
    ("CI1","Cycle Ingénieur 1ère Année"),
    ("CI2","Cycle Ingénieur 2ème Année"),
    ("CI3","Cycle Ingénieur 3ème Année")

]

# Nicely titled (and translatable) cursus names.
CURSUS_DICT = OrderedDict(CURSUS_LIST)

# List of cursuss suitable for use in forms
SELECT_CURSUS_LIST = [("", "")] + CURSUS_LIST


def get_cursus():
    return CURSUS_DICT


def lookup_cursus_code(cursus_code):
    return CURSUS_DICT.get(cursus_code)
