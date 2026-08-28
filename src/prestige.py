# -*- coding: utf-8 -*-
"""Les maisons de prestige : donnees du site noir.

SITE SEPARE, et pas un filtre « 5 etoiles » sur la section hotellerie. La
raison est la meme que celle qui a sorti l'hotellerie de l'annuaire
generaliste, un cran plus loin : au sommet de la gamme, le metier ne se
mesure plus dans les memes unites.

  - on n'y signe presque jamais une franchise. Le proprietaire garde ses
    murs et confie l'exploitation au groupe : c'est un CONTRAT DE GESTION.
  - la remuneration n'est donc pas une redevance, c'est un COUPLE :
    des honoraires de base sur le chiffre d'affaires TOTAL, plus des
    honoraires d'incitation sur le RESULTAT BRUT D'EXPLOITATION. Le premier
    tombe meme quand l'hotel perd de l'argent, le second non — et c'est tout
    le sujet d'une negociation de gestion.
  - dans l'autre sens, le groupe peut APPORTER de l'argent au proprietaire
    pour emporter le contrat (le « key money »). Un franchiseur ne fait
    jamais cela.
  - un budget de PRE-OUVERTURE et des honoraires de services techniques
    s'ajoutent, par cle, avant meme la premiere nuitee vendue.
  - et la question du proprietaire n'est plus « combien ca coute », c'est
    « a quel prix moyen de la nuitee cette marque me positionne-t-elle ».

Mis dans la meme liste que l'economique, tout cela produit des colonnes
vides sur les trois quarts des lignes, et un filtre par redevance qui
compare un pourcentage de chiffre d'affaires a un pourcentage de resultat.
Ce ne sont pas les memes nombres.

Tout ce qui suit est FICTIF. Aucun groupe reel, aucune maison reelle, aucun
chiffre reel. Les montants sont tires dans les bandes de la distinction
visee, avec une graine fixe : deux reconstructions donnent le meme fichier.
"""

import hashlib
import json
import os
import random

from reference import (PAYS, REGIONS, TAUX_EUR, arrondi_prix, arrondi_utile,
                       pays_ouverts, slug)

ICI = os.path.dirname(os.path.abspath(__file__))
from chemins import dossier_pages   # noqa: E402
DEMO = dossier_pages(ICI)

# ---------------------------------------------------------------------------
# LES DISTINCTIONS. Au-dessus du « segment » hotelier ordinaire, le metier
# parle par TYPE DE MAISON, parce que deux adresses cinq etoiles de tailles
# opposees ne se gerent pas pareil : un palace urbain de 200 cles vit de ses
# banquets et de sa restauration, une maison de 40 cles vit de son taux
# d'occupation et de son prix moyen. La table choisit les fourchettes ; elle
# n'est pas plaquee apres coup sur des chiffres tires au hasard.
#
# cle, fr, en, resume fr, resume en,
#   investissement par cle (EUR, hors foncier) bas/haut,
#   taille acceptee bas/haut (cles),
#   prix moyen de la nuitee (EUR) bas/haut,
#   part de suites (%) bas/haut,
#   points de restauration bas/haut
# ---------------------------------------------------------------------------
DISTINCTIONS = [
    ('palace', 'Palace urbain', 'City palace',
     'Grande adresse de centre-ville : restauration signee, salons de '
     'reception, spa complet, service continu.',
     'Landmark city address: signature dining, function salons, full spa, '
     'round-the-clock service.',
     620000, 1250000, 90, 260, 750, 1900, 18, 40, 3, 6),
    ('maison', 'Maison de luxe', 'Luxury house',
     'Petite unite, moins de cent cles, ou le personnel connait le nom du '
     'client avant son arrivee.',
     'A small property, under one hundred keys, where the staff know the '
     'guest\'s name before arrival.',
     700000, 1500000, 24, 90, 900, 2600, 25, 55, 1, 3),
    ('resort', 'Resort de prestige', 'Prestige resort',
     'Bord de mer ou montagne, sejours longs, plusieurs tables, activites '
     'et clientele familiale haut de gamme.',
     'Seaside or mountain, longer stays, several restaurants, activities '
     'and high-end family clientele.',
     480000, 1050000, 80, 320, 650, 1800, 20, 45, 3, 7),
    ('domaine', 'Domaine et demeure historique', 'Estate and historic house',
     'Chateau, manoir ou domaine viticole converti : le batiment est le '
     'produit, et il impose ses contraintes.',
     'A converted chateau, manor or wine estate: the building is the '
     'product, and it sets the constraints.',
     560000, 1200000, 20, 80, 700, 2200, 30, 60, 2, 4),
    ('design', 'Lifestyle de prestige', 'Prestige lifestyle',
     'Adresse d\'auteur : architecture signee, bar de destination, '
     'programmation culturelle, clientele plus jeune.',
     'A design-led address: named architecture, destination bar, cultural '
     'programme, younger clientele.',
     450000, 900000, 50, 160, 550, 1400, 12, 30, 2, 5),
]

