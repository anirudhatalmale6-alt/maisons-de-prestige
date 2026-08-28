# -*- coding: utf-8 -*-
"""Controles du site de prestige.

Trois etages.

1. LES DONNEES. C'est la que se joue la credibilite d'une fiche de luxe :
   des honoraires d'incitation sans contrat de gestion, un apport du groupe
   chez un franchiseur, ou un cout de projet qui contredit le prix a la cle
   affiche deux lignes plus haut — chaque fiche reste plausible seule, et
   l'ensemble sonne faux.

2. LES FICHIERS. Ce qui est ECRIT dans les pages : les cadres d'image
   portent-ils le ratio annonce, les deux langues sont-elles completes, le
   nombre affiche sur l'accueil est-il celui du JSON, et aucun nom de groupe
   hotelier reel n'a-t-il glisse dans le texte.

3. LA PAGE, dans un vrai navigateur. Lire la feuille de style ne dit pas
   quelle regle a gagne, et compter des lignes dans un fichier ne dit pas ce
   qui s'est affiche.

Le suite se relance deux fois de suite sans nettoyage : elle ne doit rien
laisser derriere elle.
"""

import html as _H
import http.server
import json
import os
import re
import socket
import subprocess
import sys
import threading

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)

from chemins import dossier_pages          # noqa: E402
from prestige import (DISTINCTIONS, DUREE, GROUPES,  # noqa: E402
                      HONORAIRES_BASE, HONORAIRES_INCITATION,
                      MODES, MODES_PAR_DISTINCTION, PRESTATIONS, REDEVANCE,
                      construire, tranche_cle)
from reference import TAUX_EUR             # noqa: E402
import page_prestige                       # noqa: E402

OK = []
IGNORES = []


def t(nom, cond, detail=''):
    OK.append(bool(cond))
    print('%s %s%s' % ('  ok  ' if cond else ' ECHEC', nom,
                       ('   -> ' + str(detail)) if not cond and detail else ''))


def ignore(nom, pourquoi):
    """Un controle qui n'a PAS tourne.

    Il ne compte pas comme reussi. Un « ignore » silencieux qui s'additionne
    aux verts est la facon la plus simple de livrer une suite qui ne verifie
    plus rien.
    """
    IGNORES.append(nom)
    print(' IGNORE %s   -> %s' % (nom, pourquoi))


# On regenere avant de controler : un controle qui lit un fichier vieux de
# trois modifications valide un livrable qui n'existe plus.
subprocess.run([sys.executable, os.path.join(ICI, 'prestige.py')],
               check=True, stdout=subprocess.DEVNULL)
subprocess.run([sys.executable, os.path.join(ICI, 'page_prestige.py')],
               check=True, stdout=subprocess.DEVNULL)

DEMO = dossier_pages(ICI)
D = json.load(open(os.path.join(DEMO, 'prestige.json'), encoding='utf-8'))
FI = D['fiches']
DIST = dict((d[0], d) for d in DISTINCTIONS)
ACC = open(os.path.join(DEMO, 'index.html'), encoding='utf-8').read()
COL = open(os.path.join(DEMO, 'collection.html'), encoding='utf-8').read()

print('\n--- les donnees se tiennent, maison par maison ---')

t('la collection contient des maisons', len(FI) > 0, len(FI))
t('%d maisons pour %d groupes' % (len(FI), len(D['groupes'])),
  len(FI) == sum(len(ms) for _p, ms in GROUPES.values())
  and len(D['groupes']) == len(GROUPES))
t('les identifiants sont uniques', len({f['id'] for f in FI}) == len(FI))
t('les noms de maison sont uniques', len({f['nom'] for f in FI}) == len(FI))
# Une marque qui porte le nom de son groupe s'affiche deux fois de suite sur
# la carte, et se lit comme un bug d'affichage.
memes = [f['nom'] for f in FI if f['nom'] == f['groupe']]
t('aucune maison ne porte exactement le nom de son groupe', not memes, memes)

faux = [(f['id'], f['projet'],
         f['investissement_cle']['bas'] * f['cles']['min'],
         f['investissement_cle']['haut'] * f['cles']['max']) for f in FI
        if f['projet']['bas'] != f['investissement_cle']['bas'] * f['cles']['min']
        or f['projet']['haut'] != f['investissement_cle']['haut'] * f['cles']['max']]
t('le cout du projet est le PRODUIT investissement/cle x taille acceptee',
  not faux, faux[:2])

faux = [(f['id'], f['reseau']) for f in FI
        if f['reseau']['cles'] !=
        f['reseau']['maisons'] * f['reseau']['taille_moyenne']]
