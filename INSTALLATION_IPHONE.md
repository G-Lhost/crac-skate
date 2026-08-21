# Mettre CRAC ! sur l'iPhone 13 Pro

Trois chemins possibles, du plus rapide au plus « vraie application ».
**Le chemin A suffit dans 90 % des cas** : le jeu s'installe avec son icône sur
l'écran d'accueil, s'ouvre en plein écran sans barre Safari, et fonctionne sans
réseau. Aucun compte développeur, aucun Xcode.

| | Chemin A — PWA hébergée | Chemin B — PWA en Wi-Fi local | Chemin C — App native |
|---|---|---|---|
| À installer sur le Mac | rien | rien | Xcode + Node |
| Temps | ~10 min | ~3 min | ~1 h (dont téléchargements) |
| Fonctionne sans le Mac allumé | oui | non | oui |
| Fonctionne hors-ligne | oui | non | oui |
| Durée de validité | illimitée | illimitée | 7 jours (compte gratuit) |

---

## Chemin A — Publier sur GitHub, puis ajouter à l'écran d'accueil

Pour qu'iOS installe le jeu comme une vraie application capable de tourner
hors-ligne, il faut qu'il soit servi en **HTTPS**. GitHub Pages le fait
gratuitement, en une poignée de commandes. Comptez dix minutes la première
fois, puis une seule commande pour chaque mise à jour.

Toutes les commandes se tapent dans **Terminal** (Applications → Utilitaires →
Terminal), depuis le dossier du jeu. Placez-vous-y une fois pour toutes :

```bash
cd "/Users/guillaumelhost/Library/CloudStorage/OneDrive-UMONS/Drive travaux extras/Jeux_videos/Eduardo_fait_du_skate/CRAC_Eduardo_Skate_Rush"
```

---

### Étape 1 — Avoir un compte GitHub

Si vous n'en avez pas : <https://github.com/signup>. Notez bien votre **nom
d'utilisateur**, il apparaîtra dans l'adresse du jeu.

---

### Étape 2 — Dire à git qui vous êtes

À faire une seule fois par machine. Si c'est déjà configuré, ces commandes ne
font que réécrire la même chose.

```bash
git config --global user.name "Guillaume Lhost" && git config --global user.email "guillaume.lhost22@gmail.com"
```

---

### Étape 3 — Transformer le dossier du jeu en dépôt

```bash
git init -b main && git add . && git commit -m "CRAC ! - Eduardo Skate Rush"
```

Vous devez voir défiler une soixantaine de fichiers et une ligne du genre
`[main (root-commit) a1b2c3d] CRAC ! - Eduardo Skate Rush`.

> Seul le dossier `CRAC_Eduardo_Skate_Rush` devient un dépôt. Le jeu de 2016,
> qui est dans le dossier parent, n'est pas embarqué et n'est pas modifié.

---

### Étape 4 — Créer le dépôt vide sur GitHub

Allez sur <https://github.com/new> et remplissez :

| Champ | Valeur |
|---|---|
| **Repository name** | `crac-skate` |
| **Public / Private** | **Public** — obligatoire : GitHub Pages n'est pas gratuit sur un dépôt privé |
| Add a README file | **décoché** |
| Add .gitignore | **None** |
| Choose a license | **None** |

Cliquez sur **Create repository**. GitHub affiche alors une page « …or push an
existing repository from the command line » : c'est exactement ce qu'on va
faire.

---

### Étape 5 — Relier votre dossier au dépôt et l'envoyer

Remplacez `VOTRE-PSEUDO` par votre nom d'utilisateur GitHub :

```bash
git remote add origin https://github.com/VOTRE-PSEUDO/crac-skate.git && git push -u origin main
```

**Git va vous demander de vous identifier.** Attention : depuis 2021, GitHub
n'accepte plus le mot de passe du compte en ligne de commande. Deux solutions :

- **Le plus simple — GitHub Desktop.** Installez <https://desktop.github.com>,
  connectez-vous une fois dans l'application, et fermez-la. Elle installe un
  assistant d'identification que git réutilisera automatiquement ; relancez
  alors la commande ci-dessus, elle passera sans rien demander.

- **Sinon — un jeton d'accès.** Sur GitHub : cliquez sur votre photo en haut à
  droite → **Settings** → tout en bas à gauche **Developer settings** →
  **Personal access tokens** → **Tokens (classic)** → **Generate new token
  (classic)**. Donnez-lui un nom (`mac`), une expiration, et cochez la case
  **repo**. Validez, puis **copiez le jeton affiché** (il ne sera plus jamais
  montré). Quand git demande `Username`, tapez votre pseudo ; quand il demande
  `Password`, **collez le jeton**. macOS le retiendra dans le trousseau.

Quand ça a marché, rafraîchissez la page de votre dépôt : vos fichiers y sont.

---

### Étape 6 — Publier la version web