# ---------------------------------------------------------------------------
# LES MODES D'EXPLOITATION. Ce ne sont PAS les contrats de la section
# hotellerie : le vocabulaire change, et surtout la base de calcul change.
#
# cle, fr, en, base de remuneration fr, base en, explication fr, explication en
# ---------------------------------------------------------------------------
MODES = [
    ('gestion', 'Contrat de gestion', 'Management contract',
     'Honoraires de base sur le chiffre d\'affaires total, plus honoraires '
     'd\'incitation sur le resultat brut d\'exploitation',
     'Base fee on total revenue, plus incentive fee on gross operating '
     'profit',
     'Le groupe exploite la maison pour le compte du proprietaire : il '
     'recrute le directeur general, engage les equipes, tient les comptes '
     'd\'exploitation. Le proprietaire porte l\'actif et le resultat.',
     'The group operates the house on the owner\'s behalf: it appoints the '
     'general manager, hires the teams and runs the operating accounts. The '
     'owner carries the asset and the result.'),
    ('affiliation', 'Affiliation a une collection', 'Collection affiliation',
     'Redevance sur le chiffre d\'affaires hebergement, plus frais de '
     'distribution',
     'Royalty on rooms revenue, plus distribution fees',
     'La maison GARDE SON NOM et son equipe, et rejoint une collection qui '
     'lui apporte la distribution, la clientele fidelisee et la caution. '
     'C\'est la porte d\'entree des proprietaires independants.',
     'The house KEEPS ITS OWN NAME and team, and joins a collection that '
     'brings distribution, a loyal clientele and endorsement. This is the '
     'usual route for independent owners.'),
    ('franchise', 'Franchise de marque', 'Brand franchise',
     'Redevance sur le chiffre d\'affaires hebergement',
     'Royalty on rooms revenue',
     'Le proprietaire exploite lui-meme sous la marque. Rare a ce niveau de '
     'gamme, et reserve aux exploitants qui ont deja une direction '
     'hoteliere en propre.',
     'The owner operates under the brand. Rare at this level, and reserved '
     'for owners who already have their own hotel management.'),
    ('location', 'Bail', 'Lease',
     'Loyer fixe ou indexe sur le chiffre d\'affaires',
     'Fixed or revenue-indexed rent',
     'Le groupe loue les murs et exploite a ses risques. Le proprietaire '
     'percoit un loyer et sort de l\'exploitation.',
     'The group leases the building and operates at its own risk. The owner '
     'receives a rent and steps out of operations.'),
]

# Un palace ne se franchise pas : la marque ne confie pas a un tiers le seul
# endroit ou elle se juge. A l'inverse, une demeure historique se met
# rarement en gestion complete — le proprietaire est souvent la famille.
MODES_PAR_DISTINCTION = {
    'palace': ['gestion', 'location'],
    'maison': ['affiliation', 'gestion'],
    'resort': ['gestion', 'franchise'],
    'domaine': ['affiliation', 'gestion'],
    'design': ['gestion', 'franchise', 'affiliation'],
}

# Duree, en annees. Une gestion est longue : le groupe y met sa direction
# generale et amortit un budget de pre-ouverture. Une affiliation est courte
# et se resilie — c'est ce qui la rend acceptable a un independant.
DUREE = {
    'gestion': (20, 30),
    'affiliation': (5, 10),
    'franchise': (15, 20),
    'location': (15, 25),
}