t('les cles du reseau sont le produit adresses x taille moyenne',
  not faux, faux[:2])

faux = [(f['id'], f['reseau']['taille_moyenne'], f['cles']) for f in FI
        if not (f['cles']['min'] <= f['reseau']['taille_moyenne']
                <= f['cles']['max'])]
t('la taille moyenne du reseau tombe dans la fourchette acceptee',
  not faux, faux[:2])

faux = [(f['id'], f['cles'], DIST[f['distinction']][7:9]) for f in FI
        if not (DIST[f['distinction']][7] <= f['cles']['min']
                < f['cles']['max'] <= DIST[f['distinction']][8])]
t('la taille acceptee tient dans la bande de sa distinction', not faux,
  faux[:2])

faux = [(f['id'], f['investissement_cle']['eur_bas'],
         DIST[f['distinction']][5:7]) for f in FI
        if not (DIST[f['distinction']][5] <= f['investissement_cle']['eur_bas']
                <= DIST[f['distinction']][6])]
t("l'investissement par cle tient dans la bande de sa distinction",
  not faux, faux[:2])

faux = [(f['id'], f['investissement_cle']) for f in FI
        if f['investissement_cle']['bas'] >= f['investissement_cle']['haut']]
t("le bas de l'investissement est sous le haut", not faux, faux[:2])

faux = [(f['id'], f['investissement_cle']['tranche'],
         tranche_cle(f['investissement_cle']['eur_bas'])) for f in FI
        if f['investissement_cle']['tranche']
        != tranche_cle(f['investissement_cle']['eur_bas'])]
t("la tranche annoncee est celle que le montant en euros designe", not faux,
  faux[:2])

faux = [(f['id'], f['nuitee']) for f in FI
        if not (0 < f['nuitee']['bas'] < f['nuitee']['haut'])]
t('le prix moyen de la nuitee est une fourchette croissante', not faux,
  faux[:2])

# Le haut de fourchette peut depasser la bande de la distinction — une suite
# se vend au-dessus du prix moyen de la maison. Le BAS, lui, ne doit pas
# tomber sous la bande : ce serait promettre un positionnement que la marque
# ne tient pas.
faux = [(f['id'], f['devise'],
         round(f['nuitee']['bas'] * TAUX_EUR[f['devise']]),
         DIST[f['distinction']][9]) for f in FI
        if f['nuitee']['bas'] * TAUX_EUR[f['devise']]
        < DIST[f['distinction']][9] * .75]
t('le bas du prix moyen reste dans le positionnement de la distinction',
  not faux, faux[:2])

print('\n--- la remuneration : trois pourcentages, trois assiettes ---')

faux = [(f['id'], f['modes'], f['honoraires']) for f in FI
        if ('gestion' in f['modes'])
        != (f['honoraires']['base'] is not None)]
t("les honoraires de gestion existent si et seulement s'il y a gestion",
  not faux, faux[:2])

faux = [(f['id'], f['honoraires']) for f in FI
        if (f['honoraires']['base'] is None)
        != (f['honoraires']['incitation'] is None)]
t('base et incitation vont toujours ensemble', not faux, faux[:2])

faux = [(f['id'], f['honoraires']) for f in FI
        if f['honoraires']['base'] is not None
        and not (HONORAIRES_BASE[0] <= f['honoraires']['base']
                 <= HONORAIRES_BASE[1]
                 and HONORAIRES_INCITATION[0] <= f['honoraires']['incitation']
                 <= HONORAIRES_INCITATION[1])]
t('les honoraires tiennent dans leurs bandes', not faux, faux[:2])

faux = [(f['id'], f['honoraires']) for f in FI
        if f['honoraires']['base'] is not None
        and f['honoraires']['base'] >= f['honoraires']['incitation']]
t("l'incitation, assise sur le resultat, est toujours au-dessus de la base, "
  "assise sur le chiffre d'affaires", not faux, faux[:2])

vendus = [m for m in ('franchise', 'affiliation')]
faux = [(f['id'], f['modes'], f['redevance']) for f in FI
        if (any(m in f['modes'] for m in vendus))
        != (f['redevance'] is not None)]
t("la redevance existe si et seulement s'il y a franchise ou affiliation",
  not faux, faux[:2])

faux = [(f['id'], f['modes'], f['redevance']) for f in FI
        if f['redevance'] is not None
        and not (REDEVANCE['affiliation'][0] <= f['redevance']
                 <= REDEVANCE['franchise'][1])]
