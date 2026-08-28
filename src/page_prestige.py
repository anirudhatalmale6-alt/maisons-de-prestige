# -*- coding: utf-8 -*-
"""Construit les deux pages du site noir : l'accueil et la collection.

Deux pages, pas une. L'accueil ne filtre rien et ne charge aucune donnee :
il se lit. La collection travaille. Melangees, on obtient soit un accueil
qui met trois secondes a s'afficher, soit un moteur de recherche precede
d'un long texte que personne ne relit apres la premiere visite.

Les CHIFFRES de l'accueil sont calcules ICI, a la construction, a partir du
meme prestige.json que la collection. Ecrits a la main dans le HTML, ils
auraient survecu a l'ajout d'une maison et le site se serait mis a annoncer
un total faux.
"""

import html as _H
import json
import os
import re

from style_prestige import CSS
from chemins import dossier_pages

ICI = os.path.dirname(os.path.abspath(__file__))
DEMO = dossier_pages(ICI)

# ---------------------------------------------------------------------------
# LES DEUX SEULES ADRESSES A CHANGER LE JOUR DES NOMS DE DOMAINE. Le site de
# prestige est un site separe : il ne peut pas atteindre l'annuaire par un
# chemin relatif. Ces liens sont donc absolus, et ils sont ici, en haut, tous
# les deux — pas disperses dans le corps des pages.
# ---------------------------------------------------------------------------
URL_ANNUAIRE = 'https://anirudhatalmale6-alt.github.io/annuaire-franchises-demo/'
URL_HOTELLERIE = URL_ANNUAIRE + 'hotellerie.html'

MARQUE_FR = 'Maisons de Prestige'
MARQUE_EN = 'Maisons de Prestige'

# LA DEVISE DU FONDATEUR. Elle est ecrite ici et, mot pour mot, dans
# agence/contenu.py ; un controle compare les deux fichiers. Une devise qui
# differe d'un site a l'autre n'est plus une devise, c'est deux slogans.
#
# Changee le 28 aout a sa demande (« change la devise / mes sites impacte le
# monde »). Je la pose telle qu'il l'a formulee : une devise se choisit, elle
# ne se redige pas a la place de quelqu'un.
DEVISE_FR = 'Mes sites impactent le monde.'
DEVISE_EN = 'My sites impact the world.'


def e(x):
    return _H.escape(str(x), quote=True)


# Le diamant. DESSINE, pas copie : la pierre de l'image envoyee par le client
# est une photographie, elle serait floue a 14 px dans un logo et pixellisee
# sur un ecran a haute densite. Un trace vectoriel reste net a toutes les
# tailles, prend 300 octets, et se recolore avec le reste de la page.
#
#   contour  : table (6,3)-(18,3), rondiste a y=9, culasse en (12,21)
#   facettes : couronne (6,3)->(9,9), (12,3)->(9,9) et leurs symetriques,
#              puis pavillon (9,9)->(12,21) et (15,9)->(12,21)
DIAMANT = (
    '<svg class="diamant" viewBox="0 0 24 24" aria-hidden="true" '
    'focusable="false">'
    '<path d="M6 3h12l4 6-10 12L2 9z"/>'
    '<path d="M2 9h20M6 3l3 6M18 3l-3 6M12 3l-3 6M12 3l3 6'
    'M9 9l3 12M15 9l-3 12"/>'
    '</svg>')


def photo(src, alt_fr, alt_en):
    """Une VRAIE image, par opposition a un emplacement en attente.

    La largeur et la hauteur sont lues dans le fichier au moment de la
    construction, pas ecrites a la main : le navigateur reserve alors la
    bonne place avant meme d'avoir telecharge l'image, et la page ne saute
    pas. Ecrites a la main, elles deviennent fausses au premier remplacement
    du fichier et personne ne s'en apercoit.
    """
    chemin = os.path.join(DEMO, src)
    with open(chemin, 'rb') as f:
        tete = f.read(24)
    larg, haut = _dimensions_jpeg(chemin) if tete[:2] == b'\xff\xd8' \
        else (None, None)
    if not larg:
        raise SystemExit('dimensions illisibles : %s' % chemin)
    return ('<figure class="cadre photo" data-photo="%s" data-ratio="%d/%d">'
            '<img src="%s" alt="%s" data-alt-fr="%s" data-alt-en="%s" '
            'width="%d" height="%d" '
            'style="aspect-ratio:%d/%d">'
            '</figure>'
            % (e(src), larg, haut, e(src), e(alt_fr), e(alt_fr), e(alt_en),
               larg, haut, larg, haut))


def _dimensions_jpeg(chemin):
    """Largeur et hauteur d'un JPEG, lues dans ses marqueurs SOF."""
    with open(chemin, 'rb') as f:
        f.read(2)
        while True:
            octet = f.read(1)
            if not octet:
                return None, None
            if octet != b'\xff':
                continue
            while octet == b'\xff':
                octet = f.read(1)
            marqueur = octet[0]
            taille = int.from_bytes(f.read(2), 'big')
            if 0xC0 <= marqueur <= 0xCF and marqueur not in (0xC4, 0xC8, 0xCC):
                f.read(1)
                h = int.from_bytes(f.read(2), 'big')
                w = int.from_bytes(f.read(2), 'big')
                return w, h
            f.read(taille - 2)


def cadre(src, ratio, legende_fr, legende_en):
    """Un emplacement d'image.

    Le cadre porte DEJA le ratio de l'image attendue, en ligne. Sans cela il
    prendrait la valeur par defaut de la feuille de style quel que soit le
    ratio annonce : un bandeau 21/9 s'afficherait en carre, et la page
    sauterait le jour ou le vrai fichier arriverait.
    """
    return (
        '<figure class="cadre" data-img="%s" data-ratio="%s">'
        '<div class="ph" style="aspect-ratio:%s">'
        '<b data-fr="%s" data-en="%s">%s</b>'
        '<span>%s</span></div></figure>'
        % (e(src), e(ratio), e(ratio), e(legende_fr), e(legende_en),
           e(legende_fr), e(src)))


def bi(fr, en, balise='p', classe=''):
    c = ' class="%s"' % e(classe) if classe else ''
    return ('<%s%s data-fr="%s" data-en="%s">%s</%s>'
            % (balise, c, e(fr), e(en), fr, balise))


def entete(page):
    def lien(href, cle, fr, en):
        a = ' aria-current="page"' if cle == page else ''
        return ('<a href="%s"%s data-fr="%s" data-en="%s">%s</a>'
                % (href, a, e(fr), e(en), fr))
    return """<header class="haut"><div class="haut-in">
  <a class="marque" href="index.html">__DIAMANT__<span class="mot">Maisons de <b>Prestige</b></span><span
     class="ph-marque" data-fr="nom a definir" data-en="name to be set"
     >nom a definir</span></a>
  <nav class="nav">
    __L1__
    __L2__
    __L3__
    __L4__
  </nav>
  <div class="langue">
    <button type="button" data-l="fr" aria-pressed="true">FR</button>
    <button type="button" data-l="en" aria-pressed="false">EN</button>
  </div>
</div></header>""" \
        .replace('__DIAMANT__', DIAMANT) \
        .replace('__L1__', lien('index.html', 'accueil', 'Accueil', 'Home')) \
        .replace('__L2__', lien('collection.html', 'collection',
                                'La collection', 'The collection')) \
        .replace('__L3__', lien('collection.html#proposer', '',
                                'Proposer un actif', 'Submit an asset')) \
        .replace('__L4__', lien(URL_HOTELLERIE, '',
                                'Hotellerie de chaine', 'Chain hotels'))


PIED = """<footer><div class="enveloppe">
  <div class="avert" data-fr="__A_FR__" data-en="__A_EN__">__A_FR__</div>
  <div data-fr="__C_FR__" data-en="__C_EN__">__C_FR__</div>
  <div class="liens-sites">
    <a href="__U_HOT__" data-fr="Hotellerie de chaine"
       data-en="Chain hotels">Hotellerie de chaine</a>
    <a href="__U_ANN__" data-fr="Annuaire des franchises"
       data-en="Franchise directory">Annuaire des franchises</a>
  </div>
</div></footer>"""