```bash
./tools/publier.sh
```

Ce script fait tout le travail : il recopie `web/` dans un dossier `docs/`
(le seul sous-dossier que GitHub Pages sache servir), donne un nouveau numéro
de version au cache hors-ligne, enregistre et envoie sur GitHub. Il se termine
en vous affichant l'adresse de votre jeu.

---

### Étape 7 — Activer GitHub Pages

Une seule fois, sur le site :

1. Ouvrez votre dépôt → onglet **Settings** (tout à droite, avec l'engrenage).
2. Menu de gauche → **Pages**.
3. **Source** : `Deploy from a branch`.
4. **Branch** : `main`, et juste à côté, le dossier : **`/docs`**.
5. **Save**.

Rechargez la page au bout d'une à deux minutes : un bandeau vert affiche
*« Your site is live at… »* avec l'adresse :

```
https://VOTRE-PSEUDO.github.io/crac-skate/
```

> Si la page reste blanche ou renvoie une erreur 404, c'est presque toujours
> que le dossier `/docs` n'a pas été sélectionné à l'étape 4, ou que la
> première publication n'est pas terminée. L'onglet **Actions** du dépôt montre
> l'avancement.

Ouvrez l'adresse sur l'ordinateur pour vérifier que le jeu se lance.

---

### Étape 8 — Installer sur l'iPhone 13 Pro

1. Sur l'iPhone, ouvrez **Safari** — et vraiment Safari : sur iOS, Chrome et
   Firefox ne savent pas installer une application sur l'écran d'accueil.
2. Tapez l'adresse `https://VOTRE-PSEUDO.github.io/crac-skate/`.
   (Pour éviter de la retaper : envoyez-la-vous par message ou par mail depuis
   le Mac.)
3. Laissez la page finir de charger — la barre de progression jaune sous le
   titre « CRAC ! » doit aller au bout.
4. Touchez le bouton **Partager** (le carré avec une flèche vers le haut, en
   bas au centre de l'écran).
5. Faites défiler la liste vers le bas → **« Sur l'écran d'accueil »**.
6. Le nom proposé est déjà « CRAC ! ». Touchez **Ajouter** en haut à droite.
7. L'icône (la tête d'Eduardo sur fond bleu) apparaît sur l'écran d'accueil.

Lancez-la : le jeu s'ouvre en plein écran, sans barre d'adresse. Tournez le
téléphone en paysage, touchez l'écran une fois — la musique démarre et Eduardo
part.

---

### Étape 9 — Vérifier que ça marche sans réseau

1. Jouez une partie complète (le jeu met alors ses 3,6 Mo en cache).
2. Fermez l'application.
3. Activez le **mode Avion**.
4. Relancez l'icône : le jeu doit démarrer normalement.

Si c'est le cas, l'installation est terminée : le jeu ne dépend plus ni de
votre Mac ni d'internet.

---

### Plus tard : mettre à jour le jeu

Après avoir modifié quoi que ce soit dans le projet :

```bash
./tools/publier.sh "ce que j'ai changé"
```

Attendez une minute, puis relancez l'application sur l'iPhone **avec le réseau
activé** : elle récupère la nouvelle version toute seule. Un second lancement
peut être nécessaire pour que tous les fichiers soient rafraîchis.

## Chemin B — Depuis le Mac, en Wi-Fi local (le plus rapide pour essayer)

Utile pour tester une modification tout de suite. Le Mac et l'iPhone doivent
être sur le **même réseau Wi-Fi**.

Sur le Mac :

```bash
cd "/Users/guillaumelhost/Library/CloudStorage/OneDrive-UMONS/Drive travaux extras/Jeux_videos/Eduardo_fait_du_skate/CRAC_Eduardo_Skate_Rush" && python3 -m http.server 8123 --directory web
```

Récupérez l'adresse IP du Mac :

```bash
ipconfig getifaddr en0 || ipconfig getifaddr en1
```

Sur l'iPhone, ouvrez dans Safari `http://ADRESSE-IP:8123` (par exemple
`http://192.168.1.24:8123`).

Vous pouvez aussi l'ajouter à l'écran d'accueil, mais comme la connexion est en
`http://` et non `https://`, iOS n'autorise pas la mise en cache hors-ligne :
le jeu ne marchera que si le Mac tourne. Pour un usage quotidien, préférez le
chemin A.

---

## Chemin C — Une vraie application native (fichier `.app` signé)

À faire si vous voulez l'icône « installée » comme une app de l'App Store,
sans passer par Safari. On empaquette la version web dans une coquille native
avec **Capacitor**.

### 1. Prérequis sur le Mac

```bash
brew install node cocoapods
```

Installez **Xcode** depuis le Mac App Store (~10 Go, comptez un moment), puis
lancez-le une fois pour accepter la licence, et pointez la ligne de commande
dessus :

