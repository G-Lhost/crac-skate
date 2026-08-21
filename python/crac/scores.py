"""Persistance du meilleur score.

Le jeu de 2016 stockait les scores dans une base SQLite nommee "Donnees" et
relisait la table **a chaque image** de la boucle de jeu. Ici on garde un
simple JSON charge une fois, ecrit uniquement quand le record tombe -- et on
importe automatiquement l'ancien palmares au premier lancement.
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # .../python
LEGACY_DB = ROOT.parent.parent / "Données"      # la base du jeu d'origine


def _data_dir() -> Path:
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home()))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share"))
    d = base / "CRAC-Eduardo-Skate-Rush"
    d.mkdir(parents=True, exist_ok=True)
    return d


class Scores:
    def __init__(self) -> None:
        self.path = _data_dir() / "scores.json"
        self.best = 0
        self.runs = 0
        self.legacy_best = 0
        self._load()

    def _load(self) -> None:
        data = {}
        if self.path.exists():
            try:
                data = json.loads(self.path.read_text("utf-8"))
            except (json.JSONDecodeError, OSError):
                data = {}
        self.best = int(data.get("best", 0))
        self.runs = int(data.get("runs", 0))
        self.legacy_best = int(data.get("legacy_best", 0))

        if not data.get("migrated"):
            legacy = self._read_legacy()
            if legacy:
                self.legacy_best = legacy
                self.best = max(self.best, legacy)
            self._save(migrated=True)

    @staticmethod
    def _read_legacy() -> int:
        """Recupere le record de la base SQLite du jeu d'origine."""
        if not LEGACY_DB.exists():
            return 0
        try:
            with sqlite3.connect(f"file:{LEGACY_DB}?mode=ro", uri=True) as conn:
                row = conn.execute("select max(score) from membres").fetchone()
            return int(row[0]) if row and row[0] is not None else 0
        except (sqlite3.Error, ValueError, TypeError):
            return 0

    def _save(self, migrated: bool = True) -> None:
        try:
            self.path.write_text(json.dumps({
                "best": self.best,
                "runs": self.runs,
                "legacy_best": self.legacy_best,
                "migrated": migrated,
            }, indent=2), "utf-8")
        except OSError:
            pass  # un disque en lecture seule ne doit pas casser la partie

    def submit(self, score: int) -> bool:
        """Enregistre une partie ; renvoie True si c'est un nouveau record."""
        self.runs += 1
        record = score > self.best
        if record:
            self.best = score
        self._save()
        return record