AVERT_FR = ('DEMONSTRATION. Les groupes, les maisons et tous les chiffres de '
            'ce site sont fictifs. Ils servent a montrer la structure et le '
            'fonctionnement, pas a decrire une offre reelle. Aucun groupe '
            'hotelier existant n\'est nomme ni represente ici.')
AVERT_EN = ('DEMONSTRATION. The groups, houses and every figure on this site '
            'are fictional. They exist to show the structure and the '
            'mechanics, not to describe a real offer. No existing hotel '
            'group is named or represented here.')
COPIE_FR = ('Site separe de l\'annuaire de franchises et de la section '
            'hotellerie de chaine : autre promesse, autres unites de mesure, '
            'autre charte.')
COPIE_EN = ('A site separate from the franchise directory and the chain-hotel '
            'section: a different promise, different units, a different look.')


def pied():
    return (PIED.replace('__A_FR__', e(AVERT_FR)).replace('__A_EN__', e(AVERT_EN))
                .replace('__C_FR__', e(COPIE_FR)).replace('__C_EN__', e(COPIE_EN))
                .replace('__U_HOT__', URL_HOTELLERIE)
                .replace('__U_ANN__', URL_ANNUAIRE))


# La bascule de langue de l'accueil : elle ne connait rien au contenu, elle
# echange le texte de tout element qui porte les deux versions. Un element
# qui n'aurait qu'un data-fr resterait en francais sans rien signaler — un
# controle du fichier verifie que les deux attributs vont toujours ensemble.
JS_LANGUE = """
(function(){
  var L = 'fr';
  function pose(l){
    L = l;
    document.documentElement.lang = l;
    var n = document.querySelectorAll('[data-fr][data-en]');
    for (var i=0;i<n.length;i++) n[i].innerHTML = n[i].getAttribute('data-'+l);
    /* Le texte alternatif d'une image est du contenu, pas de la decoration :
       il se traduit comme le reste. Laisse en francais, il devient le seul
       morceau de la page qui ne suit pas le bouton de langue — et c'est
       precisement le morceau que lit un lecteur d'ecran. */
    var im = document.querySelectorAll('img[data-alt-en][data-alt-fr]');
    for (var k=0;k<im.length;k++)
      im[k].setAttribute('alt', im[k].getAttribute('data-alt-'+l));
    var b = document.querySelectorAll('.langue button');
    for (var j=0;j<b.length;j++)
      b[j].setAttribute('aria-pressed',
                        b[j].getAttribute('data-l') === l ? 'true' : 'false');
    try { localStorage.setItem('mdp-langue', l); } catch(e){}
    if (window.surLangue) window.surLangue(l);
  }
  window.langue = function(){ return L; };
  window.poseLangue = pose;
  document.addEventListener('click', function(ev){
    var b = ev.target.closest && ev.target.closest('.langue button');
    if (b) pose(b.getAttribute('data-l'));
  });
  var m = null;
  try { m = localStorage.getItem('mdp-langue'); } catch(e){}
  pose(m === 'en' ? 'en' : 'fr');
})();
"""


