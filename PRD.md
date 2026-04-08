# PRD — Ant Colony (Terminal Idle Game)

> Version 0.1 — 2026-04-08

---

## 1. Vision

Un jeu idle qui tourne dans un terminal pendant qu'on travaille.
Une fourmilière qui vit, grandit et évolue toute seule — on intervient de temps en temps pour orienter sa croissance.
L'ambiance est contemplative : observer une colonie prospérer est satisfaisant sans être distrayant.

---

## 2. Principes de design

| Principe | Détail |
|----------|--------|
| **Idle first** | Le jeu avance sans le joueur. Aucune action urgente. |
| **Offline gains** | La colonie continue à vivre entre deux sessions. |
| **Interaction légère** | 2–3 touches suffisent. Jamais plus de 30s d'attention. |
| **Zéro stress** | Pas de défaite, pas de timer fatal, pas de punition. |
| **Lisible d'un coup d'œil** | L'état global visible en < 2 secondes. |

---

## 3. Concept de jeu

### 3.1 Boucle principale

```
Reine pond → Œufs éclosent → Fourmis travaillent → Ressources collectées
     ↑                                                        ↓
Upgrades achetés ←────────────── Ressources dépensées ←──────┘
```

### 3.2 Ressources

| Ressource | Source | Usage |
|-----------|--------|-------|
| **Nourriture** | Fourrageuses | Nourrir la colonie, pondre |
| **Matériaux** | Ouvrières | Creuser, construire |
| **Population** | Éclosions | Permet d'assigner des rôles |

### 3.3 Castes de fourmis

| Caste | Rôle | Déblocage |
|-------|------|-----------|
| **Ouvrière** | Creuse les tunnels, construit | Départ |
| **Fourrageuse** | Collecte nourriture | Départ |
| **Soldate** | Défend contre événements | Tunnel 3 |
| **Champignonniste** | Cultive champignons (bonus nourriture) | Upgrade |
| **Reine secondaire** | Accélère ponte | Fin de jeu |

Le joueur **répartit** sa population entre castes selon ses priorités.

---

## 4. Progression

### 4.1 Phases de jeu

**Phase 1 — Naissance** (0–$500 de ressources)
- 1 reine, 5 fourmis, 2 tunnels
- Apprendre la boucle de base
- Cultures : radis et carottes (rapides)

**Phase 2 — Expansion** ($500–$10k)
- Débloquer soldates, champignonnistes
- Nouvelles salles : nurserie, garde-manger, champignonnière
- Événements aléatoires commencent

**Phase 3 — Colonie établie** ($10k–$100k)
- Reine secondaire
- Espèces exotiques de fourmis
- Mécaniques de commerce inter-colonies

**Phase 4 — Légendaire** ($100k+)
- Fourmis légionnaires (raids)
- Symbiose avec plantes
- Objectifs de fin de jeu

### 4.2 Arbre d'upgrades

```
Gros ventre de reine (+ponte)
├── Nurserie renforcée (+éclosions)
│   └── Crèche royale (reine secondaire)
├── Garde-manger (stockage ×2)
│   └── Fermentation (nourriture dure plus longtemps)
Pattes renforcées (+vitesse fourrageuse)
├── Phéromones optimisées (+efficacité chemin)
│   └── Carte de territoire (zone de collecte élargie)
Mandibules acérées (+vitesse creusage)
├── Chambre de stockage matériaux
│   └── Architecture avancée (salles spéciales)
Champignonnière (prod nourriture passive)
└── Symbiose fongique (bonus multiplicateur)
```

---

## 5. Événements aléatoires

Surviennent toutes les 30–90 min de temps réel (configurable).
Notification discrète dans l'UI, jamais bloquante.

| Événement | Effet | Réponse joueur |
|-----------|-------|----------------|
| Pluie | +nourriture, tunnels ralentis | Aucune |
| Araignée | Perd des fourrageuses | Envoyer soldates |
| Fourmilière voisine | Négocie ou combat | Choix diplomatique |
| Essaimage | Bonus pop temporaire | Aucune |
| Sécheresse | -nourriture ×0.5 | Activer garde-manger |
| Champignon toxique | Zone inaccessible temporaire | Aucune |

---

## 6. Interface (TUI)

### Layout principal

```
┌─────────────────────────────────────────────────────────────┐
│  ANT COLONY              🐜 247 fourmis    Jour 12  10:34  │
├─────────────────┬───────────────────────────────────────────┤
│  FOURMILIÈRE    │  RESSOURCES                               │
│                 │  🍖 Nourriture  ████████░░  824 / 1000   │
│  ████░░░░░░░░   │  🪨 Matériaux   ████░░░░░░  412 / 800    │
│  ██F░W░░░S░░░   │                                           │
│  ░░░░░░░░░░░░   │  POPULATION                               │
│  ░░[Nurserie]░  │  Ouvrières    ██████░░░░  60  [+] [-]   │
│  ░░░░░░░░░░░░   │  Fourrageuses ████████░░  80  [+] [-]   │
│  ░[Garde-manger]│  Soldates     ██░░░░░░░░  20  [+] [-]   │
│  ░░░░░░░░░░░░   │  Champign.    ████░░░░░░  40  [+] [-]   │
│                 │  Inactives               47              │
├─────────────────┴───────────────────────────────────────────┤
│  ÉVÉNEMENT  ⚠  Araignée détectée ! [s] Envoyer soldates    │
├─────────────────────────────────────────────────────────────┤
│  [u] Upgrades   [e] Événements   [t] Stats   [q] Quitter   │
└─────────────────────────────────────────────────────────────┘
```

### Écran Upgrades (overlay)

```
┌─────────────────────────────────────────────┐
│  UPGRADES                    💰 1,247       │
│                                             │
│  ✅ Pattes renforcées        (acheté)       │
│  ▶  Phéromones optimisées    $500           │
│     Champignonnière          $800           │
│     Nurserie renforcée       $1,200         │
│  🔒 Crèche royale            (locked)       │
│                                             │
│  [↑↓] Naviguer  [Entrée] Acheter  [Esc] OK │
└─────────────────────────────────────────────┘
```

---

## 7. Persistance

- Sauvegarde automatique : `~/.ant-colony/save.json`
- Fréquence : toutes les 30 secondes + à la fermeture
- Au lancement : calcul des gains offline (population qui a continué de travailler)
- Gains offline plafonés à **8h** pour ne pas trivialiser le jeu

---

## 8. Stack technique

| Choix | Justification |
|-------|---------------|
| **Python 3.11+** | Pas de compilation, facile à lancer |
| **Textual** | TUI moderne, réactif, composants, timers natifs |
| **Aucune DB** | JSON pur pour la sauvegarde |
| **Un seul binaire** | `python ant_colony.py` pour lancer |

### Dépendances

```
textual>=0.50
```

---

## 9. Hors scope (v1)

- Sons / musique
- Multijoueur
- Sauvegarde cloud
- Mode nuit / thème customisé
- Espèces de fourmis exotiques (post-v1)

---

## 10. Métriques de succès

- Session de 5 min sans action → jeu toujours vivant et lisible
- Progression visible après 1h de jeu idle
- Lancement en < 1 seconde
- Mémoire < 50 MB

---

## Questions ouvertes

- [ ] Les gains offline sont-ils calculés "fidèlement" ou estimés ?
- [ ] Faut-il un mode "accéléré" (×2, ×4) pour les tests ?
- [ ] Veut-on de l'ASCII art animé pour la fourmilière, ou juste une grille symbolique ?
- [ ] Combien de temps pour atteindre la "fin" du jeu (objectif jour 30 ?) ?