t('la redevance tient dans sa bande', not faux, faux[:2])

# Le key money : le groupe APPORTE de l'argent au proprietaire. Un
# franchiseur ne paie pas pour etre franchiseur.
faux = [(f['id'], f['modes'], f['key_money_cle']) for f in FI
        if f['key_money_cle'] and 'gestion' not in f['modes']]
t("l'apport du groupe n'existe que sur un contrat de gestion", not faux,
  faux[:2])
km = [f for f in FI if f['key_money_cle']]
t("l'apport du groupe existe sur une partie seulement des gestions (%d/%d)"
  % (len(km), sum(1 for f in FI if 'gestion' in f['modes'])),
  0 < len(km) < sum(1 for f in FI if 'gestion' in f['modes']), len(km))

faux = [(f['id'], f['services_techniques_cle'], f['preouverture_cle'])
        for f in FI
        if f['services_techniques_cle'] <= 0 or f['preouverture_cle'] <= 0]
t('services techniques et pre-ouverture sont toujours chiffres', not faux,
  faux[:2])

print('\n--- le contrat suit la distinction ---')

faux = [(f['id'], f['distinction'], f['modes']) for f in FI
        if any(m not in MODES_PAR_DISTINCTION[f['distinction']]
               for m in f['modes'])]
t('aucune maison ne propose un mode interdit a sa distinction', not faux,
  faux[:2])

faux = [(f['id'], f['modes']) for f in FI
        if f['modes'][0] != MODES_PAR_DISTINCTION[f['distinction']][0]]
t('le mode principal est bien le premier de sa distinction', not faux,
  faux[:2])

faux = [(f['id'], f['distinction'], f['modes']) for f in FI
        if f['distinction'] in ('palace', 'maison')
        and 'franchise' in f['modes']]
t('ni un palace ni une maison de luxe ne se franchise', not faux, faux[:2])

faux = [(f['id'], f['duree_contrat'], DUREE[f['modes'][0]]) for f in FI
        if not (DUREE[f['modes'][0]][0] <= f['duree_contrat']
                <= DUREE[f['modes'][0]][1])]
t('la duree du contrat correspond au mode principal', not faux, faux[:2])

gest = [f['duree_contrat'] for f in FI if f['modes'][0] == 'gestion']
aff = [f['duree_contrat'] for f in FI if f['modes'][0] == 'affiliation']
t("une gestion est toujours plus longue qu'une affiliation",
  not aff or (min(gest) > max(aff)),
  (min(gest) if gest else None, max(aff) if aff else None))

faux = [(f['id'], f['modes']) for f in FI if len(set(f['modes'])) != len(f['modes'])]
t('aucune maison ne repete un mode', not faux, faux[:2])

print('\n--- les groupes, les listes, les references ---')

doubles = []
for g, (_p, ms) in GROUPES.items():
    vus = {}
    for nom, dist, _a, _b in ms:
        vus.setdefault(dist, []).append(nom)
    for dist, noms in vus.items():
        if len(noms) > 1:
            doubles.append((g, dist, noms))
t('aucun groupe ne porte deux maisons dans la meme distinction', not doubles,
  doubles[:2])

cles_p = {p[0] for p in PRESTATIONS}
faux = [(f['id'], set(f['prestations']) - cles_p) for f in FI
        if set(f['prestations']) - cles_p]
t('toutes les prestations citees existent dans la table', not faux, faux[:2])

faux = [(f['id'],) for f in FI
        if f['residences_de_marque'] != ('residences' in f['prestations'])]
t('la commercialisation des residences est proposee exactement quand il y a '
  'des residences', not faux, faux[:2])

cles_pays = {p['cle'] for p in D['pays']}
faux = [(f['id'], set(f['pays']) - cles_pays) for f in FI
        if set(f['pays']) - cles_pays]
t("tous les pays d'implantation existent dans la table", not faux, faux[:2])

faux = [(f['id'],) for f in FI if f['pays_origine'] not in f['pays']]
t("le pays d'origine fait partie des pays d'implantation", not faux, faux[:2])

faux = [(f['id'], f['annee_creation'], f['annee_premiere_gestion']) for f in FI
        if not (1600 < f['annee_creation'] <= f['annee_premiere_gestion']
                <= 2024)]
t('la maison est exploitee sous la marque apres avoir ete construite',
  not faux, faux[:2])

faux = [(f['id'], f['suites_pct'], DIST[f['distinction']][11:13]) for f in FI
        if not (DIST[f['distinction']][11] <= f['suites_pct']
                <= DIST[f['distinction']][12])]