# Honoraires de GESTION. Base = % du chiffre d'affaires TOTAL. Incitation =
# % du resultat brut d'exploitation. Les deux ne se comparent pas et ne
# s'additionnent pas — la page ne les additionne nulle part.
HONORAIRES_BASE = (1.5, 3.5)
HONORAIRES_INCITATION = (6.0, 12.0)

# Redevance d'AFFILIATION et de FRANCHISE : % du chiffre d'affaires
# hebergement seul. Une affiliation coute moins cher qu'une franchise, et
# c'est normal : elle apporte moins.
REDEVANCE = {'affiliation': (2.5, 5.0), 'franchise': (5.0, 8.0)}

# Ce que le groupe met en face, a ce niveau de gamme. Rien a voir avec la
# liste de la section hotellerie : ici la centrale de reservation est un
# minimum, pas un argument.
PRESTATIONS = [
    ('direction', 'Direction generale et encadrement',
     'General manager and senior team'),
    ('chef', 'Chef executif et concept de restauration',
     'Executive chef and dining concept'),
    ('conciergerie', 'Conciergerie et service d\'etage continu',
     'Concierge and 24-hour in-room service'),
    ('distribution', 'Distribution luxe et agences de voyages de prestige',
     'Luxury distribution and prestige travel agencies'),
    ('reconnaissance', 'Programme de reconnaissance client',
     'Guest recognition programme'),
    ('tarifaire', 'Gestion tarifaire et prevision de la demande',
     'Revenue management and demand forecasting'),
    ('spa', 'Concept de spa et de bien-etre', 'Spa and wellness concept'),
    ('arts', 'Arts de la table et approvisionnement',
     'Tableware and sourcing'),
    ('architecture', 'Direction artistique et suivi d\'architecture',
     'Art direction and architectural supervision'),
    ('preouverture', 'Equipe de pre-ouverture et recrutement',
     'Pre-opening team and recruitment'),
    ('residences', 'Commercialisation des residences de marque',
     'Branded residences sales'),
]

