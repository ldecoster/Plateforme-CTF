# -*- coding: utf-8 -*-

from collections import OrderedDict

SPECIALISATIONS_LIST = [
    ## ISEN
    ("RCMOC","Réseaux, Communication Mobiles et Objets Connectés"),
    ("SNE","Systèmes Numérique Embarqués"),
    ("IAMN","Ingénierie des Affaires dans le Monde du Numérique"),
    ("RM",  "Robotique Mobile"),
    ("DLBDCC","Dévelopement Logiciel,Big data et Cloud Computing"),
    ("BD", "Big Data"),
    ("TMS","Technologies Médicales et de Santé"),
    ("BE","Biomédical & E-santé"),
    ("BN","Bio-Nanotechs"),
    ("NM", "NanoÉlectronique et Micro-Méca-Tronique"),
    ("CS","Cybersécurité"),
    ("IA","Intelligence Artificielle"),
    ("DSD","Dévelopement des Systèmes d'Information"),
    ("FN","Finance"),
    ("ME","Mobilité Électronique"),
    ("EN","Énegie"),
    ("SE","Smart Energies"),
    ("NEDD","Numérique, Environnement et developement durable"),
    ##HEI
    ("BTP", "Batiment Travauc Public"),
    ("BAA", "Batiment Amenagement Architecture"),
    ("MEOF", "Management d'Entreprise Option Finance"),
    ("CM", "Conception Mécanique"),
    ("ESEA", "Energie Systèmes Electriques Automatisés"),
    ("IMS", "Ingénierie Médicale et Santé"),
    ("ITI", "Informatique et Technologies de l'Information"),
    ("CITE", "Chimie Innovante et Transition Ecologique"),
    ("SC", "Smartcities"),
    ("TIMT", "Technologies Innovation et Management Textile"),
    ("EIE", "Entreprenariat, Intreprenariat, Extraprenariat"),
    ("MOIL", "Management des Opérations Industrielles et Logistiques"),
    ("MR", "Mecatronique et Robotique"),

    #ISA
    ("AGI", "Agriculture"),
    ("AGO", "Agroalimentaire"),
    ("ENV", "Environnement"),
    ("MKT", "Marketing"),
]

# Nicely titled (and translatable) specialisation names.
SPECIALISATIONS_DICT = OrderedDict(SPECIALISATIONS_LIST)

# List of specialisations suitable for use in forms
SELECT_SPECIALISATIONS_LIST = [("", "")] + SPECIALISATIONS_LIST


def get_specialisations():
    return SPECIALISATIONS_DICT


def lookup_specialisation_code(specialisation_code):
    return SPECIALISATIONS_DICT.get(specialisation_code)