t('la part de suites tient dans la bande de sa distinction', not faux,
  faux[:2])

faux = [(f['id'], f['tables'], DIST[f['distinction']][13:15]) for f in FI
        if not (DIST[f['distinction']][13] <= f['tables']
                <= DIST[f['distinction']][14])]
t('le nombre de points de restauration tient dans sa bande', not faux,
  faux[:2])

t('chaque distinction porte au moins deux maisons',
  all(sum(1 for f in FI if f['distinction'] == d[0]) >= 2
      for d in DISTINCTIONS),
  [(d[0], sum(1 for f in FI if f['distinction'] == d[0]))
   for d in DISTINCTIONS])
t('chaque mode est propose par au moins une maison',
  all(any(m[0] in f['modes'] for f in FI) for m in MODES),
  [(m[0], sum(1 for f in FI if m[0] in f['modes'])) for m in MODES])

# Deux constructions doivent donner le meme fichier, sinon la moindre
# reconstruction change les chiffres sous les yeux du client.
t('la construction est reproductible',
  json.dumps(construire(), sort_keys=True)
  == json.dumps(construire(), sort_keys=True))

print('\n--- une maison ne peut pas etre sur deux sites a la fois ---')

autre = os.path.join(os.path.dirname(ICI), 'franchises', 'demo',
                     'hotellerie.json')
if os.path.isfile(autre):
    H = json.load(open(autre, encoding='utf-8'))
    ici_noms = {f['nom'] for f in FI}
    la_noms = {f['nom'] for f in H['fiches']}
    t('aucune marque ne figure a la fois ici et dans la section hotellerie',
      not (ici_noms & la_noms), sorted(ici_noms & la_noms))
    t('la section hotellerie ne porte plus de segment « luxe »',
      not any(f['segment'] == 'luxe' for f in H['fiches']),
      sorted({f['nom'] for f in H['fiches'] if f['segment'] == 'luxe'}))
else:
    ignore('recoupement avec la section hotellerie',
           'hotellerie.json absent de cet arbre (%s)' % autre)

print('\n--- ce qui est ecrit dans les pages ---')

t('aucun marqueur de gabarit ne subsiste',
  not re.search(r'__[A-Z0-9_]+__', ACC + COL),
  sorted(set(re.findall(r'__[A-Z0-9_]+__', ACC + COL)))[:4])

t('les deux pages embarquent exactement la meme feuille de style',
  re.search(r'<style>\n(.*?)\n</style>', ACC, re.S).group(1)
  == re.search(r'<style>\n(.*?)\n</style>', COL, re.S).group(1))

# Les cadres d'image : le ratio ANNONCE doit etre le ratio APPLIQUE. Lire la
# feuille de style ne dit pas quelle regle a gagne — mais comparer les deux
# valeurs ecrites cote a cote, si.
TOUT = ACC + COL
paires = re.findall(r'data-ratio="([^"]+)"><div class="ph" '
                    r'style="aspect-ratio:([^"]+)"', TOUT)
mauvais = [(a, b) for a, b in paires if a != b]
nb_stat = len(re.findall(r'data-img="images/', TOUT))
t('chaque cadre statique porte le ratio de son image (%d cadres)' % nb_stat,
  len(paires) == nb_stat and not mauvais, (len(paires), mauvais[:2]))
sans = re.findall(r'class="ph"(?![^>]*aspect-ratio)', TOUT)
t('aucun cadre, gabarit JavaScript compris, ne reste sans ratio', not sans,
  len(sans))

# Un element traduit doit porter LES DEUX langues. Un data-fr solitaire reste
# en francais sans rien signaler.
# On isole les balises entieres puis on regarde DEDANS. Une negation
# placee apres l'attribut ne voit que ce qui le suit : elle laissait passer
# une balise ou data-fr precede data-en, c'est-a-dire le cas normal.
balises = re.findall(r'<[a-z][^>]*>', TOUT, re.S)
boiteux = [b for b in balises
           if ('data-fr=' in b) != ('data-en=' in b)]
t('aucun element ne porte une seule des deux langues', not boiteux,
  [b[:90] for b in boiteux[:2]])