SQUELETTE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITRE__</title>
<meta name="description" content="__DESC__">
<meta name="robots" content="noindex">
<style>
__CSS__
</style>
</head>
<body>
__CORPS__
<script>
__JS__
</script>
</body>
</html>
"""


def squelette(titre, desc, corps, js):
    return (SQUELETTE.replace('__TITRE__', e(titre))
                     .replace('__DESC__', e(desc))
                     .replace('__CSS__', CSS.strip())
                     .replace('__CORPS__', corps)
                     .replace('__JS__', js.strip()))


def charger():
    chemin = os.path.join(DEMO, 'prestige.json')
    with open(chemin, encoding='utf-8') as f:
        return json.load(f)


def nb_fr(n):
    """Un nombre ecrit dans le texte francais de l'accueil.

    Espace INSECABLE entre les groupes : « 12 400 » coupe en fin de ligne se
    lit comme deux nombres.
    """
    s = '%d' % n
    out = ''
    while len(s) > 3:
        out = ' ' + s[-3:] + out
        s = s[:-3]
    return s + out


def nb_en(n):
    return '{:,}'.format(n)


# ===========================================================================
#                                  L'ACCUEIL
# ===========================================================================
def page_accueil(D):
    fi = D['fiches']
    dists = D['distinctions']
    modes = D['modes']

    # Les chiffres. Calcules, jamais ecrits a la main.
    n_maisons = len(fi)
    n_groupes = len(D['groupes'])
    n_pays = len(set(p for f in fi for p in f['pays']))
    n_adresses = sum(f['reseau']['maisons'] for f in fi)
    n_cles = sum(f['reseau']['cles'] for f in fi)

    o = []
    o.append(entete('accueil'))

    # ------------------------------------------------------------------ hero
    o.append('<div class="hero"><div class="enveloppe">'
             '<div class="hero-in"><div class="hero-txt">')
    o.append(bi('Cinq etoiles et au-dessus', 'Five stars and above',
                'p', 'surtitre'))
    o.append(bi('Les enseignes qui prennent en gestion '
                'une adresse d\'exception.',
                'The brands that take an exceptional address '
                'under management.', 'h1'))
    o.append(bi('Un palace ne se franchise pas comme un hotel d\'autoroute. '
                'Cette collection reunit les maisons de prestige et dit, pour '
                'chacune, la seule chose qui interesse un proprietaire : a '
                'quelles conditions elle prend votre actif.',
                'A palace is not franchised like a highway hotel. This '
                'collection brings together the prestige brands and states, '
                'for each of them, the only thing an owner needs: on what '
                'terms it will take your asset.', 'p', 'chapo'))
    o.append('</div><div class="hero-img">')
    o.append(cadre('images/accueil-bandeau.jpg', '4/5',
                   'Photo d\'accueil a deposer',
                   'Homepage photo to be supplied'))
    o.append('</div></div></div></div>')

    # ------------------------------------------------------------- manifeste
    o.append('<section><div class="enveloppe">')
    o.append(bi('Pourquoi un site a part', 'Why a separate site', 'p',
                'eyebrow'))
    o.append('<div class="manifeste"><div>')
    o.append(bi('Au sommet de la gamme, le metier cesse de se mesurer dans '
                'les memes unites que le reste de l\'hotellerie.',
                'At the top of the market, the trade stops being measured in '
                'the same units as the rest of the hotel business.'))
    o.append(bi('Ailleurs, on achete une franchise et on paie une redevance. '
                'Ici, le proprietaire garde ses murs et confie l\'exploitation '
                'au groupe. La remuneration devient un couple : des '
                '<strong>honoraires de base</strong> assis sur le chiffre '
                'd\'affaires total, et des <strong>honoraires '
                'd\'incitation</strong> assis sur le resultat. Le premier '
                'tombe meme quand la maison perd de l\'argent. Le second non. '
                'Toute la negociation est la.',
                'Elsewhere you buy a franchise and pay a royalty. Here the '
                'owner keeps the building and hands operations to the group. '
                'The fee becomes a pair: a <strong>base fee</strong> on total '
                'revenue, and an <strong>incentive fee</strong> on profit. '
                'The first is paid even when the house loses money. The '
                'second is not. That is the whole negotiation.'))
    o.append('</div><div>')
    o.append(bi('Et le sens de l\'argent peut s\'inverser : pour emporter un '
                'contrat, un groupe <strong>apporte</strong> parfois du '
                'capital au proprietaire. Un franchiseur ne fait jamais cela.',
                'And the money can flow the other way: to win a contract, a '
                'group sometimes <strong>contributes</strong> capital to the '
                'owner. A franchisor never does that.'))
    o.append(bi('Mises dans la meme liste que les enseignes de chaine, ces '
                'maisons laissaient les trois quarts des colonnes vides, et '
                'le filtre par redevance comparait un pourcentage de chiffre '
                'd\'affaires a un pourcentage de resultat. Ce ne sont pas les '
                'memes nombres. D\'ou ce site.',
                'Placed in the same list as chain brands, these houses left '
                'three quarters of the columns empty, and the royalty filter '
                'compared a percentage of revenue with a percentage of '
                'profit. Those are not the same numbers. Hence this site.'))
    o.append('</div></div></div></section>')

    # -------------------------------------------------------------- chiffres
    o.append('<section><div class="enveloppe"><div class="chiffres">')
    for val, fr, en in (
            (n_maisons, 'Maisons de prestige', 'Prestige brands'),
            (n_groupes, 'Groupes', 'Groups'),
            (n_pays, 'Pays d\'implantation', 'Countries present'),
            (n_adresses, 'Adresses exploitees', 'Operating addresses'),
            (n_cles, 'Cles au total', 'Keys in total')):
        o.append('<div class="chiffre"><b data-fr="%s" data-en="%s">%s</b>'
                 '<span data-fr="%s" data-en="%s">%s</span></div>'
                 % (e(nb_fr(val)), e(nb_en(val)), nb_fr(val),
                    e(fr), e(en), fr))
    o.append('</div></div></section>')

    # ------------------------------------------------------------ paliers
    o.append('<section><div class="enveloppe">')
    o.append(bi('Cinq facons d\'etre une grande maison',
                'Five ways to be a great house', 'p', 'eyebrow'))
    o.append(bi('Deux adresses cinq etoiles de tailles opposees ne se '
                'gerent pas de la meme facon.',
                'Two five-star addresses of opposite sizes are not run the '
                'same way.', 'h2', 'titre-sec'))
    o.append(bi('Un palace urbain de deux cents cles vit de ses banquets et '
                'de sa restauration. Une maison de quarante cles vit de son '
                'prix moyen. Le filtre de la collection part de la.',
                'A two-hundred-key city palace lives on banqueting and '
                'dining. A forty-key house lives on its average rate. The '
                'collection\'s filter starts there.', 'p', 'intro-sec'))
    o.append('<div class="paliers">')
    for i, d in enumerate(dists, 1):
        n = sum(1 for f in fi if f['distinction'] == d['cle'])
        o.append('<div class="palier">')
        o.append('<div class="n">%02d</div>' % i)
        o.append('<h3 data-fr="%s" data-en="%s">%s</h3>'
                 % (e(d['fr']), e(d['en']), e(d['fr'])))
        o.append('<p data-fr="%s" data-en="%s">%s</p>'
                 % (e(d['desc_fr']), e(d['desc_en']), e(d['desc_fr'])))
        o.append('<p style="margin-top:12px;color:var(--or);font-size:13px" '
                 'data-fr="%s" data-en="%s">%s</p>'
                 % (e('%d maisons' % n), e('%d brands' % n),
                    e('%d maisons' % n)))
        o.append('</div>')
    o.append('</div></div></section>')

    # ---------------------------------------------------------------- modes
    o.append('<section><div class="enveloppe">')
    o.append(bi('Les quatre facons de signer', 'Four ways to sign', 'p',
                'eyebrow'))
    o.append(bi('Ce que vous signez decide de ce que vous payez, et sur quelle '
                'assiette.',
                'What you sign decides what you pay, and on what base.',
                'h2', 'titre-sec'))
    o.append('<div class="modes">')
    for m in modes:
        n = sum(1 for f in fi if m['cle'] in f['modes'])
        o.append('<div class="mode">')
        o.append('<h3 data-fr="%s" data-en="%s">%s</h3>'
                 % (e(m['fr']), e(m['en']), e(m['fr'])))
        o.append('<p class="base" data-fr="%s" data-en="%s">%s</p>'
                 % (e(m['base_fr']), e(m['base_en']), e(m['base_fr'])))
        o.append('<p data-fr="%s" data-en="%s">%s</p>'
                 % (e(m['desc_fr']), e(m['desc_en']), e(m['desc_fr'])))
        o.append('<p style="margin-top:16px;color:var(--faible);font-size:13px"'
                 ' data-fr="%s" data-en="%s">%s</p>'
                 % (e('%d maisons proposent ce mode' % n),
                    e('%d brands offer this' % n),
                    e('%d maisons proposent ce mode' % n)))
        o.append('</div>')
    o.append('</div></div></section>')

    # ------------------------------------------------------------ un extrait
    #
    # Une par distinction : un extrait qui prendrait les cinq premieres de la
    # liste montrerait cinq palaces, et la page dirait le contraire de ce
    # qu'elle vient d'expliquer.
    o.append('<section><div class="enveloppe">')
    o.append(bi('Un apercu', 'A glimpse', 'p', 'eyebrow'))
    o.append(bi('Une maison par distinction.', 'One house per distinction.',
                'h2', 'titre-sec'))
    o.append('<div class="grille">')
    # Un « next() » sur une liste triee par (distinction, nom) renvoyait cinq
    # fois le groupe dont le nom vient en premier : la page promettait cinq
    # facons d'etre une grande maison et montrait un seul groupe.
    deja = set()
    choix = []
    for d in dists:
        cand = [x for x in fi if x['distinction'] == d['cle']]
        pris = next((x for x in cand if x['groupe'] not in deja), cand[0])
        deja.add(pris['groupe'])
        choix.append((d, pris))
    for d, f in choix:
        o.append('<a class="carte" href="collection.html#%s">' % e(f['id']))
        o.append(cadre('images/%s.jpg' % f['id'], '4/3',
                       'Photo a deposer', 'Photo to be supplied'))
        o.append('<div class="carte-corps">')
        o.append('<div class="dist" data-fr="%s" data-en="%s">%s</div>'
                 % (e(d['fr']), e(d['en']), e(d['fr'])))
        o.append('<h3>%s</h3>' % e(f['nom']))
        o.append('<p class="grp">%s</p>' % e(f['groupe']))
        o.append('<p class="res" data-fr="%s" data-en="%s">%s</p>'
                 % (e(f['resume']['fr']), e(f['resume']['en']),
                    e(f['resume']['fr'])))
        o.append('<dl><dt data-fr="Taille acceptee" data-en="Accepted size">'
                 'Taille acceptee</dt><dd>%d&ndash;%d</dd>'
                 % (f['cles']['min'], f['cles']['max']))
        o.append('<dt data-fr="Mode principal" data-en="Main structure">'
                 'Mode principal</dt><dd data-fr="%s" data-en="%s">%s</dd>'
                 '</dl>'
                 % (e(_lib(modes, f['modes'][0], 'fr')),
                    e(_lib(modes, f['modes'][0], 'en')),
                    e(_lib(modes, f['modes'][0], 'fr'))))
        o.append('</div></a>')
    o.append('</div>')
    o.append('<p style="margin-top:34px"><a class="bouton" '
             'href="collection.html" data-fr="Voir les %d maisons" '
             'data-en="See all %d brands">Voir les %d maisons</a></p>'
             % (n_maisons, n_maisons, n_maisons))
    o.append('</div></section>')

    # ------------------------------------------------------------ fondateur
    #
    # Ce bloc ne porte AUCUNE biographie inventee. Un nom, un role, et la
    # phrase que le client a lui-meme ecrite. Le reste est un emplacement
    # signale : ecrire trois lignes plausibles sur la trajectoire d'une
    # personne reelle, c'est publier une affirmation sur quelqu'un.
    o.append('<section class="fondateur"><div class="enveloppe">')
    o.append('<div class="fond-in"><div class="fond-photo">')
    o.append(photo('images/fondateur.jpg',
                   'Hakim Adjaoudi, fondateur',
                   'Hakim Adjaoudi, founder'))
    o.append('</div><div class="fond-txt">')
    o.append(bi('Le fondateur', 'The founder', 'p', 'eyebrow'))
    o.append('<h2 class="titre-sec">Hakim Adjaoudi</h2>')
    o.append('<p class="fond-role" data-fr="%s" data-en="%s">%s</p>'
             % (e('Fondateur, JNCORP INC.'), e('Founder, JNCORP INC.'),
                e('Fondateur, JNCORP INC.')))
    o.append('<p class="devise">' + DIAMANT
             + '<span data-fr="%s" data-en="%s">%s</span></p>'
             % (e(DEVISE_FR), e(DEVISE_EN), e(DEVISE_FR)))
    o.append('<p class="cms-tbc" data-fr="%s" data-en="%s">%s</p>'
             % (e('Texte du fondateur a fournir'),
                e('Founder statement to be supplied'),
                e('Texte du fondateur a fournir')))
    o.append('</div></div></div></section>')

    # ---------------------------------------------------------------- ruban
    o.append('<section class="ruban"><div class="enveloppe"><div class="ruban-in">')
    o.append('<div class="ruban-txt">')
    o.append(bi('Vous possedez un actif de prestige',
                'You own a prestige asset', 'h2', 'titre-sec'))
    o.append(bi('Decrivez-le une fois. Le formulaire demande ce que les '
                'groupes demandent : le nombre de cles, l\'annee de '
                'construction, la derniere renovation, et le mode que vous '
                'envisagez. Rien de plus.',
                'Describe it once. The form asks what the groups ask: the '
                'number of keys, the year built, the last refurbishment, and '
                'the structure you have in mind. Nothing more.', 'p',
                'intro-sec'))
    o.append('</div>')
    o.append('<a class="bouton" href="collection.html#proposer" '
             'data-fr="Proposer un actif" data-en="Submit an asset">'
             'Proposer un actif</a>')
    o.append('</div></div></section>')

    o.append(pied())

    return squelette(
        'Maisons de Prestige — les enseignes qui prennent une adresse '
        'd\'exception en gestion',
        'Collection de demonstration : les maisons hotelieres de prestige, '
        'leurs modes d\'exploitation et leurs conditions.',
        '\n'.join(o), JS_LANGUE)


def _lib(liste, cle, lang):
    for x in liste:
        if x['cle'] == cle:
            return x[lang]
    return cle


# ===========================================================================
#                               LA COLLECTION
# ===========================================================================
CORPS_COLLECTION = """
<section style="padding:52px 0 0;border-bottom:0"><div class="enveloppe">
  <p class="eyebrow" data-fr="La collection" data-en="The collection">La collection</p>
  <h1 style="font-size:clamp(30px,4.6vw,46px)" data-fr="__H1_FR__" data-en="__H1_EN__">__H1_FR__</h1>
  <p class="chapo" data-fr="__CH_FR__" data-en="__CH_EN__">__CH_FR__</p>
