# -*- coding: utf-8 -*-
"""Tables de reference du site de prestige.

Ce site est SEPARE de l'annuaire de franchises : depot separe, page d'accueil
separee, charte separee. Les tables ci-dessous sont donc recopiees ici plutot
qu'importees — un site qui ne peut pas se construire seul n'est pas separe,
il est juste rangee ailleurs.

Les valeurs sont identiques a celles de l'annuaire, volontairement : deux
sites du meme client qui classeraient en euros differents afficheraient des
ordres differents pour la meme marque.
"""

import math

# cle, fr, en, region, devise
PAYS = [
    ('CA', 'Canada', 'Canada', 'na', 'CAD'),
    ('US', 'Etats-Unis', 'United States', 'na', 'USD'),

    ('FR', 'France', 'France', 'eu-ouest', 'EUR'),
    ('BE', 'Belgique', 'Belgium', 'eu-ouest', 'EUR'),
    ('NL', 'Pays-Bas', 'Netherlands', 'eu-ouest', 'EUR'),
    ('DE', 'Allemagne', 'Germany', 'eu-ouest', 'EUR'),
    ('AT', 'Autriche', 'Austria', 'eu-ouest', 'EUR'),
    ('IE', 'Irlande', 'Ireland', 'eu-ouest', 'EUR'),
    ('GB', 'Royaume-Uni', 'United Kingdom', 'eu-ouest', 'GBP'),
    ('CH', 'Suisse', 'Switzerland', 'eu-ouest', 'CHF'),

    ('ES', 'Espagne', 'Spain', 'eu-sud', 'EUR'),
    ('IT', 'Italie', 'Italy', 'eu-sud', 'EUR'),
    ('PT', 'Portugal', 'Portugal', 'eu-sud', 'EUR'),
    ('GR', 'Grece', 'Greece', 'eu-sud', 'EUR'),

    ('SE', 'Suede', 'Sweden', 'eu-nord', 'SEK'),
    ('DK', 'Danemark', 'Denmark', 'eu-nord', 'DKK'),
    ('NO', 'Norvege', 'Norway', 'eu-nord', 'NOK'),
    ('FI', 'Finlande', 'Finland', 'eu-nord', 'EUR'),

    ('PL', 'Pologne', 'Poland', 'eu-est', 'PLN'),
    ('CZ', 'Tchequie', 'Czechia', 'eu-est', 'CZK'),
    ('RO', 'Roumanie', 'Romania', 'eu-est', 'RON'),
    ('HU', 'Hongrie', 'Hungary', 'eu-est', 'HUF'),
]

REGIONS = [
    ('na', 'Amerique du Nord', 'North America'),
    ('eu-ouest', 'Europe de l\'Ouest', 'Western Europe'),
    ('eu-sud', 'Europe du Sud', 'Southern Europe'),
    ('eu-nord', 'Europe du Nord', 'Northern Europe'),
    ('eu-est', 'Europe centrale et de l\'Est', 'Central and Eastern Europe'),
]

# TAUX DE REFERENCE, FIGES, POUR LE CLASSEMENT UNIQUEMENT. Ils ne servent
# JAMAIS a afficher un montant : chaque maison s'affiche dans SA devise.
TAUX_EUR = {
    'EUR': 1.0, 'USD': 0.92, 'CAD': 0.68, 'GBP': 1.17, 'CHF': 1.05,
    'PLN': 0.23, 'SEK': 0.088, 'DKK': 0.134, 'NOK': 0.086,
    'CZK': 0.040, 'RON': 0.20, 'HUF': 0.0025,
}

# Le luxe ne s'implante pas ou s'implante l'economique. On ne tire donc pas
# les pays d'implantation dans la liste complete a poids egaux : une maison
# de prestige ouvre a Paris, Londres, New York, Geneve, Rome — pas d'abord
# a Bucarest. Le poids est ici celui du marche du LUXE, pas de la population.
POIDS_PAYS = {
    'FR': 40, 'US': 38, 'IT': 30, 'GB': 28, 'CH': 22, 'ES': 20, 'GR': 14,
    'PT': 10, 'AT': 10, 'DE': 10, 'CA': 9, 'BE': 5, 'NL': 5, 'IE': 4,
    'DK': 4, 'SE': 3, 'NO': 3, 'CZ': 3, 'HU': 2, 'PL': 2, 'FI': 2, 'RO': 1,
}


def slug(t):
    out = []
    for c in t.lower():
        if c.isalnum():
            out.append(c)
        elif out and out[-1] != '-':
            out.append('-')
    return ''.join(out).strip('-')


def arrondi_utile(v):
    """Arrondir a ~3 chiffres significatifs.

    Une devise faible produit des nombres a sept chiffres : les arrondir au
    millier laisserait « 41 237 000 », ce qu'aucune maison n'ecrit.
    """
    if v <= 0:
        return 0
    ordre = 10 ** max(0, int(math.floor(math.log10(v))) - 2)
    return int(round(v / ordre) * ordre)


def arrondi_prix(v):
    """Arrondir un PRIX DE NUITEE, qui ne s'ecrit pas comme un investissement.

    Un tarif s'affiche a la dizaine (« 940 »), jamais « 937 », et jamais
    arrondi au millier non plus — ce serait perdre l'information.
    """
    if v <= 0:
        return 0
    if v < 1000:
        return int(round(v / 10.0) * 10)
    if v < 100000:
        return int(round(v / 100.0) * 100)
    return arrondi_utile(v)


def pays_ouverts(r, origine):
    """Ou la maison est deja presente. Le pays d'origine en fait toujours
    partie, et le tirage suit le poids du marche du luxe."""
    cles = [p for p in POIDS_PAYS if p != origine]
    poids = [POIDS_PAYS[p] for p in cles]
    combien = min(len(cles), r.randint(2, 11))
    tires = []
    dispo = list(zip(cles, poids))
    for _ in range(combien):
        total = sum(w for _c, w in dispo)
        if total <= 0:
            break
        seuil = r.uniform(0, total)
        acc = 0
        for i, (c, w) in enumerate(dispo):
            acc += w
            if acc >= seuil:
                tires.append(c)
                dispo.pop(i)
                break
    ordre = [p[0] for p in PAYS]
    return sorted(set([origine] + tires), key=ordre.index)