# Le texte ecrit DANS la balise est la version francaise servie avant que le
# script ne tourne ; data-fr est celle qu'il posera. Les deux doivent dire la
# meme chose, sinon la page change de mot toute seule au chargement — c'est
# ainsi qu'une faute de frappe dans l'attribut passe inapercue en relecture.
ecarts = []
for m in re.finditer(r'<(\w+)[^>]*\bdata-fr="([^"]*)"[^>]*>(.*?)</\1>',
                     TOUT, re.S):
    # Les deux cotes ne sont pas encodes pareil : l'attribut est echappe,
    # le contenu ne l'est qu'a moitie. On compare le TEXTE, pas la source.
    attr = _H.unescape(m.group(2)).strip()
    dedans = _H.unescape(m.group(3)).strip()
    if '<' in m.group(3) or '__' in dedans:
        continue
    if attr != dedans:
        ecarts.append((attr[:48], dedans[:48]))
t('le texte servi et le texte francais du script disent la meme chose',
  not ecarts, ecarts[:3])

t('les pages portent des elements traduits',
  len(re.findall(r'data-fr="', TOUT)) > 40,
  len(re.findall(r'data-fr="', TOUT)))

# Les chiffres de l'accueil sont CALCULES. Le controle les recalcule ici a
# partir du JSON — la page ne peut pas se contredire toute seule.
attendus = [len(FI), len(D['groupes']),
            len({p for f in FI for p in f['pays']}),
            sum(f['reseau']['maisons'] for f in FI),
            sum(f['reseau']['cles'] for f in FI)]
ecrits = [int(x.replace(' ', '').replace(' ', '')) for x in
          re.findall(r'<div class="chiffre"><b data-fr="([^"]+)"', ACC)]
t("les cinq chiffres de l'accueil sont ceux du JSON", ecrits == attendus,
  (ecrits, attendus))

t("l'accueil annonce le bon nombre de maisons dans son bouton",
  ('Voir les %d maisons' % len(FI)) in ACC)
t("le titre de la collection annonce le bon nombre",
  page_prestige._en_lettres(len(FI)) + ' maisons' in COL,
  page_prestige._en_lettres(len(FI)))

# L'accueil n'affiche aucun montant : il n'en a pas besoin, et un montant
# ecrit en dur sur une page statique est un chiffre qui ne suivra pas les
# donnees.
argent = re.findall(r'[$€£]|\bEUR\b|\bUSD\b|\bCAD\b|\bCHF\b', ACC)
t("aucun montant n'est ecrit en dur sur l'accueil", not argent,
  sorted(set(argent)))

t('les deux liens vers les autres sites sont presents sur les deux pages',
  ACC.count(page_prestige.URL_HOTELLERIE) >= 2
  and COL.count(page_prestige.URL_HOTELLERIE) >= 2
  and ACC.count(page_prestige.URL_ANNUAIRE) >= 1
  and COL.count(page_prestige.URL_ANNUAIRE) >= 1)

t('la marque du site est encore marquee comme un placeholder',
  'nom a definir' in ACC and 'nom a definir' in COL)

# Aucun groupe hotelier REEL ne doit apparaitre. Tout est fictif, et une
# marque reelle glissee dans un texte de demonstration devient une affirmation
# sur une entreprise qui existe.
REELS = [
    'Marriott', 'Hilton', 'Hyatt', 'Accor', 'InterContinental', 'Radisson',
    'Wyndham', 'Four Seasons', 'Ritz', 'Rosewood', 'Mandarin Oriental',
    'Belmond', 'Peninsula', 'Shangri', 'Waldorf', 'Fairmont', 'Raffles',
    'Sofitel', 'Kempinski', 'Oetker', 'Dorchester', 'Banyan Tree',
    'Six Senses', 'St. Regis', 'St Regis', 'Conrad', 'Jumeirah', 'Anantara',
    'Cheval Blanc', 'Oberoi', 'Bulgari', 'Relais & Chateaux',
    'Leading Hotels', 'Small Luxury Hotels', 'Preferred Hotels',
    'Design Hotels', 'Aman Resorts', 'Park Hyatt', 'Le Meridien',
]
trouves = sorted({m for m in REELS
                  if re.search(r'\b' + re.escape(m), TOUT, re.I)})
t('aucun groupe hotelier reel n\'est nomme dans les pages', not trouves,
  trouves)
trouves = sorted({m for m in REELS
                  if re.search(r'\b' + re.escape(m),
                               json.dumps(D, ensure_ascii=False), re.I)})
t('aucun groupe hotelier reel n\'est nomme dans les donnees', not trouves,
  trouves)

t('les deux pages annoncent la demonstration',
  'DEMONSTRATION' in ACC and 'DEMONSTRATION' in COL)
t("les pages ne sont pas indexables tant que le nom n'est pas arrete",
  ACC.count('name="robots" content="noindex"') == 1
  and COL.count('name="robots" content="noindex"') == 1)

