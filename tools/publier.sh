#!/usr/bin/env bash
#
# Publie la version web du jeu sur GitHub Pages.
#
# GitHub Pages ne sait servir qu'un site place a la racine du depot ou dans un
# dossier nomme "docs". Le dossier de travail restant "web/", ce script en
# recopie le contenu dans "docs/", puis pousse le tout.
#
#   ./tools/publier.sh                 sync + commit + push
#   ./tools/publier.sh "mon message"   idem avec un message de commit choisi
#
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d web ]; then
  echo "Erreur : dossier web/ introuvable. Lancez le script depuis le projet." >&2
  exit 1
fi

if [ ! -d .git ]; then
  echo "Erreur : ce dossier n'est pas encore un depot git." >&2
  echo "Faites d'abord :  git init -b main && git add . && git commit -m 'depart'" >&2
  exit 1
fi

# Les assets sont deja dans le depot : on ne les regenere que si le jeu de
# 2016 se trouve encore a cote (ce n'est pas le cas sur une machine ou l'on
# vient simplement de cloner le depot).
echo "1/4  Assets partages…"
if [ -f ../Ed_Skate.py ]; then
  python3 tools/prepare_assets.py >/dev/null
  echo "     regeneres depuis le jeu de 2016"
else
  echo "     sources de 2016 absentes : on garde les assets du depot"
fi

# Nouveau nom de cache a chaque publication : sans cela, les iPhone qui ont
# deja installe le jeu continueraient a servir l'ancienne version depuis leur
# cache hors-ligne, indefiniment.
stamp="$(date -u +%Y%m%d%H%M%S)"
python3 - "$stamp" <<'PYEOF'
import pathlib, re, sys
p = pathlib.Path("web/sw.js")
p.write_text(re.sub(r"^const CACHE = '.*';$",
                    f"const CACHE = 'crac-{sys.argv[1]}';",
                    p.read_text(), count=1, flags=re.M), "utf-8")
PYEOF
echo "     version du cache hors-ligne : crac-$stamp"

echo "2/4  Copie de web/ vers docs/…"
mkdir -p docs
rsync -a --delete --exclude '.nojekyll' web/ docs/
# Sans ce fichier, GitHub Pages fait passer le site par Jekyll, qui ignore
# certains fichiers et ralentit chaque publication.
touch docs/.nojekyll

echo "3/4  Enregistrement dans git…"
git add -A
if git diff --cached --quiet; then
  echo "     (rien de neuf a publier)"
else
  git commit -m "${1:-Mise a jour de CRAC !}"
fi

echo "4/4  Envoi vers GitHub…"
branch="$(git rev-parse --abbrev-ref HEAD)"
git push -u origin "$branch"

# Reconstitue l'adresse GitHub Pages a partir de l'URL du depot, en n'utilisant
# que des expansions du shell (le sed de macOS ne gere pas les quantificateurs
# non gourmands).
url="$(git remote get-url origin 2>/dev/null || true)"
echo
if [ -n "$url" ]; then
  clean="${url%.git}"
  repo="${clean##*/}"
  rest="${clean%/*}"
  user="${rest##*[:/]}"
  echo "Termine. Dans une a deux minutes, le jeu sera sur :"
  echo "    https://${user}.github.io/${repo}/"
else
  echo "Termine."
fi