</div></section>

<div class="enveloppe"><div class="travail">
  <aside class="panneau" id="panneau">
    <div class="pan-h"><h2 id="h-filtres">Filtres</h2>
      <button type="button" id="raz">Tout effacer</button></div>
    <div class="grp-f">
      <h3 id="h-rech">Recherche</h3>
      <input class="champ" id="q" type="search" placeholder="Nom, groupe, pays">
    </div>
    <div class="grp-f">
      <h3 id="h-taille">Taille de mon actif</h3>
      <select class="champ" id="taille"></select>
      <p style="font-size:12.5px;color:var(--faible);margin:10px 0 0"
         id="aide-taille"></p>
    </div>
    <div class="grp-f"><h3 id="h-dist">Distinction</h3>
      <div id="f-dists"></div></div>
    <div class="grp-f"><h3 id="h-mode">Mode d'exploitation</h3>
      <div id="f-modes"></div></div>
    <div class="grp-f"><h3 id="h-tranche">Investissement par cle</h3>
      <div id="f-tranches"></div></div>
    <div class="grp-f"><h3 id="h-region">Region d'origine</h3>
      <div id="f-regions"></div></div>
    <div class="grp-f"><h3 id="h-opt">Particularites</h3>
      <div id="f-options"></div></div>
  </aside>

  <main>
    <div class="barre">
      <div class="compte" id="compte"></div>
      <div id="puces"></div>
      <div class="tri"><label for="tri" id="l-tri"></label>
        <select id="tri"></select></div>
    </div>
    <div class="grille" id="grille"></div>
    <div class="vide" id="vide" hidden></div>
  </main>
</div></div>

<section id="proposer"><div class="enveloppe">
  <p class="eyebrow" data-fr="Proprietaires" data-en="Owners">Proprietaires</p>
  <h2 class="titre-sec" data-fr="__F1_FR__" data-en="__F1_EN__">__F1_FR__</h2>
  <p class="intro-sec" data-fr="__F2_FR__" data-en="__F2_EN__">__F2_FR__</p>
  <form class="form" id="dossier" novalidate>
    <div><label for="d-nom" id="l-nom"></label>
      <input class="champ" id="d-nom" name="nom" required></div>
    <div><label for="d-tel" id="l-tel"></label>
      <input class="champ" id="d-tel" name="tel"></div>
    <div><label for="d-ville" id="l-ville"></label>
      <input class="champ" id="d-ville" name="ville" required></div>
    <div><label for="d-cles" id="l-cles"></label>
      <input class="champ" id="d-cles" name="cles" type="number" min="1"
             max="2000" required></div>
    <div><label for="d-annee" id="l-annee"></label>
      <input class="champ" id="d-annee" name="annee" type="number"
             min="1600" max="2030"></div>
    <div><label for="d-reno" id="l-reno"></label>
      <input class="champ" id="d-reno" name="reno" type="number"
             min="1900" max="2030"></div>
    <div><label for="d-mode" id="l-mode"></label>
      <select class="champ" id="d-mode" name="mode"></select></div>
    <div><label for="d-dist" id="l-dist"></label>
      <select class="champ" id="d-dist" name="dist"></select></div>
    <div class="large"><label for="d-mot" id="l-mot"></label>
      <textarea class="champ" id="d-mot" name="mot"></textarea></div>
    <div class="large"><button class="bouton" type="submit"
      id="b-envoi"></button></div>
    <div class="large recu" id="recu" hidden></div>
  </form>
</div></section>

<div class="voile" id="voile" data-ouvert="non"></div>
<aside class="fiche" id="fiche" data-ouvert="non" role="dialog"
       aria-modal="true" aria-labelledby="fiche-nom"></aside>
"""


JS_COLLECTION = r"""
var D = null, FI = [], L = 'fr';
var F = {q:'', taille:'', dists:[], modes:[], tranches:[], regions:[],
         options:[]};
var TRI = 'nom';

/* --------------------------------------------------------------- i18n --- */
/* Les cles sont prefixees PAR EMPLOI, pas par page : `fi_mode` (la fiche) et
   `fo_mode` (le formulaire) ne peuvent pas se percuter. Deux cles identiques
   dans un objet JavaScript ne provoquent aucune erreur — la seconde gagne en
   silence, et on cherche une faute de traduction pendant une heure. */