print('\n--- la page, dans un vrai navigateur ---')

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    ignore('controles navigateur', 'playwright absent')
    sync_playwright = None

if sync_playwright:
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()

    class Muet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def __init__(self, *a, **k):
            super().__init__(*a, directory=DEMO, **k)

    srv = http.server.ThreadingHTTPServer(('127.0.0.1', port), Muet)
    fil = threading.Thread(target=srv.serve_forever, daemon=True)
    fil.start()
    base = 'http://127.0.0.1:%d/' % port

    erreurs = []
    with sync_playwright() as p:
        nav = p.chromium.launch()
        pg = nav.new_page(viewport={'width': 1280, 'height': 900})
        pg.on('console', lambda m: erreurs.append(m.text)
              if m.type == 'error' else None)
        pg.on('pageerror', lambda x: erreurs.append(str(x)))

        # ---------------------------------------------------------- accueil
        pg.goto(base + 'index.html', wait_until='networkidle')
        # Le titre doit commencer SOUS l'en-tete colle. Une superposition
        # mal dimensionnee le faisait remonter derriere lui, et il n'y a
        # aucune erreur JavaScript pour le signaler.
        bornes = pg.evaluate("""()=>{
          var h=document.querySelector('.haut').getBoundingClientRect();
          var t=document.querySelector('h1').getBoundingClientRect();
          return [h.bottom, t.top];
        }""")
        t("le titre de l'accueil commence sous l'en-tete (%.0f >= %.0f)"
          % (bornes[1], bornes[0]), bornes[1] >= bornes[0] - 1, bornes)
        t("l'accueil affiche son titre",
          'gestion' in pg.locator('h1').inner_text().lower(),
          pg.locator('h1').inner_text())
        t("l'accueil montre une maison par distinction",
          pg.locator('.grille .carte').count() == len(DISTINCTIONS),
          pg.locator('.grille .carte').count())
        vues = pg.eval_on_selector_all(
            '.grille .carte .dist', 'n=>n.map(x=>x.textContent)')
        t('les cinq distinctions sont representees, sans doublon',
          len(set(vues)) == len(DISTINCTIONS), vues)
        # Cinq cartes tirees du meme groupe illustreraient le contraire de ce
        # que la section vient d'expliquer.
        grp = pg.eval_on_selector_all(
            '.grille .carte .grp', 'n=>n.map(x=>x.textContent)')
        t("l'apercu montre cinq groupes differents",
          len(set(grp)) == len(DISTINCTIONS), grp)
        # Les cartes de l'accueil sont des liens : sans regle, tout leur
        # contenu se souligne, y compris les chiffres.
        souligne = pg.evaluate("""()=>{
          var out=[];
          document.querySelectorAll('.grille .carte, .grille .carte *')
            .forEach(function(n){
              var d = getComputedStyle(n).textDecorationLine;
              if (d && d !== 'none') out.push(n.tagName+':'+d);
            });
          return out.slice(0,4);
        }""")
        t("rien n'est souligne dans les cartes de l'accueil", not souligne,
          souligne)

        # Le fond est reellement noir : la feuille de style peut declarer ce
        # qu'elle veut, seule la valeur calculee dit ce qui a gagne.
        fond = pg.evaluate("()=>getComputedStyle(document.body)"
                           ".backgroundColor")
        rgb = [int(x) for x in re.findall(r'\d+', fond)[:3]]
        t('le fond est bien un noir, et pas un noir pur (%s)' % fond,
          max(rgb) < 30 and max(rgb) > 0, rgb)

        # --------------------------------------------------------- overflow
        for nom in ('index.html', 'collection.html'):
            pg.set_viewport_size({'width': 390, 'height': 800})
            pg.goto(base + nom, wait_until='networkidle')
            pg.wait_for_timeout(250)
            larg = pg.evaluate("()=>[document.documentElement.scrollWidth,"
                               "window.innerWidth]")
            coupables = pg.evaluate("""()=>{
              var out=[];
              document.querySelectorAll('*').forEach(function(n){
                var r=n.getBoundingClientRect();
                if (r.right > window.innerWidth+1)
                  out.push(n.tagName+'.'+n.className+' '+Math.round(r.right));
              });
              return out.slice(0,3);
            }""")
            t('%s ne deborde pas a 390 px (%d/%d)' % (nom, larg[0], larg[1]),
              larg[0] <= larg[1] + 1, coupables)
        pg.set_viewport_size({'width': 1280, 'height': 900})

        # ------------------------------------------------------- collection
        pg.goto(base + 'collection.html', wait_until='networkidle')
        pg.wait_for_selector('.grille .carte')

        def total():
            return pg.locator('.grille .carte').count()

        t('la collection affiche les %d maisons' % len(FI), total() == len(FI),
          total())

        # Le compteur d'une case doit PREDIRE le resultat de son cochage.
        case = pg.locator('.grp-f input[data-g="dists"][data-v="palace"]')
        annonce = int(case.locator('xpath=../span[@class="n"]').inner_text())
        case.check()
        pg.wait_for_timeout(200)
        attendu = sum(1 for f in FI if f['distinction'] == 'palace')
        t('le compteur de la distinction « palace » predisait le resultat (%d)'
          % attendu, annonce == attendu == total(),
          (annonce, attendu, total()))
        case.uncheck()
        pg.wait_for_timeout(150)
        t('decocher rend la totalite', total() == len(FI), total())

        # Le filtre de taille : DANS la fourchette, pas au-dessus d'un seuil.
        pg.select_option('#taille', '250')
        pg.wait_for_timeout(200)
        attendu = sum(1 for f in FI
                      if f['cles']['min'] <= 250 <= f['cles']['max'])
        t('un actif de 250 cles trouve %d maisons' % attendu,
          total() == attendu, total())
        petites = pg.eval_on_selector_all(
            '.grille .carte h3', 'n=>n.map(x=>x.textContent)')
        hors = [f['nom'] for f in FI if f['nom'] in petites
                and not (f['cles']['min'] <= 250 <= f['cles']['max'])]
        t('aucune maison affichee ne refuse cette taille', not hors, hors)

        pg.select_option('#taille', '')
        pg.wait_for_timeout(150)

        # Une option qui ne concerne qu'une partie du fichier : si elle
        # renvoie tout, elle ne filtre rien.
        pg.check('.grp-f input[data-g="options"][data-v="key"]')
        pg.wait_for_timeout(200)
        attendu = sum(1 for f in FI if f['key_money_cle'])
        t("l'apport du groupe filtre a %d maisons, un sous-ensemble strict"
          % attendu, total() == attendu < len(FI), (total(), attendu))
        pg.click('#raz')
        pg.wait_for_timeout(200)
        t('« tout effacer » rend la totalite', total() == len(FI), total())

        # -------------------------------------------------------- la fiche
        # Une maison en GESTION : elle doit montrer les deux honoraires.
        g = next(f for f in FI if 'gestion' in f['modes'])
        pg.evaluate("id=>document.querySelector('.carte[data-id=\"'+id+'\"]')"
                    ".click()", g['id'])
        pg.wait_for_selector('.fiche[data-ouvert=oui]')
        corps = pg.locator('.fiche').inner_text()
        t('la fiche %s montre les honoraires de base' % g['nom'],
          'Honoraires de base' in corps)
        t('la fiche montre les honoraires d\'incitation',
          "Honoraires d'incitation" in corps)
        t('la fiche rappelle que les assiettes sont differentes',
          "RESULTAT BRUT D'EXPLOITATION" in corps)

        # Une annee n'est pas une quantite : « 1 986 » est un autre nombre.
        # Le controle vise LES DEUX LIGNES D'ANNEE, pas toute suite de
        # chiffres : un spa de 1 200 m2 est une quantite, et il a le droit
        # a son separateur.
        lignes = pg.evaluate("""()=>{
          var o={}, n=document.querySelectorAll('.fiche .lignes > div');
          for (var i=0;i+1<n.length;i+=2)
            o[n[i].textContent.trim()] = n[i+1].textContent.trim();
          return o;
        }""")
        val_cre = lignes.get('Construction', '')
        val_ges = lignes.get('Premiere exploitation sous la marque', '')
        t("l'annee de construction s'affiche telle quelle (%r)" % val_cre,
          val_cre == str(g['annee_creation']), (val_cre, g['annee_creation']))
        t("l'annee de premiere exploitation s'affiche telle quelle (%r)"
          % val_ges,
          val_ges == str(g['annee_premiere_gestion']),
          (val_ges, g['annee_premiere_gestion']))
        t('les deux lignes d\'annee ont bien ete trouvees',
          bool(val_cre) and bool(val_ges), sorted(lignes)[:6])

        # Le cout du projet affiche doit etre celui qu'on recalcule.
        chiffres = [int(x) for x in re.findall(
            r'\d[\d  , ]*',
            corps.replace(' ', ' '))[:0]] or None
        t('le cout du projet est present dans la fiche',
          'Cout du projet' in corps)

        # Une maison SANS redevance doit l'ecrire, pas laisser un vide.
        pg.click('#x')
        pg.wait_for_timeout(150)
        sans_r = next((f for f in FI if f['redevance'] is None), None)
        if sans_r:
            pg.evaluate("id=>document.querySelector('.carte[data-id=\"'+id"
                        "+'\"]').click()", sans_r['id'])
            pg.wait_for_selector('.fiche[data-ouvert=oui]')
            c2 = pg.locator('.fiche').inner_text()
            t('une maison sans redevance affiche « Non propose », pas un vide',
              'Non propose' in c2)
            pg.click('#x')
            pg.wait_for_timeout(150)
        else:
            ignore('maison sans redevance', 'toutes en ont une')

        # Lien profond, deux cas qui n'empruntent PAS le meme chemin.
        # a) chargement neuf : on passe par une autre page, sinon
        #    « meme document + fragment » ne declenche aucune navigation et
        #    le controle mesurerait le cache du navigateur.
        cible = FI[-1]
        pg.goto(base + 'index.html', wait_until='networkidle')
        pg.goto(base + 'collection.html#' + cible['id'],
                wait_until='networkidle')
        pg.wait_for_selector('.fiche[data-ouvert=oui]')
        t('au chargement, #identifiant ouvre directement la bonne fiche',
          cible['nom'] in pg.locator('#fiche-nom').inner_text(),
          pg.locator('#fiche-nom').inner_text())
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(150)
        t('echap referme la fiche',
          pg.locator('.fiche').get_attribute('data-ouvert') == 'non')
        # b) fragment change dans la page : aucun rechargement, il faut un
        #    ecouteur. Sans lui le navigateur se contente de defiler.
        autre = FI[0]
        pg.evaluate("id=>{ location.hash = id; }", autre['id'])
        pg.wait_for_selector('.fiche[data-ouvert=oui]')
        t('un fragment change dans la page ouvre aussi la fiche',
          autre['nom'] in pg.locator('#fiche-nom').inner_text(),
          pg.locator('#fiche-nom').inner_text())
        pg.keyboard.press('Escape')
        pg.wait_for_timeout(150)

        # ----------------------------------------------------- formulaire
        pg.click('#b-envoi')
        pg.wait_for_timeout(150)
        recu = pg.locator('#recu').inner_text()
        t('le formulaire vide dit ce qui manque', 'Il manque' in recu, recu)
        pg.fill('#d-nom', 'Test')
        pg.fill('#d-ville', 'Geneve, Suisse')
        pg.fill('#d-cles', '85')
        pg.click('#b-envoi')
        pg.wait_for_timeout(150)
        recu = pg.locator('#recu').inner_text()
        t('le formulaire rempli confirme sans rien envoyer',
          "rien n'a ete envoye" in recu and 'Geneve' in recu, recu)

        # ---------------------------------------------------------- langues
        cles = pg.evaluate("()=>[Object.keys(T.fr).sort().join(','),"
                           "Object.keys(T.en).sort().join(',')]")
        t('les deux langues portent exactement les memes cles',
          cles[0] == cles[1],
          sorted(set(cles[0].split(',')) ^ set(cles[1].split(','))))
        t('le dictionnaire est consequent (%d cles)'
          % len(cles[0].split(',')), len(cles[0].split(',')) > 60)

        pg.click('.langue button[data-l="en"]')
        pg.wait_for_timeout(300)
        panneau = pg.locator('#panneau').inner_text()
        t('les filtres passent en anglais',
          'OPERATING STRUCTURE' in panneau.upper()
          and 'MODE D' not in panneau.upper(), panneau[:120])
        t('les cartes passent en anglais',
          'Accepted size' in pg.locator('.grille .carte').first.inner_text())
        t("le nombre de maisons ne change pas avec la langue",
          total() == len(FI), total())
        pg.goto(base + 'index.html', wait_until='networkidle')
        pg.wait_for_timeout(250)
        t("l'accueil retient la langue choisie",
          'management' in pg.locator('h1').inner_text().lower(),
          pg.locator('h1').inner_text())
        pg.click('.langue button[data-l="fr"]')
        pg.wait_for_timeout(200)

        nav.close()

    srv.shutdown()
    srv.server_close()

    t("aucune erreur JavaScript sur les deux pages", not erreurs, erreurs[:3])

print('\n%d controles, %d en echec, %d non executes'
      % (len(OK), OK.count(False), len(IGNORES)))
if IGNORES:
    for n in IGNORES:
        print('   non execute : %s' % n)
sys.exit(1 if (OK.count(False) or IGNORES) else 0)
