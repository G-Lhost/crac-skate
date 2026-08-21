"""Silhouettes de Mons pour le decor du jeu.

Chaque monument est decrit une seule fois, en primitives geometriques, dans un
repere local : x part du bord gauche du batiment, **y est une hauteur au-dessus
du sol** (donc vers le haut). Le moteur de rendu se charge de retourner l'axe.

Ce fichier est la source de verite : `tools/prepare_assets.py` en genere
`web/js/mons.js` a l'identique, pour que la version navigateur affiche
exactement la meme ville.

Primitives :
    ("rect", x, y, w, h, teinte)
    ("poly", [(x, y), ...], teinte)
    ("circle", cx, cy, r, teinte)

Teintes : "base" (maconnerie), "roof" (ardoise, plus sombre -- sans elle les
toitures se fondent dans les murs et la silhouette devient une masse), "light"
(elements clairs : la coque de la gare est blanche), "win" (ouvertures).
"""

# --------------------------------------------------------------------------
# Le beffroi -- seul beffroi baroque de Belgique, 87 m, et le seul monument de
# Mons inscrit isolement au patrimoine mondial. Tour carree, tourelles
# d'angle, et le bulbe qui lui a valu d'etre surnomme "le chateau d'eau" par
# Victor Hugo.
# --------------------------------------------------------------------------
BEFFROI = {
    "w": 64.0, "h": 246.0,
    "parts": [
        ("rect", 0, 0, 64, 10, "base"),         # socle
        ("rect", 5, 10, 54, 40, "base"),        # embase
        ("rect", 13, 50, 38, 100, "base"),      # fut
        ("rect", 19, 72, 8, 22, "win"),
        ("rect", 37, 72, 8, 22, "win"),
        ("rect", 19, 108, 8, 22, "win"),
        ("rect", 37, 108, 8, 22, "win"),
        ("rect", 8, 150, 48, 10, "base"),       # corniche
        ("rect", 3, 152, 11, 32, "base"),       # tourelle gauche
        ("poly", [(2, 184), (15, 184), (8.5, 200)], "base"),
        ("rect", 50, 152, 11, 32, "base"),      # tourelle droite
        ("poly", [(49, 184), (62, 184), (55.5, 200)], "base"),
        ("rect", 14, 160, 36, 36, "base"),      # chambre des cloches
        ("rect", 20, 167, 9, 21, "win"),
        ("rect", 35, 167, 9, 21, "win"),
        ("poly", [                              # le bulbe
            (14, 196), (10, 203), (12, 212), (18, 219), (25, 224),
            (32, 226), (39, 224), (46, 219), (52, 212), (54, 203),
            (50, 196),
        ], "base"),
        ("rect", 26, 226, 12, 10, "base"),      # lanterne
        ("poly", [(24, 236), (32, 244), (40, 236)], "base"),
        ("rect", 31.2, 242, 1.6, 4, "base"),    # fleche
    ],
}

