# CRAC ! — Eduardo Skate Rush

> *« Après avoir pratiqué le skate un mois durant, Eduardo se sent chaud à braver
> les dangers de la ville ! Mais sa bravoure va le mener à sa perte… »*

Reprise complète de **Eduardo_fait_du_skate** (2016) : mêmes têtes, mêmes frites,
même amaretto, même « Crac ! » — mais un moteur réécrit de zéro, un décor qui
plante Eduardo dans **les rues de Mons**, une version navigateur qui s'installe
sur iPhone et Android, et le record de 2016 récupéré depuis l'ancienne base
SQLite.

Eduardo dévale la ville avec, derrière lui, le **beffroi**, la **collégiale
Sainte-Waudru**, l'**hôtel de ville de la Grand-Place**, la coque blanche de la
**gare Calatrava** et les maisons à pignons à redents.

Le nom vient du message de fin de l'original : `message('Crac !')`.

---

## Ce qu'il y a dans le dossier

```
CRAC_Eduardo_Skate_Rush/
├── python/          Version bureau (macOS / Windows / Linux) — pygame-ce
│   ├── main.py          point d'entrée
│   ├── crac/            config, monde, rendu, audio, scores
│   │   └── mons.py      silhouettes des monuments montois (source unique)
│   └── assets/          images, sons, police
├── web/             Version navigateur + mobile (PWA installable)
│   ├── index.html
│   ├── js/              même découpage qu'en Python
│   │   └── mons.js      généré depuis crac/mons.py — ne pas éditer
│   └── sw.js            fonctionnement hors-ligne
├── tools/
│   └── prepare_assets.py   reconstruit tous les assets depuis le jeu de 2016
├── package.json / capacitor.config.json   empaquetage iOS et Android
├── INSTALLATION_IPHONE.md  ← comment mettre le jeu sur l'iPhone 13 Pro
└── CHANGEMENTS.md          ce qui a changé depuis 2016, en détail
```

---

## Jouer tout de suite

### Sur l'ordinateur (Python)

```bash
cd CRAC_Eduardo_Skate_Rush/python && pip3 install -r requirements.txt && python3 main.py
```

| Touche | Action |
|---|---|
| `Espace` / `↑` / clic | Sauter (maintenir = saut plus haut) |
| `↓` | S'accroupir — passer sous le drapeau italien |
| `P` | Pause |
| `M` | Sourdine |
| `F11` | Plein écran |
| `Échap` | Menu, puis quitter |

### Dans le navigateur

```bash
cd CRAC_Eduardo_Skate_Rush && python3 -m http.server 8123 --directory web
```

Puis ouvrez <http://localhost:8123>.

### Sur le téléphone

Voir **[INSTALLATION_IPHONE.md](INSTALLATION_IPHONE.md)** : trois chemins, du
plus simple (GitHub Pages + « Sur l'écran d'accueil », aucun outil à installer)
à la vraie application native compilée dans Xcode.

Une fois le dépôt GitHub relié, publier une nouvelle version tient en une
commande :

```bash
./tools/publier.sh "ce que j'ai changé"
```

---

## Régénérer les assets

Les sprites ne sont pas dessinés à la main : ils sont **reconstruits** à partir
des fichiers d'origine par un script, qui détoure automatiquement les fonds et
rééchantillonne en haute résolution.

```bash
cd CRAC_Eduardo_Skate_Rush && python3 tools/prepare_assets.py
```

Le script cherche le jeu de 2016 dans le dossier parent. Pour pointer ailleurs :
`python3 tools/prepare_assets.py --src /chemin/vers/Eduardo_fait_du_skate`.

---

## Les deux versions sont le même jeu

`python/crac/world.py` et `web/js/world.js` sont deux écritures de la **même**
simulation : mêmes constantes, même gravité, mêmes règles d'apparition. Un bot
qui joue parfaitement atteint ~285 points en 5 minutes des deux côtés, à
quelques unités près. Si vous modifiez une valeur de `config.py`, reportez-la
dans `config.js` (et inversement).

Le décor, lui, ne se recopie pas à la main : les monuments sont décrits une
seule fois dans `python/crac/mons.py`, et `tools/prepare_assets.py` en génère
`web/js/mons.js`. Les deux versions partagent même leur générateur
pseudo-aléatoire (`mulberry32`), si bien que la ville est disposée **exactement**
de la même façon des deux côtés. Pour déplacer un monument ou en ajouter un,
éditez `mons.py` puis relancez le script.

---

## Crédits

- Jeu, idée et photos originales : Guillaume Lhost (2016).
- Police **Brady Bunch Remastered** : Adam Nerland / Insanitype! (freeware, 2001).
- Musiques et photos : celles du projet d'origine. Le jeu embarque des visuels de
  personnes réelles et une pochette de bouteille : **projet privé, à ne pas
  publier sur une boutique d'applications** sans l'accord des intéressés.