# ---------------------------------------------------------------------------
# LES GROUPES ET LEURS MAISONS. Neuf groupes fictifs, vingt-cinq maisons.
#
# Les trois premieres lignes reprennent les marques de luxe qui figuraient
# dans la section hotellerie : elles n'y sont plus, elles sont ICI. Une
# marque ne peut pas etre a deux endroits — sinon le total du site et le
# total de la section se contredisent, et le client compte deux fois.
#
# Un groupe ne porte jamais deux maisons dans la meme distinction.
#
# groupe -> (pays, [(maison, distinction, resume fr, resume en)])
# ---------------------------------------------------------------------------
GROUPES = {
    'Cassiopee Hospitality': ('CH', [
        ('Cassiopee Collection', 'palace',
         'Palaces de ville et adresses de villegiature historique',
         'City palaces and historic resort addresses'),
        ('Cassiopee Maison Privee', 'maison',
         'Moins de soixante cles, majordome d\'etage, table confidentielle',
         'Under sixty keys, floor butler, private dining'),
        ('Cassiopee Rivages', 'resort',
         'Resorts de bord de mer, spa marin et ecole de voile',
         'Seaside resorts with marine spa and sailing school'),
    ]),
    'Rivermark Hotels': ('US', [
        ('Rivermark Signature', 'palace',
         'Adresses de prestige en capitale, conciergerie et salons prives',
         'Prestige capital-city addresses, concierge and private salons'),
        ('Rivermark Reserve', 'resort',
         'Domaines de villegiature, golf et grandes suites familiales',
         'Resort estates with golf and large family suites'),
        ('Rivermark Atelier', 'design',
         'Immeubles reconvertis, bar de destination, galerie permanente',
         'Converted buildings, destination bar, permanent gallery'),
    ]),
    'Kestrel Hospitality': ('GB', [
        ('Kestrel Manor', 'domaine',
         'Manoirs et domaines, table gastronomique et chasse',
         'Manor houses and estates, fine dining and country pursuits'),
        ('Kestrel Row', 'design',
         'Maisons de ville georgiennes reunies, club de membres',
         'Joined Georgian townhouses with a members\' club'),
    ]),
    'Maison Valmore': ('FR', [
        ('Valmore Palaces', 'palace',
         'Palaces classes, brigade de cuisine etoilee, galerie de boutiques',
         'Listed palaces, starred kitchen brigade, retail gallery'),
        ('Valmore Demeures', 'domaine',
         'Chateaux et domaines viticoles convertis, table du terroir',
         'Converted chateaux and wine estates, regional dining'),
        ('Valmore Rivage', 'resort',
         'Resorts mediterraneens, plage privee et spa de vignoble',
         'Mediterranean resorts, private beach and vineyard spa'),
    ]),
    'Aurelio Collezione': ('IT', [
        ('Aurelio Palazzi', 'palace',
         'Palais urbains restaures, cour interieure et terrasse panoramique',
         'Restored urban palazzi with courtyard and rooftop terrace'),
        ('Aurelio Dimore', 'maison',
         'Demeures de quarante cles, service de maison, cuisine ouverte',
         'Forty-key houses, house service, open kitchen'),
        ('Aurelio Coste', 'resort',
         'Resorts de la cote et des lacs, jardins historiques',
         'Coastal and lakeside resorts with historic gardens'),
    ]),
    'Orenda Hotels': ('CA', [
        ('Orenda Grand', 'palace',
         'Grands hotels de gare et de centre-ville, salles de reception',
         'Grand station and downtown hotels with ballrooms'),
        ('Orenda Lodges', 'domaine',
         'Lodges de montagne et de riviere, guides et grandes cheminees',
         'Mountain and river lodges with guides and great fireplaces'),
        ('Orenda Loft', 'design',
         'Entrepots reconvertis, ateliers d\'artistes et cafe torrefacteur',
         'Converted warehouses, artist studios and roastery cafe'),
    ]),
    'Grupo Alvear': ('ES', [
        ('Alvear Palacios', 'palace',
         'Palais andalous et madrilenes, patio, azulejos, spa arabe',
         'Andalusian and Madrid palaces, patio, azulejos, hammam spa'),
        ('Alvear Casas', 'maison',
         'Maisons de ville de trente cles, terrasse et table du marche',
         'Thirty-key townhouses with terrace and market kitchen'),
        ('Alvear Costa', 'resort',
         'Resorts des iles et de la cote, criques privees',
         'Island and coastal resorts with private coves'),
    ]),
    'Lysander Hotels': ('GR', [
        ('Lysander Islands', 'resort',
         'Resorts insulaires, villas avec piscine, port d\'attache',
         'Island resorts, pool villas and a home marina'),
        ('Lysander Maisons', 'maison',
         'Maisons de village restaurees, moins de quarante cles',
         'Restored village houses, under forty keys'),
    ]),
    'Bergwald Hotels': ('AT', [
        ('Bergwald Residenz', 'palace',
         'Grands hotels alpins historiques, salles de bal et thermes',
         'Historic alpine grand hotels with ballrooms and thermal baths'),
        ('Bergwald Almhof', 'domaine',
         'Fermes d\'alpage restaurees, ski aux pieds, table de montagne',
         'Restored alpine farmhouses, ski-in ski-out, mountain kitchen'),
        ('Bergwald Atelier', 'design',
         'Architecture contemporaine en bois, sauna panoramique',
         'Contemporary timber architecture with panoramic sauna'),
    ]),
}

# Tranches d'investissement PAR CLE, en euros de reference. Les bornes ne
# sont pas celles de la section hotellerie : ici la premiere tranche
# commence la ou l'autre se terminait.
TRANCHES_CLE = [
    ('p1', 'Moins de 600 000 EUR la cle', 'Under EUR 600,000 per key',
     0, 600000),
    ('p2', '600 000 a 900 000 EUR la cle',
     'EUR 600,000 to 900,000 per key', 600000, 900000),
    ('p3', '900 000 a 1,2 M EUR la cle',
     'EUR 900,000 to 1.2M per key', 900000, 1200000),
    ('p4', 'Plus de 1,2 M EUR la cle', 'Over EUR 1.2M per key',
     1200000, 10 ** 13),
]

