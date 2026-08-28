# -*- coding: utf-8 -*-
"""La charte du site noir.

Une seule feuille, injectee dans les deux pages. Elle n'est PAS partagee avec
l'annuaire de franchises : c'est un autre site, avec une autre promesse. La
partager aurait ete pratique et aurait fini par contaminer l'un des deux.

Trois regles tenues partout :

  - le noir n'est pas #000. Un noir pur sur un ecran moderne fait vibrer le
    texte clair et fatigue en trois paragraphes. On travaille a #0b0b0c, et
    les surfaces montent par paliers de quelques points seulement.
  - pas de blanc pur non plus : #ece7df, casse chaud. Le contraste reste
    au-dessus de 13:1 sur le fond, largement au-dessus du seuil AA.
  - une seule couleur d'accent, un champagne desature. Deux couleurs
    d'accent sur un site de luxe donnent un site de promotion.
"""

CSS = """
:root{
  --noir:#0b0b0c;      /* le fond */
  --noir2:#121214;     /* surface posee dessus */
  --noir3:#191A1D;     /* surface au-dessus encore */
  --trait:rgba(236,231,223,.13);
  --trait2:rgba(236,231,223,.26);
  --texte:#ece7df;
  --doux:#a8a199;      /* texte secondaire */
  --faible:#7d766e;    /* legendes */
  --or:#c8a96a;        /* l'unique accent */
  --or-doux:rgba(200,169,106,.14);
  --serif:'Iowan Old Style','Palatino Linotype',Palatino,Georgia,
          'Times New Roman',serif;
  --sans:system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{
  background:var(--noir);color:var(--texte);font-family:var(--sans);
  font-size:16px;line-height:1.62;-webkit-font-smoothing:antialiased;
  overflow-x:hidden}
a{color:inherit}
img{max-width:100%}
.enveloppe{max-width:1220px;margin:0 auto;padding:0 34px}

/* ---------------------------------------------------------------- en-tete */
.haut{position:sticky;top:0;z-index:60;background:rgba(11,11,12,.86);
 backdrop-filter:blur(14px);border-bottom:1px solid var(--trait)}
.haut-in{display:flex;align-items:center;gap:26px;
 max-width:1220px;margin:0 auto;padding:16px 34px}
.marque{font-family:var(--serif);font-size:21px;letter-spacing:.10em;
 text-transform:uppercase;text-decoration:none;white-space:nowrap;
 display:flex;align-items:baseline;gap:9px}
.marque .mot{white-space:nowrap}
.marque b{color:var(--or);font-weight:400}
.ph-marque{font-family:var(--sans);font-size:9.5px;letter-spacing:.06em;
 text-transform:none;color:var(--or);border:1px dashed var(--trait2);
 border-radius:4px;padding:1px 6px;white-space:nowrap}
.nav{display:flex;gap:22px;margin-left:auto;align-items:center}
.nav a{font-size:12.5px;letter-spacing:.13em;text-transform:uppercase;
 text-decoration:none;color:var(--doux);padding:6px 0;
 border-bottom:1px solid transparent}
.nav a:hover,.nav a[aria-current]{color:var(--texte);border-bottom-color:var(--or)}
.langue{display:flex;border:1px solid var(--trait);border-radius:2px;
 overflow:hidden}
.langue button{background:none;border:0;color:var(--doux);cursor:pointer;
 font:inherit;font-size:11.5px;letter-spacing:.12em;padding:6px 11px}
.langue button[aria-pressed=true]{background:var(--or);color:#17130c}

/* ------------------------------------------------------------------- hero */
/* Le titre n'est PAS pose par-dessus l'image. Une superposition tient tant
   que le texte est plus court que la photo ; le jour ou il fait cinq lignes,
   il remonte sous l'en-tete colle et se fait couper. Deux colonnes ne
   peuvent pas se chevaucher. */
.hero{padding:58px 0 76px;border-bottom:1px solid var(--trait)}
.hero-in{display:grid;grid-template-columns:1.05fr .95fr;gap:54px;
 align-items:center}
.surtitre{font-size:11.5px;letter-spacing:.30em;text-transform:uppercase;
 color:var(--or);margin:0 0 18px}
h1{font-family:var(--serif);font-weight:400;font-size:clamp(31px,4.4vw,54px);
 line-height:1.1;letter-spacing:-.01em;margin:0 0 20px;max-width:17ch}
.chapo{font-size:18px;color:var(--doux);max-width:56ch;margin:0}

/* ---------------------------------------------------------------- sections */
section{padding:78px 0;border-bottom:1px solid var(--trait)}
.titre-sec{font-family:var(--serif);font-weight:400;
 font-size:clamp(25px,3.4vw,38px);line-height:1.15;margin:0 0 16px;
 max-width:22ch}
.intro-sec{color:var(--doux);max-width:62ch;margin:0 0 40px}
.eyebrow{font-size:11px;letter-spacing:.28em;text-transform:uppercase;
 color:var(--or);margin:0 0 14px}

/* ------------------------------------------------------------ le manifeste */
.manifeste{display:grid;grid-template-columns:1fr 1fr;gap:52px}
.manifeste p{margin:0 0 18px;color:var(--doux)}
.manifeste p:first-child{font-family:var(--serif);font-size:21px;
 line-height:1.5;color:var(--texte)}
.manifeste strong{color:var(--texte);font-weight:600}

/* ---------------------------------------------------------- les paliers */
.paliers{display:grid;grid-template-columns:repeat(auto-fit,minmax(215px,1fr));
 gap:1px;background:var(--trait);border:1px solid var(--trait)}
.palier{background:var(--noir);padding:26px 22px}
.palier h3{font-family:var(--serif);font-weight:400;font-size:20px;
 margin:16px 0 8px}
.palier p{margin:0;font-size:14px;color:var(--doux);line-height:1.55}
.palier .n{font-size:11px;letter-spacing:.22em;color:var(--or)}

/* ------------------------------------------------------------- les chiffres */
.chiffres{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));
 gap:34px}
.chiffre{border-top:1px solid var(--or);padding-top:16px}
.chiffre b{display:block;font-family:var(--serif);font-weight:400;
 font-size:clamp(30px,4.2vw,46px);line-height:1}
.chiffre span{display:block;margin-top:8px;font-size:12px;letter-spacing:.14em;
 text-transform:uppercase;color:var(--faible)}

/* ------------------------------------------------------------- les modes */
.modes{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));
 gap:26px}
.mode{border:1px solid var(--trait);padding:28px 24px;background:var(--noir2)}
.mode h3{font-family:var(--serif);font-weight:400;font-size:22px;margin:0 0 6px}
.mode .base{font-size:12px;letter-spacing:.05em;color:var(--or);
 margin:0 0 14px;line-height:1.5}
.mode p{margin:0;color:var(--doux);font-size:14.5px}

/* -------------------------------------------------------------- les cartes */
.grille{display:grid;grid-template-columns:repeat(auto-fill,minmax(292px,1fr));
 gap:26px}
.carte{background:var(--noir2);border:1px solid var(--trait);
 display:flex;flex-direction:column;text-align:left;padding:0;color:inherit;
 font:inherit;cursor:pointer;transition:border-color .18s,transform .18s;
 text-decoration:none}
.carte *{text-decoration:none}
.carte:hover{border-color:var(--trait2);transform:translateY(-2px)}
.carte-corps{padding:22px 22px 24px;display:flex;flex-direction:column;
 flex:1}
.carte .dist{font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;
 color:var(--or);margin-bottom:11px}
.carte h3{font-family:var(--serif);font-weight:400;font-size:23px;
 line-height:1.15;margin:0 0 4px}
.carte .grp{font-size:12.5px;color:var(--faible);margin:0 0 13px}
.carte .res{font-size:14px;color:var(--doux);margin:0 0 18px;flex:1}
.carte dl{margin:0;padding-top:15px;border-top:1px solid var(--trait);
 display:grid;grid-template-columns:auto 1fr;gap:5px 14px;font-size:13px}
.carte dt{color:var(--faible)}
.carte dd{margin:0;text-align:right;font-variant-numeric:tabular-nums}

/* ----------------------------------------------------------------- images */
.cadre{position:relative;display:block;margin:0;overflow:hidden;
 background:var(--noir3)}
.cadre .ph{display:flex;flex-direction:column;align-items:center;
 justify-content:center;gap:6px;width:100%;
 border:1px dashed var(--trait2);color:var(--faible);text-align:center;
 padding:16px}
.cadre .ph b{font-weight:600;font-size:12px;letter-spacing:.14em;
 text-transform:uppercase;color:var(--doux)}
.cadre .ph span{font-size:11.5px;word-break:break-all;max-width:90%}

/* ---------------------------------------------------------------- le ruban */
.ruban{background:var(--noir2)}
.ruban-in{display:flex;gap:40px;align-items:center;flex-wrap:wrap}
.ruban-txt{flex:1;min-width:280px}
.bouton{display:inline-block;background:var(--or);color:#17130c;
 text-decoration:none;font-size:12.5px;letter-spacing:.16em;
 text-transform:uppercase;padding:15px 30px;border:0;cursor:pointer;
 font-family:var(--sans);font-weight:600}
.bouton:hover{background:#d8bc82}
.bouton.fantome{background:none;color:var(--texte);
 border:1px solid var(--trait2)}
.bouton.fantome:hover{background:rgba(236,231,223,.06)}

/* ------------------------------------------------------------------ filtres */
.travail{display:grid;grid-template-columns:288px 1fr;gap:40px;
 align-items:start;padding:36px 0 70px}
.panneau{position:sticky;top:78px;border:1px solid var(--trait);
 background:var(--noir2);max-height:calc(100vh - 108px);overflow:auto}
.pan-h{padding:16px 20px;border-bottom:1px solid var(--trait);
 display:flex;align-items:center;gap:10px}
.pan-h h2{font-size:11px;letter-spacing:.22em;text-transform:uppercase;
 margin:0;color:var(--doux);font-weight:600}
.pan-h button{margin-left:auto;background:none;border:0;color:var(--or);
 font:inherit;font-size:12px;cursor:pointer;text-decoration:underline}
.grp-f{padding:18px 20px;border-bottom:1px solid var(--trait)}
.grp-f:last-child{border-bottom:0}
.grp-f h3{font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;
 color:var(--faible);margin:0 0 12px;font-weight:600}
.grp-f label{display:flex;align-items:center;gap:9px;padding:4px 0;
 font-size:14px;cursor:pointer;color:var(--doux)}
.grp-f label:hover{color:var(--texte)}
.grp-f input[type=checkbox]{accent-color:var(--or);width:15px;height:15px;
 flex:none}
.grp-f .n{margin-left:auto;font-size:12px;color:var(--faible);
 font-variant-numeric:tabular-nums}
.champ,select.champ{width:100%;background:var(--noir3);color:var(--texte);
 border:1px solid var(--trait);padding:10px 12px;font:inherit;font-size:14px;
 border-radius:0}
.champ:focus{outline:1px solid var(--or);outline-offset:-1px}
.champ::placeholder{color:var(--faible)}

/* ------------------------------------------------------------- resultats */
.barre{display:flex;align-items:center;gap:16px;flex-wrap:wrap;
 padding-bottom:22px;border-bottom:1px solid var(--trait);margin-bottom:26px}
.compte{font-family:var(--serif);font-size:19px}
.compte b{color:var(--or);font-weight:400}
.tri{margin-left:auto;display:flex;align-items:center;gap:9px;
 font-size:13px;color:var(--faible)}
.tri select{background:var(--noir2);color:var(--texte);
 border:1px solid var(--trait);padding:7px 10px;font:inherit;font-size:13px}
.vide{border:1px dashed var(--trait2);padding:48px 26px;text-align:center;
 color:var(--doux)}
.puce{display:inline-flex;align-items:center;gap:8px;background:var(--or-doux);
 border:1px solid rgba(200,169,106,.32);color:var(--texte);
 padding:5px 10px;font-size:12.5px}
.puce button{background:none;border:0;color:var(--or);cursor:pointer;
 font:inherit;line-height:1;padding:0}

/* ---------------------------------------------------------------- la fiche */
.voile{position:fixed;inset:0;background:rgba(6,6,7,.82);z-index:90;
 display:none}
.voile[data-ouvert=oui]{display:block}
.fiche{position:fixed;top:0;right:0;bottom:0;width:min(660px,100%);
 background:var(--noir);border-left:1px solid var(--trait);z-index:91;
 overflow:auto;display:none}
.fiche[data-ouvert=oui]{display:block}
.fiche-h{position:sticky;top:0;background:var(--noir);z-index:2;
 border-bottom:1px solid var(--trait);padding:20px 30px;display:flex;
 align-items:flex-start;gap:16px}
.fiche-h h2{font-family:var(--serif);font-weight:400;font-size:28px;
 line-height:1.15;margin:0}
.fiche-h .grp{font-size:12.5px;color:var(--faible);margin:5px 0 0}
.fermer{margin-left:auto;background:none;border:1px solid var(--trait);
 color:var(--doux);width:36px;height:36px;cursor:pointer;font-size:17px;
 flex:none;line-height:1}
.fermer:hover{border-color:var(--trait2);color:var(--texte)}
.fiche-c{padding:26px 30px 60px}
.bloc{margin-bottom:32px}
.bloc h3{font-size:10.5px;letter-spacing:.22em;text-transform:uppercase;
 color:var(--or);margin:0 0 14px;font-weight:600}
.lignes{display:grid;grid-template-columns:1fr auto;gap:9px 20px;
 font-size:14.5px}
.lignes .k{color:var(--doux)}
.lignes .v{text-align:right;font-variant-numeric:tabular-nums}
.note{font-size:13px;color:var(--faible);line-height:1.55;
 border-left:2px solid var(--trait2);padding-left:14px;margin-top:14px}
.etiq{display:inline-block;font-size:12px;border:1px solid var(--trait);
 padding:4px 10px;margin:0 6px 6px 0;color:var(--doux)}
.etiq.on{border-color:rgba(200,169,106,.4);color:var(--texte);
 background:var(--or-doux)}

/* ----------------------------------------------------------- le formulaire */
.form{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.form .large{grid-column:1/-1}
.form label{display:block;font-size:11.5px;letter-spacing:.14em;
 text-transform:uppercase;color:var(--faible);margin-bottom:7px}
.form textarea{min-height:110px;resize:vertical}
.oblig{color:var(--or)}
.recu{border:1px solid rgba(200,169,106,.4);background:var(--or-doux);
 padding:20px;font-size:14.5px}

/* --------------------------------------------------------------- pied */
footer{padding:56px 0 70px;color:var(--faible);font-size:13.5px}
footer a{color:var(--doux)}
.avert{border:1px dashed var(--trait2);padding:16px 18px;margin-bottom:28px;
 color:var(--doux);font-size:13.5px}
.liens-sites{display:flex;gap:26px;flex-wrap:wrap;margin-top:18px}

/* -------------------------------------------------------------- reglages */
@media(max-width:900px){
  .hero-in{grid-template-columns:1fr;gap:30px}
  .hero-img{order:-1}
  .manifeste{grid-template-columns:1fr;gap:0}
  .travail{grid-template-columns:1fr;gap:26px}
  .panneau{position:static;max-height:none}
}
@media(max-width:620px){
  .enveloppe,.haut-in,.hero-txt{padding-left:20px;padding-right:20px}
  section{padding:52px 0}
  .haut-in{gap:14px;flex-wrap:wrap}
  .marque{font-size:17px}
  .ph-marque{font-size:9px;padding:1px 5px}
  .nav{gap:15px;order:3;width:100%;margin-left:0;
   border-top:1px solid var(--trait);padding-top:10px}
  .nav a{font-size:11.5px}
  .langue{margin-left:auto}
  .hero{padding:34px 0 48px}
  .fiche-h,.fiche-c{padding-left:20px;padding-right:20px}
  .form{grid-template-columns:1fr}
  }
"""