var T = {
 fr:{
  h_filtres:'Filtres', raz:'Tout effacer', h_rech:'Recherche',
  h_taille:'Taille de mon actif', h_dist:'Distinction',
  h_mode:"Mode d'exploitation", h_tranche:'Investissement par cle',
  h_region:"Region d'origine", h_opt:'Particularites',
  t_toutes:'Toutes tailles',
  aide_taille:"La maison doit accepter CETTE taille : le nombre saisi doit tomber dans sa fourchette, pas seulement la depasser.",
  o_residences:'Residences de marque', o_spa:'Spa', o_key:'Apport du groupe possible',
  compte_un:'%(n)d maison', compte_n:'%(n)d maisons',
  sur:'sur %(t)d', l_tri:'Trier par',
  tri_nom:'Nom', tri_cle:'Investissement par cle', tri_nuitee:'Prix moyen',
  tri_reseau:'Taille du reseau', tri_cles:'Taille acceptee',
  vide:"Aucune maison ne repond a ces criteres. Elargissez la taille ou le mode d'exploitation.",
  c_taille:'Taille acceptee', c_mode:'Mode principal', c_nuitee:'Prix moyen',
  fi_apercu:"En un coup d'oeil", fi_argent:"L'argent", fi_contrat:'Le contrat',
  fi_maison:'La maison', fi_reseau:'Le reseau', fi_presta:'Ce que le groupe apporte',
  fi_pays:'Presente dans', fi_modes:"Modes d'exploitation proposes",
  d_dist:'Distinction', d_groupe:'Groupe', d_origine:'Origine',
  d_cles:'Taille acceptee', d_invest:'Investissement par cle',
  d_projet:'Cout du projet', d_nuitee:'Prix moyen de la nuitee',
  d_base:'Honoraires de base', d_incit:"Honoraires d'incitation",
  d_redev:'Redevance', d_key:'Apport du groupe (par cle)',
  d_tech:'Services techniques (par cle)', d_preouv:'Pre-ouverture (par cle)',
  d_duree:'Duree du contrat', d_montee:'Montee en puissance',
  d_reno:'Cycle de renovation', d_suites:'Part de suites',
  d_tables:'Points de restauration', d_spa:'Spa', d_res:'Residences de marque',
  d_cre:'Construction', d_ges:'Premiere exploitation sous la marque',
  d_maisons:'Adresses exploitees', d_total:'Cles au total',
  d_moy:'Taille moyenne', d_aucun:'Non propose', d_oui:'Oui', d_non:'Non',
  u_ans:'ans', u_mois:'mois', u_cles:'cles', u_m2:'m2', u_nuit:'la nuit',
  n_base:"Les honoraires de base portent sur le chiffre d'affaires TOTAL, les honoraires d'incitation sur le RESULTAT BRUT D'EXPLOITATION, la redevance sur le chiffre d'affaires HEBERGEMENT seul. Ces pourcentages ne s'additionnent pas.",
  n_key:"L'apport du groupe est une concession de negociation, pas un droit : il se discute contrat par contrat.",
  fermer:'Fermer',
  fo_nom:'Votre nom', fo_tel:'Telephone', fo_ville:"Ville et pays de l'actif",
  fo_cles:'Nombre de cles', fo_annee:'Annee de construction',
  fo_reno:'Derniere renovation', fo_mode:'Mode envisage',
  fo_dist:'Positionnement vise', fo_mot:'Ce qu\'il faut savoir de la maison',
  fo_envoi:'Envoyer le dossier', fo_indif:'Sans preference',
  fo_manque:'Il manque : %(l)s',
  fo_recu:"Demonstration : rien n'a ete envoye. Sur le site reel, ce dossier partirait au service developpement. Recapitulatif : %(r)s",
  fo_obl:'obligatoire'
 },
 en:{
  h_filtres:'Filters', raz:'Clear all', h_rech:'Search',
  h_taille:'My asset size', h_dist:'Distinction',
  h_mode:'Operating structure', h_tranche:'Investment per key',
  h_region:'Region of origin', h_opt:'Particulars',
  t_toutes:'Any size',
  aide_taille:'The brand must accept THIS size: the number must fall inside its range, not merely exceed it.',
  o_residences:'Branded residences', o_spa:'Spa', o_key:'Group contribution possible',
  compte_un:'%(n)d brand', compte_n:'%(n)d brands',
  sur:'of %(t)d', l_tri:'Sort by',
  tri_nom:'Name', tri_cle:'Investment per key', tri_nuitee:'Average rate',
  tri_reseau:'Network size', tri_cles:'Accepted size',
  vide:'No brand matches these criteria. Widen the size or the operating structure.',
  c_taille:'Accepted size', c_mode:'Main structure', c_nuitee:'Average rate',
  fi_apercu:'At a glance', fi_argent:'The money', fi_contrat:'The contract',
  fi_maison:'The house', fi_reseau:'The network', fi_presta:'What the group brings',
  fi_pays:'Present in', fi_modes:'Structures offered',
  d_dist:'Distinction', d_groupe:'Group', d_origine:'Origin',
  d_cles:'Accepted size', d_invest:'Investment per key',
  d_projet:'Project cost', d_nuitee:'Average daily rate',
  d_base:'Base fee', d_incit:'Incentive fee',
  d_redev:'Royalty', d_key:'Group contribution (per key)',
  d_tech:'Technical services (per key)', d_preouv:'Pre-opening (per key)',
  d_duree:'Contract term', d_montee:'Ramp-up',
  d_reno:'Refurbishment cycle', d_suites:'Suites share',
  d_tables:'Dining outlets', d_spa:'Spa', d_res:'Branded residences',
  d_cre:'Built', d_ges:'First operated under the brand',
  d_maisons:'Operating addresses', d_total:'Keys in total',
  d_moy:'Average size', d_aucun:'Not offered', d_oui:'Yes', d_non:'No',
  u_ans:'years', u_mois:'months', u_cles:'keys', u_m2:'sqm', u_nuit:'per night',
  n_base:'The base fee applies to TOTAL revenue, the incentive fee to GROSS OPERATING PROFIT, the royalty to ROOMS revenue only. These percentages do not add up.',
  n_key:'A group contribution is a negotiating concession, not an entitlement: it is discussed contract by contract.',
  fermer:'Close',
  fo_nom:'Your name', fo_tel:'Telephone', fo_ville:'City and country of the asset',
  fo_cles:'Number of keys', fo_annee:'Year built',
  fo_reno:'Last refurbishment', fo_mode:'Structure considered',
  fo_dist:'Intended positioning', fo_mot:'What we should know about the house',
  fo_envoi:'Send the file', fo_indif:'No preference',
  fo_manque:'Missing: %(l)s',
  fo_recu:'Demonstration: nothing was sent. On the live site this file would reach the development team. Summary: %(r)s',
  fo_obl:'required'
 }
};
function t(k){ return T[L][k]; }
function loc(){ return L === 'fr' ? 'fr-CA' : 'en-CA'; }

var FMT = {};
function argent(v, dev){
  var k = L + dev;
  if (!FMT[k]) FMT[k] = new Intl.NumberFormat(loc(),
    {style:'currency', currency:dev, maximumFractionDigits:0});
  return FMT[k].format(v);
}
function nb(v){ return v.toLocaleString(loc()); }
/* Une annee, un identifiant, un port : ce sont des DESIGNATIONS, pas des
   quantites. Passees dans nb(), « 1986 » s'affiche « 1 986 ». */
function an(v){ return String(v); }
function pct(v){
  var s = v.toLocaleString(loc(), {minimumFractionDigits:1,
                                   maximumFractionDigits:1});
  return L === 'fr' ? s + ' %' : s + '%';
}
function ech(s){
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;')
                  .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function lib(liste, cle){
  for (var i=0;i<liste.length;i++) if (liste[i].cle === cle) return liste[i][L];
  return cle;
}
function fmt(s, o){
  return s.replace(/%\((\w+)\)[ds]/g, function(_, k){ return o[k]; });
}
function pliage(s){
  return s.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g,'');
}

/* ------------------------------------------------------------ filtrage --- */
/* `sauf` sert aux compteurs : le nombre affiche a cote d'une case est le
   nombre de maisons qui resteraient SI on la cochait, les autres filtres en
   place. Calcule sur le resultat final, il afficherait 0 partout. */