# Tailles proposees au filtre. « Mon actif fait N cles, quelles maisons le
# prennent » — donc N doit tomber DANS la fourchette acceptee.
TAILLES = [30, 50, 80, 120, 180, 250]


def tranche_cle(v_eur):
    for cle, _fr, _en, bas, haut in TRANCHES_CLE:
        if bas <= v_eur < haut:
            return cle
    return 'p4'


def construire():
    devise_de = dict((p[0], p[4]) for p in PAYS)
    region_de = dict((p[0], p[3]) for p in PAYS)
    dist_de = dict((d[0], d) for d in DISTINCTIONS)
    fiches = []

    for groupe, (origine, maisons) in GROUPES.items():
        for nom, dist, rfr, ren in maisons:
            s = slug(nom)
            graine = int(hashlib.md5(s.encode('utf-8')).hexdigest()[:8], 16)
            r = random.Random(graine)
            (_c, _fr, _en, _dfr, _den, ibas, ihaut, kbas, khaut,
             abas, ahaut, sbas, shaut, rbas, rhaut) = dist_de[dist]

            dev = devise_de[origine]
            taux = TAUX_EUR[dev]

            # La taille acceptee : une fourchette DANS la fourchette de la
            # distinction, jamais l'inverse.
            cles_min = r.randint(kbas, kbas + int((khaut - kbas) * .35))
            cles_max = min(khaut, int(cles_min * r.uniform(1.5, 2.4)))

            # L'investissement se tire PAR CLE en euros de reference, puis se
            # convertit. Le cout du projet ne se tire pas : il se CALCULE.
            eur_cle_bas = r.uniform(ibas, ibas + (ihaut - ibas) * .5)
            eur_cle_haut = min(ihaut, eur_cle_bas * r.uniform(1.15, 1.5))
            cle_bas = arrondi_utile(eur_cle_bas / taux)
            cle_haut = arrondi_utile(eur_cle_haut / taux)
            projet_bas = cle_bas * cles_min
            projet_haut = cle_haut * cles_max

            # Le prix moyen de la nuitee. C'est la question du proprietaire :
            # a quel niveau cette marque me positionne-t-elle. Il se tire
            # dans la bande de la distinction, et il se DEPLACE avec
            # l'investissement — une maison ou on met 1,4 M la cle ne se
            # vend pas au bas de sa bande.
            place = (eur_cle_bas - ibas) / float(ihaut - ibas)
            centre = abas + (ahaut - abas) * (.25 + .5 * place)
            adr_bas = arrondi_prix(centre * r.uniform(.85, .95) / taux)
            adr_haut = arrondi_prix(centre * r.uniform(1.25, 1.55) / taux)

            possibles = MODES_PAR_DISTINCTION[dist]
            principal = possibles[0]
            autres = [m for m in possibles[1:] if r.random() < .5]
            modes = [principal] + autres
            d_bas, d_haut = DUREE[principal]
            duree = r.randint(d_bas, d_haut)

            # Les honoraires de GESTION n'existent que s'il y a gestion, et
            # la redevance n'existe que s'il y a franchise ou affiliation.
            # Une colonne remplie « pour ne pas laisser de vide » est un
            # chiffre invente qui se lira comme une offre.
            base_pct = incit_pct = None
            if 'gestion' in modes:
                base_pct = round(r.uniform(*HONORAIRES_BASE), 1)
                incit_pct = round(r.uniform(*HONORAIRES_INCITATION), 1)
            redev_pct = None
            for m in ('franchise', 'affiliation'):
                if m in modes:
                    redev_pct = round(r.uniform(*REDEVANCE[m]), 1)
                    break

            # Le key money : le groupe APPORTE de l'argent au proprietaire
            # pour emporter le contrat. Cela n'a de sens que sur une gestion
            # — un franchiseur ne paie pas pour etre franchiseur. Et cela
            # n'arrive pas toujours : c'est une concession de negociation.
            key_money = 0
            if 'gestion' in modes and r.random() < .45:
                key_money = arrondi_utile(r.uniform(15000, 70000) / taux)

            services_tech = arrondi_utile(r.uniform(4000, 11000) / taux)
            preouverture = arrondi_utile(r.uniform(12000, 32000) / taux)

            creation = r.randint(1852, 2012)
            debut = min(2024, creation + r.randint(4, 30))

            # Le reseau : on tire le nombre de MAISONS et la taille MOYENNE,
            # et on multiplie. Tires a part, on obtiendrait des collections
            # de 30 maisons et 400 cles, soit treize chambres l'unite.
            maisons_n = r.randint(4, 68)
            taille_moy = r.randint(cles_min, cles_max)
            cles_reseau = maisons_n * taille_moy

            suites_pct = r.randint(sbas, shaut)
            tables = r.randint(rbas, rhaut)
            spa_m2 = arrondi_utile(r.uniform(300, 3200)) if r.random() < .9 else 0
            residences = r.random() < .35

            presta = ['direction', 'distribution', 'tarifaire', 'preouverture']
            for p in ('chef', 'conciergerie', 'reconnaissance', 'spa', 'arts',
                      'architecture'):
                if r.random() < .72:
                    presta.append(p)
            if residences:
                presta.append('residences')

            fiches.append({
                'id': s,
                'nom': nom,
                'groupe': groupe,
                'distinction': dist,
                'resume': {'fr': rfr, 'en': ren},
                'pays_origine': origine,
                'region': region_de[origine],
                'devise': dev,
                'cles': {'min': cles_min, 'max': cles_max},
                'investissement_cle': {
                    'bas': cle_bas, 'haut': cle_haut,
                    'eur_bas': int(round(eur_cle_bas)),
                    'tranche': tranche_cle(eur_cle_bas),
                },
                'projet': {'bas': projet_bas, 'haut': projet_haut},
                'nuitee': {'bas': adr_bas, 'haut': adr_haut},
                'honoraires': {'base': base_pct, 'incitation': incit_pct},
                'redevance': redev_pct,
                'key_money_cle': key_money,
                'services_techniques_cle': services_tech,
                'preouverture_cle': preouverture,
                'modes': modes,
                'duree_contrat': duree,
                'montee_en_puissance_mois': r.choice([18, 24, 30, 36]),
                'renovation_ans': r.choice([7, 8, 10, 12]),
                'suites_pct': suites_pct,
                'tables': tables,
                'spa_m2': spa_m2,
                'residences_de_marque': residences,
                'annee_creation': creation,
                'annee_premiere_gestion': debut,
                'reseau': {'maisons': maisons_n, 'cles': cles_reseau,
                           'taille_moyenne': taille_moy},
                'pays': pays_ouverts(r, origine),
                'prestations': presta,
                'demonstration': True,
            })

    ordre_dist = [d[0] for d in DISTINCTIONS]
    fiches.sort(key=lambda f: (ordre_dist.index(f['distinction']), f['nom']))
    return fiches


