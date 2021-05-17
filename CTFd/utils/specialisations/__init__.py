# -*- coding: utf-8 -*-

from collections import OrderedDict

SPECIALISATIONS_LIST = [
    # ISEN
    ("RCMOC", "Réseaux, Communications Mobiles et Objets Connectés"),
    ("SNE", "Systèmes Numérique Embarqués"),
    ("IAMN", "Ingénierie des Affaires dans le Monde du Numérique"),
    ("RM",  "Robotique Mobile"),
    ("DLBDCC", "Développement Logiciel, Big Data et Cloud Computing"),
    ("BD", "Big Data"),
    ("TMS", "Technologies Médicales et de Santé"),
    ("BE", "Biomédical & E-santé"),
    ("BN", "Bio-Nanotechs"),
    ("NM", "Nanoélectronique et Micro-Méca-Tronique"),
    ("CS", "Cybersécurité"),
    ("IA", "Intelligence Artificielle"),
    ("DSD", "Développement des Systèmes d'Information"),
    ("FN", "Finance"),
    ("ME", "Mobilité Électronique"),
    ("EN", "Énergie"),
    ("SE", "Smart Energies"),
    ("NEDD", "Numérique, Environnement et Développement Durable"),
    # HEI
    ("BTP", "Bâtiment Travaux Public"),
    ("BAA", "Bâtiment Aménagement Architecture"),
    ("MEOF", "Management d'Entreprise Option Finance"),
    ("CM", "Conception Mécanique"),
    ("ESEA", "Énergie Systèmes Électriques et Automatisés"),
    ("IMS", "Ingénierie Médicale et Santé"),
    ("ITI", "Informatique et Technologies de l'Information"),
    ("CITE", "Chimie Innovante et Transition Écologique"),
    ("SC", "Smart Cities"),
    ("TIMT", "Technologies Innovation et Management Textile"),
    ("EIE", "Entreprenariat Intrapreneuriat Extrapreneuriat"),
    ("MOIL", "Management des Opérations Industrielles et Logistiques"),
    ("MR", "Mécatronique et Robotique"),
    # ISA
    ("AGI", "Agriculture"),
    ("AGO", "Agroalimentaire"),
    ("ENV", "Environnement"),
    ("MKT", "Marketing"),
    # ADIMAKER
    ("ADI", "Adimaker"),
    # Other
    ("OTH", "Other")
]

# Nicely titled (and translatable) specialisation names.
SPECIALISATIONS_DICT = OrderedDict(SPECIALISATIONS_LIST)

# List of specialisations suitable for use in forms
SELECT_SPECIALISATIONS_LIST = [("", "")] + SPECIALISATIONS_LIST


def get_specialisations():
    return SPECIALISATIONS_DICT


def lookup_specialisation_code(specialisation_code):
    return SPECIALISATIONS_DICT.get(specialisation_code)
