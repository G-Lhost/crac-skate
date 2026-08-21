# Ce qui a changé depuis `Ed_Skate.py` (2016)

Le jeu est le même : Eduardo, sa planche, les frites, les altères, l'amaretto,
les béquilles, Bale, Ezgy, le drapeau italien, et « Crac ! » à la fin. C'est le
moteur qui a été refait.

## Les cinq corrections qui changent vraiment le jeu

### 1. La vitesse ne dépend plus de la puissance de la machine

La boucle d'origine n'appelait jamais `horloge.tick()` — il n'y avait que
`pygame.display.update()`. Les obstacles avançaient de `obstacle_vitesse`
pixels **par tour de boucle**, pas par seconde : sur un PC de 2016 le jeu était
jouable, sur une machine d'aujourd'hui Eduardo traverse l'écran en un clin
d'œil.

Tout est maintenant exprimé en pixels **par seconde** et multiplié par le temps
réellement écoulé (`dt`), borné à 1/30 s pour encaisser un décrochage. Le jeu
se joue pareil à 30, 60 ou 144 images par seconde.

### 2. Le saut a une vraie physique

Avant : `y_mouvement` valait `-pixel` en montée puis `+pixel` en descente, avec
un demi-tour quand `y_skate <= 125`. Un saut en triangle, à vitesse constante,
et une comparaison de flottants (`if y_skate == 400 - skateH`) pour détecter le
sol — qui pouvait ne jamais être vraie et laisser Eduardo coincé.

Maintenant : gravité constante, vitesse initiale, et trois conforts d'usage
qu'on attend d'un jeu de saut moderne —

- **saut modulable** : relâcher tôt coupe l'élan, on fait des petits sauts ;
- **coyote time** (0,09 s) : on peut encore sauter juste après avoir quitté le sol ;
- **tampon d'entrée** (0,13 s) : un appui juste avant l'atterrissage est mémorisé
  et déclenche le saut dès le contact.

### 3. Les obstacles restent franchissables

Avant : un seul obstacle à la fois, réapparaissant toujours à la même distance
en pixels, avec `obstacle_vitesse += 0.05` à chaque passage. Comme l'écart était
fixe en pixels et la vitesse croissante, le temps pour réagir tendait vers zéro :
le jeu devenait mathématiquement impossible, pas difficile.

Maintenant l'écart est exprimé **en secondes de trajet** (1,10 à 1,95 s, plancher
à 1,00 s), donc toujours supérieur à la durée d'un saut (0,89 s). La vitesse
plafonne à 1250 px/s. Un bot qui joue parfaitement tient 5 minutes et dépasse
280 points — le jeu est dur, mais il reste gagnable.

Les paires d'obstacles collés n'apparaissent que si un seul saut suffit encore à
les franchir à la vitesse du moment ; le test est fait avant de les créer.

### 4. `gameOver()` ne s'appelle plus lui-même

Dans l'original, `principale()` appelait `gameOver()`, qui appelait `message()`,
qui rappelait `principale()`. Chaque partie empilait donc trois niveaux d'appels
de plus, sans jamais revenir : une longue session finissait en
`RecursionError`, et rien ne se libérait entre-temps.

Le jeu est maintenant une machine à états plate (`menu`, `play`, `pause`,
`dead`) : une seule boucle, aucune pile qui grandit.

### 5. La base de données n'est plus lue 60 fois par seconde

L'original faisait `cur.execute('select * from membres')` **à l'intérieur de la
boucle de jeu**, à chaque image, pour afficher le high score. Le record est
désormais chargé une fois au démarrage et écrit uniquement quand il tombe.

Et il n'est pas perdu : au premier lancement, la version Python lit l'ancienne
base `Données` et en importe le meilleur score (**182**). La version web reçoit
la même valeur, figée dans `config.js` par le script de préparation des assets.

## Collisions

L'ancien test empilait trois `if` avec des marges magiques (`+ 5`) sur les
rectangles complets des images. Comme les sprites étaient des carrés de 80×80
avec du fond bleu autour, on mourait souvent « à côté » de l'obstacle.

Les sprites sont maintenant détourés, et chaque type d'obstacle a sa propre
marge de tolérance (10 % pour le drapeau, 20 % pour les béquilles qui sont fines
et pleines de vide). La boîte du joueur est volontairement plus étroite que la
planche. Quand on passe à moins de 26 px, le jeu affiche **« CHAUD ! »**.

## Performances

- Les images sont chargées, **détourées, redimensionnées et converties une seule
  fois** au format de l'écran. L'original blittait des surfaces non converties
  (`pygame.image.load` sans `.convert()`), ce qui force une conversion de format
  à chaque affichage.
- Les rotations de la planche et de la tête sont quantifiées à 2° et mises en
  cache, au lieu d'appeler `transform.rotate` à chaque image.
- Le décor (ciel, ville, soleil) est pré-rendu dans des surfaces qu'on décale,
  pas redessiné pixel par pixel.
- Résultat, en rendu **100 % logiciel** (sans accélération) : 266 images/s en
  1280×720, 108 en 1920×1080, 59 en 2560×1440.

