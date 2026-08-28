# Maisons de Prestige — demonstration

Site de demonstration pour les **enseignes hotelieres cinq etoiles**, separe
de l'annuaire de franchises et de la section hotellerie de chaine.

- Accueil : `index.html`
- La collection : `collection.html`
- Donnees : `prestige.json`
- Sources : `src/`

> **Tout est fictif.** Neuf groupes, vingt-cinq maisons, tous les chiffres.
> Aucun groupe hotelier existant n'est nomme ni represente. Les deux pages
> portent `noindex` tant que le nom du site n'est pas arrete.

---

## Pourquoi un site a part, et pas un filtre « 5 etoiles »

C'est le meme raisonnement qui avait sorti l'hotellerie de l'annuaire
generaliste, pousse d'un cran. Au sommet de la gamme, le metier cesse de se
mesurer dans les memes unites :

| | Hotellerie de chaine | Maisons de prestige |
|---|---|---|
| Contrat habituel | franchise | **contrat de gestion** |
| Ce que paie le proprietaire | une redevance | **honoraires de base** (% du CA total) **+ honoraires d'incitation** (% du RBE) |
| Sens de l'argent | du proprietaire vers le groupe | le groupe peut **apporter** du capital (key money) |
| Avant l'ouverture | droit d'entree | services techniques + budget de pre-ouverture, par cle |
| Question du proprietaire | « combien ca coute » | « a quel **prix moyen de la nuitee** cette marque me positionne » |

Mis dans une seule liste, cela donne des colonnes vides sur les trois quarts
des lignes, et un filtre par redevance qui compare un pourcentage de chiffre
d'affaires a un pourcentage de resultat. **Ce ne sont pas les memes nombres.**

Consequence assumee : les trois marques de luxe qui figuraient dans la
section hotellerie n'y sont plus, elles sont ici. Une marque a deux endroits,
c'est un total qui se contredit — et un controle automatique le verifie.

---

## Ce que le site sait faire

- **Filtrer par taille d'actif.** « Mon hotel fait 250 cles, qui le prend ? »
  Le nombre doit tomber **dans** la fourchette acceptee par la maison, pas
  seulement depasser un minimum.
- **Compteurs predictifs.** Le nombre a cote d'une case est le nombre de
  maisons qui resteraient **si on la cochait**, les autres filtres en place.
- **Cinq distinctions** : palace urbain, maison de luxe, resort de prestige,
  domaine et demeure historique, lifestyle de prestige.
- **Quatre modes d'exploitation** : gestion, affiliation a une collection,
  franchise de marque, bail.
- **Francais / anglais**, devise par pays d'origine, classement sur une
  valeur de reference en euros (taux figes).
- **Formulaire proprietaire** : il demande ce qu'un service developpement
  demande en premier. Il n'envoie rien.

---

## Regles de coherence tenues par les donnees

Chaque fiche reste plausible seule ; c'est l'ensemble qui trahit une donnee
tiree n'importe comment. Sont **calculees, jamais tirees** :

- le **cout du projet** = investissement par cle x taille acceptee ;
- les **cles du reseau** = nombre d'adresses x taille moyenne.

Sont **interdites** :

- un palace ou une maison de luxe qui se franchise ;
- des honoraires d'incitation sans contrat de gestion ;
- une redevance sans franchise ni affiliation ;
- un apport du groupe chez un franchiseur ;
- deux maisons du meme groupe dans la meme distinction ;
- une maison qui porte le nom de son groupe.

---

## Reconstruire

```sh
cd src
python3 prestige.py          # ecrit prestige.json
python3 page_prestige.py     # ecrit index.html et collection.html
python3 tests-prestige.py    # 95 controles
python3 captures-prestige.py # captures d'ecran (playwright)
```

La construction est **reproductible** : graine fixe, deux executions donnent
le meme fichier au bit pres. Un controle le verifie.

---

## Les images

Chaque emplacement est un cadre pointille qui **porte deja le ratio de
l'image attendue** — la page ne saute pas le jour ou le fichier arrive.

| Fichier | Ratio | Ou |
|---|---|---|
| `images/accueil-bandeau.jpg` | 4/5 | accueil, en-tete |
| `images/<identifiant>.jpg` | 4/3 | cartes |
| `images/<identifiant>.jpg` | 16/9 | fiche detaillee |

Les identifiants sont ceux de `prestige.json` (`alvear-palacios`,
`cassiopee-collection`, …).

---

## A regler

1. **Le nom du site.** « Maisons de Prestige » est un placeholder, signale
   par une pastille `nom a definir` dans l'en-tete.
2. **Les domaines temporaires.** Deux constantes a changer, toutes les deux
   en haut de `src/page_prestige.py` :
   `URL_ANNUAIRE` et `URL_HOTELLERIE`. Cote annuaire, la constante
   symetrique est `URL_PRESTIGE`, en haut de `page_hotels.py`.
3. **Les photos.**
4. **Le canal de reception** des dossiers proprietaires.

---

## Import

`import-modele-prestige.csv` (point-virgule, UTF-8 avec BOM) donne les
trente-trois colonnes attendues et deux lignes d'exemple.
