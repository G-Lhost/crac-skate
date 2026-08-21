// CRAC ! - reglages du jeu.
// Ce fichier est le miroir exact de python/crac/config.py : toute valeur
// modifiee d'un cote doit l'etre de l'autre pour que les deux versions se
// jouent de la meme facon.

export const VIEW_H = 600;
export const VIEW_W_MIN = 1000;
export const VIEW_W_MAX = 1500;
export const VIEW_W_DEFAULT = 1100;

export const GROUND_Y = 400;
export const ROAD_H = VIEW_H - GROUND_Y;

export const BLUE = '#4d54b5';
export const SKY_TOP = '#262a6e';
export const SKY_BOT = '#6c76d6';
export const WHITE = '#ffffff';
export const CREAM = '#fff4d6';
export const AMBER = '#ffc440';
export const RED = '#e74c3c';

export const PLAYER_X = 150;
export const BOARD_W = 192;
export const BOARD_H = 53;
export const HEAD_H = 110;

export const HITBOX_INSET_X = 46;
export const HITBOX_INSET_Y = 16;
export const DUCK_HEIGHT = 74;

export const GRAVITY = 2650;
export const JUMP_VELOCITY = -1180;
export const JUMP_CUT = 0.42;
export const FAST_FALL = 2.05;
export const COYOTE_TIME = 0.09;
export const JUMP_BUFFER = 0.13;
export const MAX_FALL = 2200;

export const SPEED_START = 560;
export const SPEED_MAX = 1250;
export const SPEED_GAIN = 7.0;
export const SPEED_RAMP = 8.0;

export const GAP_MIN_S = 1.10;
export const GAP_MAX_S = 1.95;
export const GAP_TIGHTEN = 0.0026;
export const GAP_FLOOR_S = 1.00;

export const DOUBLE_CHANCE_FROM = 12;
export const FLYER_CHANCE_FROM = 20;

export const MAX_DT = 1 / 30;
export const SHAKE_ON_CRASH = 18;

export const TITLE = 'CRAC !';
export const SUBTITLE = 'Eduardo Skate Rush';

// Meilleur score de la version 2016, importe depuis la base SQLite d'origine
// par tools/prepare_assets.py.
export const LEGACY_BEST = 182;