# --------------------------------------------------------------------------
# La collegiale Sainte-Waudru -- gothique brabancon. Sa tour est restee
# inachevee : c'est ce moignon massif et plat, plus haut que la nef, qui la
# rend reconnaissable au premier coup d'oeil.
# --------------------------------------------------------------------------
WAUDRU = {
    "w": 144.0, "h": 194.0,
    "parts": [
        ("rect", 2, 0, 48, 162, "base"),        # tour inachevee
        ("rect", 0, 162, 52, 9, "base"),        # parapet
        ("rect", 0, 171, 9, 13, "base"),        # pinacles d'angle
        ("poly", [(-1, 184), (10, 184), (4.5, 194)], "base"),
        ("rect", 43, 171, 9, 13, "base"),
        ("poly", [(42, 184), (53, 184), (47.5, 194)], "base"),
        ("rect", 18, 0, 16, 28, "win"),         # portail
        ("rect", 13, 62, 26, 56, "win"),        # grande verriere
        ("rect", 12, 130, 9, 20, "win"),
        ("rect", 31, 130, 9, 20, "win"),
        ("rect", 50, 0, 80, 80, "base"),        # nef
        ("rect", 64, 30, 8, 44, "win"),         # lancettes
        ("rect", 82, 30, 8, 44, "win"),
        ("rect", 100, 30, 8, 44, "win"),
        ("rect", 46, 80, 88, 6, "base"),        # corniche debordante
        ("rect", 50, 86, 80, 30, "roof"),       # toiture d'ardoise
        ("rect", 48, 116, 84, 4, "roof"),       # faitiere
        # Les contreforts sont dessines APRES la toiture : leurs pinacles
        # doivent se detacher devant l'ardoise, comme sur le batiment reel.
        ("rect", 56, 0, 6, 96, "base"),
        ("poly", [(54, 96), (64, 96), (59, 116)], "base"),
        ("rect", 74, 0, 6, 96, "base"),
        ("poly", [(72, 96), (82, 96), (77, 116)], "base"),
        ("rect", 92, 0, 6, 96, "base"),
        ("poly", [(90, 96), (100, 96), (95, 116)], "base"),
        ("rect", 110, 0, 6, 96, "base"),
        ("poly", [(108, 96), (118, 96), (113, 116)], "base"),
        ("rect", 128, 0, 14, 78, "base"),       # chevet
        ("rect", 126, 78, 18, 5, "base"),
        ("poly", [(126, 83), (135, 100), (144, 83)], "roof"),
        ("rect", 132, 24, 8, 34, "win"),
    ],
}

# --------------------------------------------------------------------------
# L'hotel de ville gothique et son campanile, au fond de la Grand-Place.
# --------------------------------------------------------------------------
HOTEL_DE_VILLE = {
    "w": 112.0, "h": 146.0,
    "parts": [
        ("rect", 0, 0, 112, 74, "base"),
        ("rect", 0, 74, 112, 7, "base"),        # corniche
        ("rect", 4, 81, 104, 16, "roof"),       # toiture
        ("rect", 20, 84, 11, 11, "base"),       # lucarnes
        ("rect", 81, 84, 11, 11, "base"),
        ("rect", 10, 6, 12, 22, "win"),         # arcades du rez-de-chaussee
        ("rect", 30, 6, 12, 22, "win"),
        ("rect", 50, 6, 12, 22, "win"),
        ("rect", 70, 6, 12, 22, "win"),
        ("rect", 90, 6, 12, 22, "win"),
        ("rect", 14, 40, 10, 24, "win"),        # fenetres a meneaux
        ("rect", 34, 40, 10, 24, "win"),
        ("rect", 68, 40, 10, 24, "win"),
        ("rect", 88, 40, 10, 24, "win"),
        ("rect", 48, 97, 16, 24, "base"),       # campanile
        ("poly", [
            (46, 121), (44, 126), (47, 132), (51, 136),
            (56, 138), (61, 136), (65, 132), (68, 126), (66, 121),
        ], "base"),
        ("rect", 51, 138, 10, 5, "base"),
        ("rect", 55.2, 143, 1.6, 3, "base"),
    ],
}

# --------------------------------------------------------------------------
# La gare de Mons signee Santiago Calatrava : une coque blanche en arc posee
# au-dessus des voies. C'est le seul element clair du decor -- et il depasse
# tout juste les toits de la Grand-Place.
# --------------------------------------------------------------------------
GARE = {
    "w": 186.0, "h": 104.0,
    "parts": [
        ("rect", 0, 0, 186, 14, "base"),        # quai
        ("rect", 20, 14, 146, 34, "win"),       # facade vitree
        ("rect", 38, 14, 4, 66, "light"),       # bequilles
        ("rect", 84, 14, 4, 82, "light"),
        ("rect", 130, 14, 4, 72, "light"),
        ("poly", [                              # la coque
            (4, 12), (12, 40), (28, 66), (50, 86), (78, 98), (108, 100),
            (140, 88), (168, 62), (182, 30), (184, 12),
            (172, 12), (166, 36), (144, 64), (114, 84), (86, 90),
            (58, 82), (34, 60), (20, 34), (16, 12),
        ], "light"),
    ],
}