function passe(f, sauf){
  if (F.q){
    var mots = pliage(F.q).split(/\s+/).filter(Boolean);
    var champ = pliage(f.nom + ' ' + f.groupe + ' ' + f.resume.fr + ' ' +
                       f.resume.en + ' ' + lib(D.distinctions, f.distinction) +
                       ' ' + lib(D.pays, f.pays_origine));
    for (var i=0;i<mots.length;i++) if (champ.indexOf(mots[i]) < 0) return false;
  }
  /* La taille demande « qui prend un actif de N cles » : N doit tomber DANS
     la fourchette acceptee, pas au-dessus d'un minimum. */
  if (sauf !== 'taille' && F.taille){
    var n = parseInt(F.taille, 10);
    if (n < f.cles.min || n > f.cles.max) return false;
  }
  if (sauf !== 'dists' && F.dists.length &&
      F.dists.indexOf(f.distinction) < 0) return false;
  if (sauf !== 'modes' && F.modes.length){
    var ok = false;
    for (var a=0;a<F.modes.length;a++)
      if (f.modes.indexOf(F.modes[a]) >= 0) ok = true;
    if (!ok) return false;
  }
  if (sauf !== 'tranches' && F.tranches.length &&
      F.tranches.indexOf(f.investissement_cle.tranche) < 0) return false;
  if (sauf !== 'regions' && F.regions.length &&
      F.regions.indexOf(f.region) < 0) return false;
  if (sauf !== 'options' && F.options.length){
    for (var b=0;b<F.options.length;b++){
      var o = F.options[b];
      if (o === 'residences' && !f.residences_de_marque) return false;
      if (o === 'spa' && !f.spa_m2) return false;
      if (o === 'key' && !f.key_money_cle) return false;
    }
  }
  return true;
}
function resultat(){ return FI.filter(function(f){ return passe(f, null); }); }
function combien(groupe, valeur){
  var sauv = F[groupe];
  F[groupe] = (groupe === 'taille') ? valeur : [valeur];
  var n = FI.filter(function(f){ return passe(f, null); }).length;
  F[groupe] = sauv;
  return n;
}

/* --------------------------------------------------------------- tri --- */
var TRIS = [
  ['nom', function(a,b){ return a.nom.localeCompare(b.nom); }],
  ['cle', function(a,b){ return b.investissement_cle.eur_bas -
                                a.investissement_cle.eur_bas; }],
  ['nuitee', function(a,b){ return b.nuitee.haut - a.nuitee.haut; }],
  ['reseau', function(a,b){ return b.reseau.cles - a.reseau.cles; }],
  ['cles', function(a,b){ return a.cles.min - b.cles.min; }]
];
function comparateur(){
  for (var i=0;i<TRIS.length;i++) if (TRIS[i][0] === TRI) return TRIS[i][1];
  return TRIS[0][1];
}

/* ------------------------------------------------------------- rendu --- */
function carte(f){
  var d = lib(D.distinctions, f.distinction);
  return '<button class="carte" type="button" data-id="' + ech(f.id) + '">'
   + '<figure class="cadre" data-img="images/' + ech(f.id) + '.jpg"'
   +   ' data-ratio="4/3"><div class="ph" style="aspect-ratio:4/3">'
   +   '<b>' + ech(L === 'fr' ? 'Photo a deposer' : 'Photo to be supplied')
   +   '</b><span>images/' + ech(f.id) + '.jpg</span></div></figure>'
   + '<div class="carte-corps">'
   + '<div class="dist">' + ech(d) + '</div>'
   + '<h3>' + ech(f.nom) + '</h3>'
   + '<p class="grp">' + ech(f.groupe) + '</p>'
   + '<p class="res">' + ech(f.resume[L]) + '</p>'
   + '<dl>'
   +  '<dt>' + ech(t('c_taille')) + '</dt><dd>' + nb(f.cles.min) + '&ndash;'
   +  nb(f.cles.max) + '</dd>'
   +  '<dt>' + ech(t('c_nuitee')) + '</dt><dd>'
   +  argent(f.nuitee.bas, f.devise) + '&ndash;'
   +  argent(f.nuitee.haut, f.devise) + '</dd>'
   +  '<dt>' + ech(t('c_mode')) + '</dt><dd>'
   +  ech(lib(D.modes, f.modes[0])) + '</dd>'
   + '</dl></div></button>';
}

function dessiner(){
  var res = resultat().sort(comparateur());
  document.getElementById('grille').innerHTML =
    res.map(carte).join('');
  var v = document.getElementById('vide');
  v.hidden = res.length > 0;
  v.textContent = t('vide');
  var c = document.getElementById('compte');
  c.innerHTML = '<b>' + fmt(res.length === 1 ? t('compte_un') : t('compte_n'),
                            {n:nb(res.length)}) + '</b> '
              + ech(fmt(t('sur'), {t:nb(FI.length)}));
  compteurs();
  puces();
}

function compteurs(){
  var g = [['dists','f-dists'],['modes','f-modes'],['tranches','f-tranches'],
           ['regions','f-regions'],['options','f-options']];
  for (var i=0;i<g.length;i++){
    var boites = document.querySelectorAll(
      '#' + g[i][1] + ' input[type=checkbox]');
    for (var j=0;j<boites.length;j++){
      var n = combien(g[i][0], boites[j].getAttribute('data-v'));
      boites[j].parentNode.querySelector('.n').textContent = nb(n);
    }
  }
}

function puces(){
  var p = [];
  function add(cle, txt, groupe, valeur){
    p.push('<span class="puce">' + ech(txt) + '<button type="button" '
      + 'data-g="' + groupe + '" data-v="' + ech(valeur) + '" '
      + 'aria-label="' + ech(t('raz')) + '">&times;</button></span>');
  }
  if (F.taille) add('taille', nb(parseInt(F.taille,10)) + ' ' + t('u_cles'),
                    'taille', F.taille);
  F.dists.forEach(function(v){ add(v, lib(D.distinctions,v),'dists',v); });
  F.modes.forEach(function(v){ add(v, lib(D.modes,v),'modes',v); });
  F.tranches.forEach(function(v){ add(v, lib(D.tranches,v),'tranches',v); });
  F.regions.forEach(function(v){ add(v, lib(D.regions,v),'regions',v); });
  F.options.forEach(function(v){ add(v, t('o_'+v),'options',v); });
  document.getElementById('puces').innerHTML = p.join(' ');
}