def ecrire(fiches):
    if not os.path.isdir(DEMO):
        os.makedirs(DEMO)
    data = {
        'avertissement': (
            'Fiches de DEMONSTRATION. Groupes et maisons fictifs, chiffres '
            'tires dans les bandes de la distinction visee. Aucun groupe '
            'reel, aucune maison reelle, aucun chiffre reel.'),
        'note_taux': (
            'Le classement et le filtre par investissement se font sur une '
            'valeur de reference en euros (taux figes). Chaque maison '
            's\'affiche dans la devise de son pays.'),
        'note_honoraires': (
            'Les honoraires de base portent sur le chiffre d\'affaires '
            'TOTAL, les honoraires d\'incitation sur le RESULTAT BRUT '
            'D\'EXPLOITATION, la redevance sur le chiffre d\'affaires '
            'HEBERGEMENT seul. Ces trois pourcentages ne s\'additionnent '
            'pas et ne se comparent pas entre eux.'),
        'distinctions': [{'cle': d[0], 'fr': d[1], 'en': d[2],
                          'desc_fr': d[3], 'desc_en': d[4]}
                         for d in DISTINCTIONS],
        'modes': [{'cle': m[0], 'fr': m[1], 'en': m[2], 'base_fr': m[3],
                   'base_en': m[4], 'desc_fr': m[5], 'desc_en': m[6]}
                  for m in MODES],
        'prestations': [{'cle': p[0], 'fr': p[1], 'en': p[2]}
                        for p in PRESTATIONS],
        'pays': [{'cle': p[0], 'fr': p[1], 'en': p[2], 'region': p[3],
                  'devise': p[4]} for p in PAYS],
        'regions': [{'cle': x[0], 'fr': x[1], 'en': x[2]} for x in REGIONS],
        'tranches': [{'cle': t[0], 'fr': t[1], 'en': t[2], 'bas': t[3],
                      'haut': t[4]} for t in TRANCHES_CLE],
        'tailles': TAILLES,
        'groupes': [{'nom': g, 'pays': p, 'maisons': [m[0] for m in ms]}
                    for g, (p, ms) in GROUPES.items()],
        'fiches': fiches,
    }
    chemin = os.path.join(DEMO, 'prestige.json')
    with open(chemin, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    return chemin


COLONNES = [
    'maison', 'groupe', 'distinction', 'resume_fr', 'resume_en',
    'pays_origine', 'devise', 'cles_min', 'cles_max',
    'investissement_cle_bas', 'investissement_cle_haut', 'nuitee_bas',
    'nuitee_haut', 'honoraires_base_pct', 'honoraires_incitation_pct',
    'redevance_pct', 'key_money_par_cle', 'services_techniques_par_cle',
    'preouverture_par_cle', 'modes', 'duree_contrat_annees',
    'montee_en_puissance_mois', 'cycle_renovation_ans', 'suites_pct',
    'points_de_restauration', 'spa_m2', 'residences_de_marque',
    'annee_creation', 'annee_premiere_gestion', 'reseau_maisons',
    'reseau_taille_moyenne', 'pays_ouverts', 'prestations',
]


def modele_csv(fiches):
    import csv
    chemin = os.path.join(ICI, 'import-modele-prestige.csv')
    with open(chemin, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(COLONNES)
        for fi in fiches[:2]:
            w.writerow([
                fi['nom'], fi['groupe'], fi['distinction'], fi['resume']['fr'],
                fi['resume']['en'], fi['pays_origine'], fi['devise'],
                fi['cles']['min'], fi['cles']['max'],
                fi['investissement_cle']['bas'],
                fi['investissement_cle']['haut'],
                fi['nuitee']['bas'], fi['nuitee']['haut'],
                fi['honoraires']['base'] if fi['honoraires']['base'] else '',
                (fi['honoraires']['incitation']
                 if fi['honoraires']['incitation'] else ''),
                fi['redevance'] if fi['redevance'] else '',
                fi['key_money_cle'], fi['services_techniques_cle'],
                fi['preouverture_cle'], '|'.join(fi['modes']),
                fi['duree_contrat'], fi['montee_en_puissance_mois'],
                fi['renovation_ans'], fi['suites_pct'], fi['tables'],
                fi['spa_m2'], 'oui' if fi['residences_de_marque'] else 'non',
                fi['annee_creation'], fi['annee_premiere_gestion'],
                fi['reseau']['maisons'], fi['reseau']['taille_moyenne'],
                '|'.join(fi['pays']), '|'.join(fi['prestations']),
            ])
    return chemin


if __name__ == '__main__':
    fi = construire()
    c1 = ecrire(fi)
    c2 = modele_csv(fi)
    print('%s  (%d octets)' % (c1, os.path.getsize(c1)))
    print('%s  (%d octets)' % (c2, os.path.getsize(c2)))
    print('%d maisons, %d groupes, %d distinctions'
          % (len(fi), len(GROUPES), len(DISTINCTIONS)))
    for d in DISTINCTIONS:
        n = sum(1 for f in fi if f['distinction'] == d[0])
        print('  %-32s %2d maisons' % (d[1], n))
    for m in MODES:
        n = sum(1 for f in fi if m[0] in f['modes'])
        print('  mode %-24s %2d maisons' % (m[0], n))
    km = [f for f in fi if f['key_money_cle']]
    print('  key money sur %d maisons, toutes en gestion : %s'
          % (len(km), all('gestion' in f['modes'] for f in km)))