# --------------------------------------------------------------------------
# Maisons a pignons de la Grand-Place et des rues alentour.
# --------------------------------------------------------------------------
MAISON_ESCALIER = {   # pignon a redents
    "w": 36.0, "h": 76.0,
    "parts": [
        ("rect", 0, 0, 36, 50, "base"),
        ("poly", [
            (0, 50), (0, 56), (6, 56), (6, 61), (12, 61), (12, 66),
            (18, 72), (24, 66), (24, 61), (30, 61), (30, 56), (36, 56),
            (36, 50),
        ], "base"),
        ("rect", 6, 9, 9, 13, "win"),
        ("rect", 21, 9, 9, 13, "win"),
        ("rect", 6, 29, 9, 13, "win"),
        ("rect", 21, 29, 9, 13, "win"),
    ],
}

MAISON_POINTUE = {
    "w": 30.0, "h": 68.0,
    "parts": [
        ("rect", 0, 0, 30, 46, "base"),
        ("poly", [(0, 46), (15, 68), (30, 46)], "roof"),
        ("rect", 5, 10, 8, 14, "win"),
        ("rect", 17, 10, 8, 14, "win"),
        ("rect", 11, 31, 8, 11, "win"),
    ],
}

MAISON_CLOCHE = {     # pignon a volutes, tres present sur la Grand-Place
    "w": 42.0, "h": 88.0,
    "parts": [
        ("rect", 0, 0, 42, 58, "base"),
        ("poly", [
            (0, 58), (2, 66), (9, 70), (12, 76), (17, 82),
            (21, 86), (25, 82), (30, 76), (33, 70), (40, 66), (42, 58),
        ], "base"),
        ("rect", 6, 10, 10, 16, "win"),
        ("rect", 26, 10, 10, 16, "win"),
        ("rect", 6, 34, 10, 16, "win"),
        ("rect", 26, 34, 10, 16, "win"),
    ],
}

HOTEL_MAITRE = {      # remplissage du plan lointain : maison de maitre
    "w": 56.0, "h": 128.0,
    "parts": [
        ("rect", 0, 0, 56, 100, "base"),
        ("rect", -2, 100, 60, 7, "base"),       # corniche debordante
        ("poly", [(0, 107), (6, 122), (50, 122), (56, 107)], "roof"),  # mansarde
        ("rect", 24, 122, 8, 6, "base"),        # souche de cheminee
        ("rect", 8, 14, 11, 16, "win"),
        ("rect", 37, 14, 11, 16, "win"),
        ("rect", 8, 42, 11, 16, "win"),
        ("rect", 22, 42, 11, 16, "win"),
        ("rect", 37, 42, 11, 16, "win"),
        ("rect", 8, 70, 11, 16, "win"),
        ("rect", 37, 70, 11, 16, "win"),
        ("rect", 24, 110, 9, 9, "win"),
    ],
}

BEGUINAGE = {         # variante de remplissage, plus large et plus basse
    "w": 74.0, "h": 112.0,
    "parts": [
        ("rect", 0, 0, 74, 86, "base"),
        ("rect", -2, 86, 78, 6, "base"),
        ("poly", [(2, 92), (10, 108), (64, 108), (72, 92)], "roof"),
        ("rect", 14, 108, 7, 4, "base"),
        ("rect", 54, 108, 7, 4, "base"),
        ("rect", 9, 12, 10, 15, "win"),
        ("rect", 32, 12, 10, 15, "win"),
        ("rect", 55, 12, 10, 15, "win"),
        ("rect", 9, 38, 10, 15, "win"),
        ("rect", 32, 38, 10, 15, "win"),
        ("rect", 55, 38, 10, 15, "win"),
        ("rect", 20, 64, 10, 15, "win"),
        ("rect", 44, 64, 10, 15, "win"),
    ],
}

BUILDINGS = {
    "beffroi": BEFFROI,
    "waudru": WAUDRU,
    "hotel_de_ville": HOTEL_DE_VILLE,
    "gare": GARE,
    "maison_escalier": MAISON_ESCALIER,
    "maison_pointue": MAISON_POINTUE,
    "maison_cloche": MAISON_CLOCHE,
    "hotel_maitre": HOTEL_MAITRE,
    "beguinage": BEGUINAGE,
}

