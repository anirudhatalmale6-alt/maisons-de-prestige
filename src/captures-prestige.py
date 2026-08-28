# -*- coding: utf-8 -*-
"""Captures du site noir. Fenetre fixe, jamais full_page."""

import http.server
import os
import socket
import threading

from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
from chemins import dossier_pages   # noqa: E402
DEMO = dossier_pages(ICI)

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
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = 'http://127.0.0.1:%d/' % port

with sync_playwright() as p:
    nav = p.chromium.launch()
    pg = nav.new_page(viewport={'width': 1280, 'height': 820})

    def prise(nom):
        pg.screenshot(path=os.path.join(ICI, nom))
        print(nom)

    pg.goto(base + 'index.html', wait_until='networkidle')
    pg.wait_for_timeout(300)
    prise('pr-1-accueil.png')

    pg.mouse.wheel(0, 1500)
    pg.wait_for_timeout(350)
    prise('pr-2-manifeste.png')

    pg.mouse.wheel(0, 1500)
    pg.wait_for_timeout(350)
    prise('pr-3-distinctions.png')

    pg.mouse.wheel(0, 1400)
    pg.wait_for_timeout(350)
    prise('pr-4-modes.png')

    pg.goto(base + 'collection.html', wait_until='networkidle')
    pg.wait_for_selector('.grille .carte')
    pg.mouse.wheel(0, 420)
    pg.wait_for_timeout(350)
    prise('pr-5-collection.png')

    # Le filtre qui fait le site : « mon actif fait 250 cles, qui le prend ».
    pg.select_option('#taille', '250')
    pg.wait_for_timeout(400)
    prise('pr-6-taille.png')

    pg.click('#raz')
    pg.wait_for_timeout(250)
    pg.evaluate("()=>document.querySelector('.carte').click()")
    pg.wait_for_selector('.fiche[data-ouvert=oui]')
    pg.wait_for_timeout(300)
    pg.evaluate("()=>{document.querySelector('.fiche').scrollTop = 430;}")
    pg.wait_for_timeout(250)
    prise('pr-7-fiche-honoraires.png')

    pg.keyboard.press('Escape')
    pg.wait_for_timeout(200)
    pg.click('.langue button[data-l="en"]')
    pg.wait_for_timeout(450)
    pg.mouse.wheel(0, 420)
    pg.wait_for_timeout(300)
    prise('pr-8-anglais.png')

    pg.click('.langue button[data-l="fr"]')
    pg.wait_for_timeout(300)

    # Le formulaire proprietaire.
    pg.evaluate("()=>document.getElementById('proposer')"
                ".scrollIntoView({block:'start'})")
    pg.wait_for_timeout(400)
    prise('pr-9-proposer.png')

    pg.set_viewport_size({'width': 390, 'height': 780})
    pg.goto(base + 'index.html', wait_until='networkidle')
    pg.wait_for_timeout(400)
    prise('pr-10-mobile.png')

    nav.close()

srv.shutdown()
srv.server_close()