/* -------------------------------------------------------------- fiche --- */
function ligne(k, v){
  return '<div class="k">' + ech(k) + '</div><div class="v">' + v + '</div>';
}
function ouvrir(id){
  var f = null;
  for (var i=0;i<FI.length;i++) if (FI[i].id === id) f = FI[i];
  if (!f) return;
  var dev = f.devise, o = [];

  o.push('<div class="fiche-h"><div><h2 id="fiche-nom">' + ech(f.nom)
        + '</h2><p class="grp">' + ech(f.groupe) + ' &middot; '
        + ech(lib(D.distinctions, f.distinction)) + '</p></div>'
        + '<button class="fermer" type="button" id="x" aria-label="'
        + ech(t('fermer')) + '">&times;</button></div>');
  o.push('<div class="fiche-c">');
  o.push('<figure class="cadre" data-img="images/' + ech(f.id) + '.jpg" '
        + 'data-ratio="16/9"><div class="ph" style="aspect-ratio:16/9"><b>'
        + ech(L === 'fr' ? 'Photo a deposer' : 'Photo to be supplied')
        + '</b><span>images/' + ech(f.id) + '.jpg</span></div></figure>');
  o.push('<p style="color:var(--doux);margin:22px 0 30px">'
        + ech(f.resume[L]) + '</p>');

  o.push('<div class="bloc"><h3>' + ech(t('fi_apercu')) + '</h3>'
   + '<div class="lignes">'
   + ligne(t('d_origine'), ech(lib(D.pays, f.pays_origine)))
   + ligne(t('d_cles'), nb(f.cles.min) + '&ndash;' + nb(f.cles.max) + ' '
           + ech(t('u_cles')))
   + ligne(t('d_nuitee'), argent(f.nuitee.bas, dev) + '&ndash;'
           + argent(f.nuitee.haut, dev) + ' <span style="color:var(--faible)">'
           + ech(t('u_nuit')) + '</span>')
   + ligne(t('d_cre'), an(f.annee_creation))
   + ligne(t('d_ges'), an(f.annee_premiere_gestion))
   + '</div></div>');

  var arg = ligne(t('d_invest'),
        argent(f.investissement_cle.bas, dev) + '&ndash;'
        + argent(f.investissement_cle.haut, dev))
   + ligne(t('d_projet'), argent(f.projet.bas, dev) + '&ndash;'
           + argent(f.projet.haut, dev));
  if (f.honoraires.base !== null)
    arg += ligne(t('d_base'), pct(f.honoraires.base))
         + ligne(t('d_incit'), pct(f.honoraires.incitation));
  arg += ligne(t('d_redev'),
    f.redevance === null ? '<span style="color:var(--faible)">'
      + ech(t('d_aucun')) + '</span>' : pct(f.redevance));
  arg += ligne(t('d_tech'), argent(f.services_techniques_cle, dev))
       + ligne(t('d_preouv'), argent(f.preouverture_cle, dev))
       + ligne(t('d_key'), f.key_money_cle
           ? argent(f.key_money_cle, dev)
           : '<span style="color:var(--faible)">' + ech(t('d_non')) + '</span>');
  o.push('<div class="bloc"><h3>' + ech(t('fi_argent')) + '</h3>'
        + '<div class="lignes">' + arg + '</div>'
        + '<p class="note">' + ech(t('n_base')) + '</p>'
        + (f.key_money_cle ? '<p class="note">' + ech(t('n_key')) + '</p>' : '')
        + '</div>');

  var md = f.modes.map(function(m){
    return '<span class="etiq on">' + ech(lib(D.modes, m)) + '</span>'; })
    .join('');
  o.push('<div class="bloc"><h3>' + ech(t('fi_contrat')) + '</h3>'
   + md
   + '<div class="lignes" style="margin-top:16px">'
   + ligne(t('d_duree'), nb(f.duree_contrat) + ' ' + ech(t('u_ans')))
   + ligne(t('d_montee'), nb(f.montee_en_puissance_mois) + ' '
           + ech(t('u_mois')))
   + ligne(t('d_reno'), nb(f.renovation_ans) + ' ' + ech(t('u_ans')))
   + '</div></div>');

  o.push('<div class="bloc"><h3>' + ech(t('fi_maison')) + '</h3>'
   + '<div class="lignes">'
   + ligne(t('d_suites'), nb(f.suites_pct) + (L === 'fr' ? ' %' : '%'))
   + ligne(t('d_tables'), nb(f.tables))
   + ligne(t('d_spa'), f.spa_m2 ? nb(f.spa_m2) + ' ' + ech(t('u_m2'))
           : ech(t('d_non')))
   + ligne(t('d_res'), f.residences_de_marque ? ech(t('d_oui'))
           : ech(t('d_non')))
   + '</div></div>');

  o.push('<div class="bloc"><h3>' + ech(t('fi_reseau')) + '</h3>'
   + '<div class="lignes">'
   + ligne(t('d_maisons'), nb(f.reseau.maisons))
   + ligne(t('d_total'), nb(f.reseau.cles) + ' ' + ech(t('u_cles')))
   + ligne(t('d_moy'), nb(f.reseau.taille_moyenne) + ' ' + ech(t('u_cles')))
   + '</div>'
   + '<h3 style="margin-top:24px">' + ech(t('fi_pays')) + '</h3>'
   + f.pays.map(function(p){
       return '<span class="etiq">' + ech(lib(D.pays, p)) + '</span>'; }).join('')
   + '</div>');

  o.push('<div class="bloc"><h3>' + ech(t('fi_presta')) + '</h3>'
   + D.prestations.map(function(p){
       var on = f.prestations.indexOf(p.cle) >= 0;
       return '<span class="etiq' + (on ? ' on' : '') + '">'
            + (on ? '' : '&minus; ') + ech(p[L]) + '</span>'; }).join(''));
  o.push('</div>');

  o.push('</div>');
  var fic = document.getElementById('fiche');
  fic.innerHTML = o.join('');
  fic.setAttribute('data-ouvert','oui');
  document.getElementById('voile').setAttribute('data-ouvert','oui');
  document.body.style.overflow = 'hidden';
  fic.scrollTop = 0;
  document.getElementById('x').focus();
  OUVERTE = id;
  if (location.hash.slice(1) !== id) history.replaceState(null,'','#'+id);
}
var OUVERTE = null;
function fermer(){
  document.getElementById('fiche').setAttribute('data-ouvert','non');
  document.getElementById('voile').setAttribute('data-ouvert','non');
  document.body.style.overflow = '';
  OUVERTE = null;
  if (location.hash) history.replaceState(null,'',location.pathname);
}

/* ---------------------------------------------------------- formulaire --- */
function dossier(ev){
  ev.preventDefault();
  var d = {
    nom: document.getElementById('d-nom').value.trim(),
    ville: document.getElementById('d-ville').value.trim(),
    cles: document.getElementById('d-cles').value.trim()
  };
  var manque = [];
  if (!d.nom) manque.push(t('fo_nom'));
  if (!d.ville) manque.push(t('fo_ville'));
  if (!d.cles) manque.push(t('fo_cles'));
  var r = document.getElementById('recu');
  r.hidden = false;
  if (manque.length){
    r.textContent = fmt(t('fo_manque'), {l:manque.join(', ')});
    return;
  }
  var mode = document.getElementById('d-mode');
  var dist = document.getElementById('d-dist');
  var parts = [d.nom, d.ville, nb(parseInt(d.cles,10)) + ' ' + t('u_cles'),
               mode.options[mode.selectedIndex].text,
               dist.options[dist.selectedIndex].text];
  r.textContent = fmt(t('fo_recu'), {r:parts.join(' — ')});
}

/* ------------------------------------------------------------ montage --- */
function cases(hote, liste, groupe, etiquette){
  var h = document.getElementById(hote);
  h.innerHTML = liste.map(function(x){
    return '<label><input type="checkbox" data-g="' + groupe + '" data-v="'
     + ech(x.cle) + '"><span class="lb">' + ech(etiquette(x))
     + '</span><span class="n"></span></label>';
  }).join('');
}

function retitrer(){
  var m = {'h-filtres':'h_filtres','raz':'raz','h-rech':'h_rech',
           'h-taille':'h_taille','h-dist':'h_dist','h-mode':'h_mode',
           'h-tranche':'h_tranche','h-region':'h_region','h-opt':'h_opt',
           'aide-taille':'aide_taille','l-tri':'l_tri',
           'l-nom':'fo_nom','l-tel':'fo_tel','l-ville':'fo_ville',
           'l-cles':'fo_cles','l-annee':'fo_annee','l-reno':'fo_reno',
           'l-mode':'fo_mode','l-dist':'fo_dist','l-mot':'fo_mot',
           'b-envoi':'fo_envoi'};
  for (var id in m){
    var n = document.getElementById(id);
    if (n) n.textContent = t(m[id]);
  }
  document.getElementById('q').placeholder =
    L === 'fr' ? 'Nom, groupe, pays' : 'Name, group, country';

  var lbs = document.querySelectorAll('.grp-f label .lb');
  var src = [];
  D.distinctions.forEach(function(x){ src.push(x[L]); });
  D.modes.forEach(function(x){ src.push(x[L]); });
  D.tranches.forEach(function(x){ src.push(x[L]); });
  D.regions.forEach(function(x){ src.push(x[L]); });
  ['residences','spa','key'].forEach(function(x){ src.push(t('o_'+x)); });
  for (var i=0;i<lbs.length && i<src.length;i++) lbs[i].textContent = src[i];

  var tl = document.getElementById('taille'), gard = tl.value;
  tl.innerHTML = '<option value="">' + ech(t('t_toutes')) + '</option>'
   + D.tailles.map(function(n){
       return '<option value="' + n + '">' + nb(n) + ' ' + ech(t('u_cles'))
            + '</option>'; }).join('');
  tl.value = gard;

  var tr = document.getElementById('tri'), gtr = tr.value;
  tr.innerHTML = TRIS.map(function(x){
    return '<option value="' + x[0] + '">' + ech(t('tri_'+x[0]))
         + '</option>'; }).join('');
  tr.value = gtr || TRI;

  var fm = document.getElementById('d-mode');
  fm.innerHTML = '<option value="">' + ech(t('fo_indif')) + '</option>'
   + D.modes.map(function(x){
       return '<option value="' + ech(x.cle) + '">' + ech(x[L])
            + '</option>'; }).join('');
  var fd = document.getElementById('d-dist');
  fd.innerHTML = '<option value="">' + ech(t('fo_indif')) + '</option>'
   + D.distinctions.map(function(x){
       return '<option value="' + ech(x.cle) + '">' + ech(x[L])
            + '</option>'; }).join('');
}