# Plan lointain : uniquement ce qui depasse la ligne des toits, sinon on ne
# verrait rien derriere le plan rapproche.
FAR_SEQUENCE = [
    "hotel_maitre", "beffroi", "beguinage", "hotel_maitre", "waudru",
    "beguinage", "gare", "hotel_maitre", "hotel_de_ville", "beguinage",
]

# Plan rapproche : la Grand-Place et ses maisons a pignons.
NEAR_SEQUENCE = [
    "maison_escalier", "maison_pointue", "maison_cloche", "maison_escalier",
    "maison_pointue", "maison_cloche", "maison_pointue", "maison_escalier",
]

# Palettes (base, light, win) par plan.
FAR_PALETTE = {"base": (54, 60, 132), "roof": (41, 46, 106),
               "light": (172, 180, 228), "win": (94, 99, 162)}
NEAR_PALETTE = {"base": (32, 36, 88), "roof": (23, 26, 68),
                "light": (104, 110, 164), "win": (74, 77, 118)}

FAR_GAP = (16.0, 46.0)
NEAR_GAP = (4.0, 26.0)

# Monuments : hauteur figee. Un beffroi etire de 12 % ne serait plus le
# beffroi. Les maisons de remplissage, elles, varient pour casser la
# monotonie de la ligne de toits.
MONUMENTS = frozenset({"beffroi", "waudru", "hotel_de_ville", "gare"})
FILLER_JITTER = (0.84, 1.16)


def _i32(v: int) -> int:
    v &= 0xFFFFFFFF
    return v - 0x100000000 if v & 0x80000000 else v


def _imul(a: int, b: int) -> int:
    """Equivalent de Math.imul : multiplication entiere 32 bits signee."""
    return _i32((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF))


def mulberry32(seed: int):
    """Le generateur pseudo-aleatoire de la version JavaScript, en Python.

    On ne peut pas se contenter de random.Random : pour que la ville soit
    *exactement* la meme dans les deux versions du jeu, il faut que les deux
    tirent la meme suite de nombres. mulberry32 tient en cinq lignes et se
    reimplemente a l'identique des deux cotes.
    """
    state = _i32(seed)

    def rnd() -> float:
        nonlocal state
        state = _i32(state + 0x6D2B79F5)
        t = _imul(state ^ ((state & 0xFFFFFFFF) >> 15), 1 | state)
        t = _i32(_i32(t + _imul(t ^ ((t & 0xFFFFFFFF) >> 7), 61 | t)) ^ t)
        return ((t ^ ((t & 0xFFFFFFFF) >> 14)) & 0xFFFFFFFF) / 4294967296.0

    return rnd


def layout(sequence, total_w, gap_range, rng):
    """Repartit la sequence sur `total_w` sans jamais couper un batiment.

    On empile les batiments tant qu'ils tiennent, puis on redistribue l'espace
    restant dans les intervalles : la bande peut ainsi etre repetee bord a bord
    sans raccord visible.

    `rng` est une fonction sans argument renvoyant un flottant dans [0, 1[
    -- voir mulberry32, partagee avec la version JavaScript.

    Renvoie une liste de (nom, x, facteur de hauteur).
    """
    chosen = []
    used = 0.0
    i = 0
    while True:
        name = sequence[i % len(sequence)]
        w = BUILDINGS[name]["w"]
        gap = gap_range[0] + rng() * (gap_range[1] - gap_range[0])
        if used + w + gap > total_w:
            break
        vscale = (1.0 if name in MONUMENTS
                  else FILLER_JITTER[0]
                  + rng() * (FILLER_JITTER[1] - FILLER_JITTER[0]))
        chosen.append((name, gap, vscale))
        used += w + gap
        i += 1
    if not chosen:
        return []
    extra = (total_w - used) / len(chosen)
    placed = []
    x = 0.0
    for name, gap, vscale in chosen:
        placed.append((name, x, vscale))
        x += BUILDINGS[name]["w"] + gap + extra
    return placed
