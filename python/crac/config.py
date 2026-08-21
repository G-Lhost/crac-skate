"""Constantes de reglage de CRAC!

Tout le jeu raisonne dans un repere virtuel de VIEW_H pixels de haut ; la
largeur s'adapte au format de l'ecran (bornee) et le rendu est mis a l'echelle
une seule fois. C'est ce qui permet au meme code de tourner en 1100x600 sur un
PC et en 2532x1170 sur un iPhone sans rien deformer.
"""

# --- Repere virtuel -------------------------------------------------------
VIEW_H = 600
VIEW_W_MIN = 1000          # format 5:3
VIEW_W_MAX = 1500          # au-dela on ajoute des bandes noires
VIEW_W_DEFAULT = 1100      # la fenetre du jeu d'origine

GROUND_Y = 400             # ligne de sol : haut de la route (comme en 2016)
ROAD_H = VIEW_H - GROUND_Y

# --- Couleurs -------------------------------------------------------------
BLUE = (77, 84, 181)       # le bleu historique du jeu
SKY_TOP = (38, 42, 110)
SKY_BOT = (108, 118, 214)
WHITE = (255, 255, 255)
CREAM = (255, 244, 214)
AMBER = (255, 196, 64)
RED = (231, 76, 60)
GREEN = (0, 146, 71)
SHADOW = (28, 30, 62)

# --- Heros ----------------------------------------------------------------
PLAYER_X = 150             # abscisse fixe du skateur
BOARD_W = 192
BOARD_H = 53
HEAD_H = 110

# Hitbox : nettement plus permissive que les dimensions affichees, pour que
# les collisions soient lisibles a l'oeil (marge de pardon).
HITBOX_INSET_X = 46
HITBOX_INSET_Y = 16
DUCK_HEIGHT = 74           # hauteur de la hitbox accroupi

# --- Physique (px/s et px/s^2, independant du framerate) ------------------
GRAVITY = 2650.0
JUMP_VELOCITY = -1180.0
JUMP_CUT = 0.42            # relacher la touche coupe l'elan montant
FAST_FALL = 2.05           # multiplicateur de gravite en descente accroupi
COYOTE_TIME = 0.09         # saut tolere juste apres avoir quitte le sol
JUMP_BUFFER = 0.13         # saut memorise juste avant l'atterrissage
MAX_FALL = 2200.0

# --- Defilement -----------------------------------------------------------
SPEED_START = 560.0
SPEED_MAX = 1250.0
SPEED_GAIN = 7.0           # px/s gagnes par obstacle franchi
SPEED_RAMP = 8.0           # px/s gagnes par seconde de survie

# Ecart entre obstacles : exprime en secondes de trajet, donc toujours
# franchissable quelle que soit la vitesse (le defaut du jeu d'origine etait
# d'avoir un ecart fixe en pixels qui devenait injouable en accelerant).
# Le plancher doit rester superieur a la duree d'un saut (~0.89 s), sinon
# le second obstacle arrive avant qu'Eduardo ait pu se reposer sur ses roues.
GAP_MIN_S = 1.10
GAP_MAX_S = 1.95
GAP_TIGHTEN = 0.0026       # resserrement par obstacle franchi
GAP_FLOOR_S = 1.00

DOUBLE_CHANCE_FROM = 12    # score a partir duquel des paires apparaissent
FLYER_CHANCE_FROM = 20     # score a partir duquel le drapeau vole

# --- Divers ---------------------------------------------------------------
TARGET_FPS = 60
MAX_DT = 1 / 30            # borne le pas de temps (fenetre deplacee, lag...)
SHAKE_ON_CRASH = 18.0

TITLE = "CRAC !"
SUBTITLE = "Eduardo Skate Rush"