window.surLangue = function(l){
  L = l;
  if (!D) return;
  retitrer();
  dessiner();
  if (OUVERTE) ouvrir(OUVERTE);
};

function demarrer(d){
  D = d; FI = D.fiches;
  L = window.langue ? window.langue() : 'fr';
  cases('f-dists', D.distinctions, 'dists', function(x){ return x[L]; });
  cases('f-modes', D.modes, 'modes', function(x){ return x[L]; });
  cases('f-tranches', D.tranches, 'tranches', function(x){ return x[L]; });
  cases('f-regions', D.regions, 'regions', function(x){ return x[L]; });
  document.getElementById('f-options').innerHTML =
    ['residences','spa','key'].map(function(c){
      return '<label><input type="checkbox" data-g="options" data-v="' + c
       + '"><span class="lb"></span><span class="n"></span></label>';
    }).join('');
  retitrer();

  document.addEventListener('change', function(ev){
    var i = ev.target;
    if (i.type === 'checkbox' && i.getAttribute('data-g')){
      var g = i.getAttribute('data-g'), v = i.getAttribute('data-v');
      if (i.checked){ if (F[g].indexOf(v) < 0) F[g].push(v); }
      else F[g] = F[g].filter(function(x){ return x !== v; });
      dessiner();
    } else if (i.id === 'taille'){ F.taille = i.value; dessiner(); }
    else if (i.id === 'tri'){ TRI = i.value; dessiner(); }
  });
  var q = document.getElementById('q'), minuteur = null;
  q.addEventListener('input', function(){
    clearTimeout(minuteur);
    minuteur = setTimeout(function(){ F.q = q.value; dessiner(); }, 140);
  });
  document.getElementById('raz').addEventListener('click', function(){
    F = {q:'', taille:'', dists:[], modes:[], tranches:[], regions:[],
         options:[]};
    q.value = ''; document.getElementById('taille').value = '';
    var b = document.querySelectorAll('.grp-f input[type=checkbox]');
    for (var i=0;i<b.length;i++) b[i].checked = false;
    dessiner();
  });
  document.addEventListener('click', function(ev){
    var c = ev.target.closest('.carte');
    if (c){ ouvrir(c.getAttribute('data-id')); return; }
    if (ev.target.id === 'x' || ev.target.id === 'voile'){ fermer(); return; }
    var p = ev.target.closest('.puce button');
    if (p){
      var g = p.getAttribute('data-g'), v = p.getAttribute('data-v');
      if (g === 'taille'){ F.taille = '';
        document.getElementById('taille').value = ''; }
      else {
        F[g] = F[g].filter(function(x){ return x !== v; });
        var bo = document.querySelector('.grp-f input[data-g="' + g
                  + '"][data-v="' + v + '"]');
        if (bo) bo.checked = false;
      }
      dessiner();
    }
  });
  document.addEventListener('keydown', function(ev){
    if (ev.key === 'Escape' && OUVERTE) fermer();
  });
  /* Un fragment qui change DANS la page ne recharge pas le document : sans
     cet ecouteur, un lien vers #identifiant depuis la page elle-meme se
     contente de faire defiler. */
  window.addEventListener('hashchange', function(){
    var h = location.hash.slice(1);
    if (!h){ if (OUVERTE) fermer(); return; }
    if (h !== OUVERTE) ouvrir(h);
  });
  document.getElementById('dossier').addEventListener('submit', dossier);

  dessiner();
  var h = location.hash.slice(1);
  if (h) ouvrir(h);
}

fetch('prestige.json')
  .then(function(r){ if (!r.ok) throw new Error(r.status); return r.json(); })
  .then(demarrer)
  .catch(function(err){
    document.getElementById('grille').innerHTML =
      '<div class="vide">prestige.json : ' + ech(err.message) + '</div>';
  });
"""


def page_collection(D):
    corps = (entete('collection')
             + CORPS_COLLECTION
             .replace('__H1_FR__', e('Vingt-cinq maisons, et ce qu\'elles '
                                     'demandent'))
             .replace('__H1_EN__', e('Twenty-five brands, and what they ask '
                                     'for'))
             .replace('__CH_FR__', e(
                 'Le filtre le plus utile est le premier : la taille de votre '
                 'actif. Une maison qui accepte de vingt-quatre a soixante '
                 'cles ne prendra pas un hotel de deux cents chambres, et '
                 'l\'inverse est tout aussi vrai.'))
             .replace('__CH_EN__', e(
                 'The most useful filter is the first one: the size of your '
                 'asset. A brand that accepts twenty-four to sixty keys will '
                 'not take a two-hundred-room hotel, and the reverse is just '
                 'as true.'))
             .replace('__F1_FR__', e('Proposer un actif'))
             .replace('__F1_EN__', e('Submit an asset'))
             .replace('__F2_FR__', e(
                 'Demonstration : le formulaire ne part nulle part. Il montre '
                 'ce qu\'un service developpement demande en premier, et dans '
                 'quel ordre.'))
             .replace('__F2_EN__', e(
                 'Demonstration: the form goes nowhere. It shows what a '
                 'development team asks for first, and in what order.'))
             + pied())
    # Le nombre de maisons du titre est calcule, pas ecrit : ajouter une
    # maison ne doit pas laisser un titre faux derriere elle.
    n = len(D['fiches'])
    corps = corps.replace('Vingt-cinq maisons', _en_lettres(n) + ' maisons')
    corps = corps.replace('Twenty-five brands', _en_lettres_en(n) + ' brands')
    return squelette(
        'La collection — Maisons de Prestige',
        'Les maisons hotelieres de prestige, leurs modes d\'exploitation, '
        'leurs honoraires et la taille d\'actif qu\'elles acceptent.',
        corps, JS_LANGUE + '\n' + JS_COLLECTION)


_LETTRES_FR = {
    20: 'Vingt', 21: 'Vingt et une', 22: 'Vingt-deux', 23: 'Vingt-trois',
    24: 'Vingt-quatre', 25: 'Vingt-cinq', 26: 'Vingt-six',
    27: 'Vingt-sept', 28: 'Vingt-huit', 29: 'Vingt-neuf', 30: 'Trente',
}
_LETTRES_EN = {
    20: 'Twenty', 21: 'Twenty-one', 22: 'Twenty-two', 23: 'Twenty-three',
    24: 'Twenty-four', 25: 'Twenty-five', 26: 'Twenty-six',
    27: 'Twenty-seven', 28: 'Twenty-eight', 29: 'Twenty-nine', 30: 'Thirty',
}


def _en_lettres(n):
    return _LETTRES_FR.get(n, str(n))


def _en_lettres_en(n):
    return _LETTRES_EN.get(n, str(n))


def main():
    D = charger()
    pages = {'index.html': page_accueil(D),
             'collection.html': page_collection(D)}
    ecrits = []
    for nom, html in pages.items():
        chemin = os.path.join(DEMO, nom)
        with open(chemin, 'w', encoding='utf-8') as f:
            f.write(html)
        ecrits.append((chemin, len(html.encode('utf-8'))))
    return ecrits


if __name__ == '__main__':
    for c, n in main():
        print('%s  (%d octets)' % (c, n))
    # Un cadre sans ratio applique se verrait a l'oeil, une fois, sur une
    # page — pas sur neuf. On compte ici, le controle complet est dans
    # tests-prestige.py.
    tout = ''
    for nom in ('index.html', 'collection.html'):
        tout += open(os.path.join(DEMO, nom), encoding='utf-8').read()
    print('%d cadres d\'image, %d ratios appliques'
          % (len(re.findall(r'data-img="', tout)),
             len(re.findall(r'style="aspect-ratio:', tout))))