```bash
sudo xcode-select -s /Applications/Xcode.app/Contents/Developer && sudo xcodebuild -license accept
```

> Votre Mac est en macOS 26.6 : prenez Xcode 26, seul capable de cibler
> l'iOS le plus récent installé sur l'iPhone 13 Pro.

### 2. Générer le projet iOS

```bash
cd "/Users/guillaumelhost/Library/CloudStorage/OneDrive-UMONS/Drive travaux extras/Jeux_videos/Eduardo_fait_du_skate/CRAC_Eduardo_Skate_Rush" && npm install && npx cap add ios && npx cap sync ios
```

Un dossier `ios/` apparaît. Pour forcer le mode paysage et le plein écran,
ouvrez `ios/App/App/Info.plist` et remplacez le bloc
`UISupportedInterfaceOrientations` par :

```xml
<key>UISupportedInterfaceOrientations</key>
<array>
  <string>UIInterfaceOrientationLandscapeLeft</string>
  <string>UIInterfaceOrientationLandscapeRight</string>
</array>
<key>UIRequiresFullScreen</key>
<true/>
<key>UIStatusBarHidden</key>
<true/>
<key>UIViewControllerBasedStatusBarAppearance</key>
<false/>
```

### 3. Compiler et envoyer sur l'iPhone

```bash
npx cap open ios
```

Dans Xcode :

1. Panneau de gauche : sélectionnez le projet **App**, puis la cible **App**.
2. Onglet **Signing & Capabilities** :
   - cochez **Automatically manage signing** ;
   - **Team** : ajoutez votre identifiant Apple (`Add an Account…`) — un compte
     Apple gratuit suffit ;
   - **Bundle Identifier** : remplacez `com.eduardo.cracskaterush` par quelque
     chose d'unique, par exemple `com.guillaume.cracskate`. Deux personnes ne
     peuvent pas signer le même identifiant.
3. Branchez l'iPhone 13 Pro en USB, déverrouillez-le, répondez **Se fier** à la
   question « Se fier à cet ordinateur ? ».
4. En haut de la fenêtre Xcode, choisissez votre iPhone comme destination
   (à la place de « Any iOS Device » ou d'un simulateur).
5. **⌘R**. La première compilation prend quelques minutes.

Au premier lancement, l'iPhone refusera d'ouvrir l'app. Sur le téléphone :
**Réglages → Général → VPN et gestion de l'appareil → Apps de développeur →**
votre identifiant Apple **→ Se fier**. Relancez l'app.

> **Compte Apple gratuit : l'app expire au bout de 7 jours.** Rebranchez
> l'iPhone et refaites ⌘R pour repartir pour 7 jours. Avec un compte Apple
> Developer payant (99 €/an), la signature est valable un an.

### 4. Après chaque modification du jeu

```bash
npx cap sync ios
```

puis ⌘R dans Xcode. `cap sync` recopie le dossier `web/` dans le projet natif.

---

## Et sur Android ?

Même principe, en plus simple : pas de compte développeur du tout.

```bash
brew install --cask android-studio && npx cap add android && npx cap sync android && npx cap open android
```

Dans Android Studio, branchez le téléphone (avec le **débogage USB** activé
dans les options pour développeurs) et cliquez sur ▶.

Pour produire un fichier `.apk` à installer à la main :

```bash
cd android && ./gradlew assembleDebug
```

Le fichier atterrit dans `android/app/build/outputs/apk/debug/app-debug.apk`.
Transférez-le sur le téléphone, ouvrez-le, et autorisez l'installation depuis
cette source.

---

## Bon à savoir sur iPhone

- **Le jeu se joue en paysage.** En portrait, il affiche « Tournez votre
  téléphone » et met la partie en pause. Si rien ne bascule, vérifiez que le
  **verrouillage de la rotation** est désactivé (centre de contrôle, l'icône
  cadenas avec la flèche circulaire).
- **Le son a besoin d'une première touche.** iOS interdit à une page de jouer du
  son sans interaction : la musique démarre au premier appui sur l'écran.
- **Le bouton silencieux coupe le son du jeu.** C'est une règle du système pour
  tout ce qui est web, y compris installé sur l'écran d'accueil. Le chemin C
  (app native) n'a pas cette limite.
- **Commandes tactiles** : toucher n'importe où = sauter ; garder le doigt appuyé
  = sauter plus haut ; toucher et maintenir dans le tiers bas de l'écran =
  s'accroupir sous le drapeau. On peut garder un doigt en bas et taper de
  l'autre.
- **L'encoche est gérée** : la zone de jeu s'arrête avant le capteur et avant la
  barre d'accueil, quelle que soit l'orientation.
- **Le record est stocké sur l'appareil.** Il démarre à 182 — le record de la
  version de 2016, récupéré dans l'ancienne base `Données`. Sur le Mac, la
  version Python lit directement cette base au premier lancement.
