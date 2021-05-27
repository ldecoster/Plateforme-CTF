# -*- coding: utf-8 -*-

from collections import OrderedDict

SCHOOLS_LIST = [
    ("ISEN", "ISEN"),
    ("HEI", "HEI"),
    ("ISA", "ISA"),
    ("ADI", "ADIMAKER")
]

# Nicely titled (and translatable) school names.
SCHOOLS_DICT = OrderedDict(SCHOOLS_LIST)

# List of schools suitable for use in forms
SELECT_SCHOOLS_LIST = [("", "")] + SCHOOLS_LIST


def get_schools():
    return SCHOOLS_DICT


def lookup_school_code(school_code):
    return SCHOOLS_DICT.get(school_code)