## Le décor : Mons

L'original avait un aplat bleu uni (`surface.fill(blue)`). Le jeu se déroule
maintenant dans une ville reconnaissable, dessinée en silhouettes vectorielles :

| Plan | Ce qu'on y voit |
|---|---|
| Lointain (défile à 12 %) | le **beffroi** et son bulbe, la **collégiale Sainte-Waudru** avec sa tour restée inachevée, l'**hôtel de ville** et son campanile, la **gare Calatrava** et sa coque blanche, des maisons de maître |
| Rapproché (défile à 34 %) | les maisons à pignons de la **Grand-Place** : pignons à redents, pignons pointus, pignons à volutes |

Les monuments sont décrits une seule fois, en primitives géométriques, dans
`python/crac/mons.py` ; `tools/prepare_assets.py` en génère `web/js/mons.js`.
Les deux versions utilisent le même générateur pseudo-aléatoire (`mulberry32`,
réimplémenté à l'identique en Python) : la ville est donc disposée exactement de
la même manière sur l'ordinateur et sur le téléphone.

Les hauteurs des maisons de remplissage varient de ±16 % pour casser la ligne
de toits, mais les quatre monuments gardent leurs proportions : un beffroi
étiré ne serait plus le beffroi.

## Ce qui est nouveau

- **Résolution libre** : fenêtre redimensionnable, plein écran, et adaptation au
  format de l'écran (le repère fait toujours 600 px de haut, la largeur suit).
  L'original était figé en 1100×600.
- **Décor** : ciel dégradé, soleil couchant, deux plans de Mons en parallaxe,
  route qui défile avec son marquage.
- **Effets** : poussière sous les roues, gerbe à l'atterrissage, débris et
  secousse de l'écran au crash, ombre portée qui rétrécit avec l'altitude.
- **S'accroupir** (`↓`) : le drapeau italien se met à voler à partir de 20 points
  et il faut passer dessous — ou le sauter très juste.
- **Écrans** : menu, pause (`P`), sourdine (`M`), écran de fin avec la photo
  d'Eduardo à l'hôpital.
- **Bruitages** : saut, atterrissage et point sont synthétisés à la volée
  (numpy côté Python, oscillateurs Web Audio côté navigateur) — aucun fichier
  supplémentaire à embarquer.
- **Version navigateur / mobile** installable sur iPhone et Android, jouable au
  doigt et hors-ligne.

## Les assets

`tools/prepare_assets.py` reconstruit les sprites à partir des **sources haute
résolution** qui dormaient dans le dossier d'origine, et non des vignettes 80×80
aplaties sur le fond bleu :

| Sprite | Source d'origine | Avant | Après |
|---|---|---|---|
| Skateboard | `http_%2F%2Fg-ecx.images-amazon…jpg` | 192×53 sur fond bleu | 480×101 détouré |
| Tête d'Eduardo | `Tete d Ed.png` | 100×110 sur fond bleu | 205×275 détouré |
| Béquilles | `Béquilles.jpg` (800×955) | 80×80 sur fond bleu | 95×260 détouré |
| Amaretto | `Bouteille_amareto.jpg` (325×677) | 80×80 sur fond bleu | 115×240 détouré |
| Altères | `Alteres.jpg` (300×300) | 80×80 sur fond bleu | 189×155 détouré |
| Bale | `Bale.jpg` (212×301) | 80×80 sur fond bleu | 149×220 détouré |
| Drapeau | `…drapeauxdespays.fr…it.png` (585×390) | 80×80 | 240×160 |

Le détourage part des pixels du bord et diffuse avec tolérance, ce qui évite de
percer des trous dans les zones claires du sujet (la chemise de Bale, les
altères gris clair sur fond blanc).

La route est rendue raccordable par fondu croisé de ses bords : elle défile sans
couture visible.

La police `BradBunR.ttf` contenait des tables `PCLT` et `hdmx` invalides
(`hdmx: Bad DeviceRecord padding 5`) que Chrome et Safari refusent — le jeu
retombait silencieusement sur Impact dans le navigateur. Le script la reconstruit
et produit un `.woff` propre.

## Divers

- **La musique ne survit plus à la fermeture de la fenêtre.** `pygame.quit()`
  ne suffit pas toujours à arrêter SDL_mixer sur macOS : le fil de lecture
  pouvait continuer après la disparition de la fenêtre. Le mixeur est
  maintenant arrêté explicitement, dans un `finally` — donc même en cas de
  plantage.

## Détails de code disparus au passage

- `def saut(y): y = y + 80` — la fonction réaffectait une variable locale et ne
  faisait donc rien ; elle n'était appelée nulle part.
- `def skate(x, y, image)` ignorait ses trois paramètres et affichait la variable
  globale `img_skate`.
- Les 90 lignes de paliers de difficulté (`if 3 <= score_actuel < 7: …`) étaient
  entièrement dans un bloc de commentaires : la seule progression réelle était
  `obstacle_vitesse += 0.05`.
- Le premier obstacle de chaque partie était toujours les frites (`m = 0`), le
  tirage n'ayant lieu qu'après le premier passage.
