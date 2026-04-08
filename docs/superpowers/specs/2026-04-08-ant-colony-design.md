# Design — Ant Colony MVP

> Date : 2026-04-08
> Statut : approuvé

---

## Contexte

Jeu idle terminal (TUI) conçu pour tourner en plein écran sur un second écran de 10" pendant une journée de travail. L'ambiance est contemplative et satisfaisante à observer passivement. Pas de pression, pas de défaite.

**Stack** : Python 3.11+, Textual ≥ 0.50, sauvegarde JSON.

---

## 1. Architecture

Trois couches strictement séparées :

```
Textual App
├── WorldWidget        ← animation cosmétique des fourmis
├── StatsPanel         ← ressources, population, reine
└── UpgradeOverlay     ← overlay clavier (u / Esc)
        ↑
    GameState          ← dataclass Python pur (aucune dépendance Textual)
        ↑
    GameLoop           ← set_interval(0.25s) Textual, met à jour GameState
```

**Règle d'or** : les widgets lisent GameState, ne le modifient jamais directement. Toute modification passe par des méthodes de GameState appelées depuis les handlers clavier de l'app.

---

## 2. État du jeu (GameState)

```python
@dataclass
class GameState:
    # Ressources
    food: float = 50.0
    food_max: float = 500.0
    materials: float = 20.0
    materials_max: float = 300.0

    # Population
    population: int = 10
    foragers: int = 5      # collectent nourriture
    workers: int = 4       # collectent matériaux
    idle: int = 1

    # Reine
    eggs: float = 0.0      # s'accumule ; éclosion à 1.0 → +1 fourmi idle

    # Upgrades achetés
    upgrades: set[str] = field(default_factory=set)

    # Temps de jeu (en ticks de 250ms)
    ticks: int = 0
```

---

## 3. Boucle de jeu (tick à 250ms)

À chaque tick :

### 3.1 Production
- `food += foragers × 0.05 × production_multiplier`
- `materials += workers × 0.03`
- `eggs += 0.01 × egg_multiplier`
- Champignonnière débloquée : `food += 0.5` (passif)

### 3.2 Consommation de nourriture
- `food -= population × 0.01`
- Si `food <= 0` et `food == 0` depuis 20 ticks (5s) : `-1 fourmi` (retirée des idle en premier, puis fourrageuses, puis ouvrières)
- La reine arrête de pondre si `food == 0`

### 3.3 Mortalité naturelle
- Lifespan : 30 jours de jeu (1 jour = 1200 ticks = 5 minutes réelles)
- Taux de mort par tick : `population / 36000` (probabiliste, loi des grands nombres)
- En moyenne ~1 mort/jour par tranche de ~120 fourmis
- La mort retire une fourmi au hasard parmi idle → fourrageuses → ouvrières

### 3.4 Éclosion
- Si `eggs >= 1.0` : `eggs -= 1.0`, `population += 1`, `idle += 1`

### 3.5 Indicateur de tendance nourriture
- `food_rate = (foragers × 0.05 × multiplier) - (population × 0.01) + champignonniere_bonus`
- Affiché en temps réel dans StatsPanel (+ ou - /min)

---

## 4. Upgrades MVP

Monnaie = **nourriture**. 6 upgrades en 3 tiers.

| Upgrade | Coût | Effet | Débloqué par |
|---------|------|-------|--------------|
| Garde-manger | 200 | `food_max` ×2 (→ 1000) | — |
| Pattes renforcées | 300 | `production_multiplier` fourrageuses ×1.2 | — |
| Phéromones optimisées | 600 | `production_multiplier` fourrageuses ×1.4 | ≥1 upgrade T1 |
| Chambre de stockage | 500 | `materials_max` ×2 (→ 600) | ≥1 upgrade T1 |
| Nurserie renforcée | 1200 | `egg_multiplier` ×2 | ≥2 upgrades T2 |
| Champignonnière | 2000 | +0.5 nourriture/tick passif | ≥2 upgrades T2 |

Les multiplicateurs sont cumulatifs (Pattes + Phéromones = ×1.68).

---

## 5. Interface TUI

### 5.1 Layout principal

```
┌─────────────────────────────────────────────────────────────────────────┐
│  🐜 ANT COLONY                                        Jour 4  |  14:22  │
├──────────────────────────────────────────┬──────────────────────────────┤
│                                          │  RESSOURCES                  │
│  🍃  🌿        🌿                        │  🍖 ████████░░  824 / 1000   │
│                      ·  ·  a  ·          │     +12.4 / min  ▲           │
│   a →→→→→→→→→→→→→→→→→→→→→ A  🍄 🍄    │  🪨 ████░░░░░░  412 /  800   │
│      ←←←←←←←←←←←←←←←←←← A            │                              │
│   a →→→→→→→→→→→→→→→→→→→→→→→→→→ A  🍄   │  POPULATION       127 🐜     │
│                  ·    ·    ·             │  Fourrageuses  80  [+][-]    │
│  🍃         ·  ·  a  ·                  │  Ouvrières     40  [+][-]    │
│                                          │  Inactives      7            │
│  ══════════════════[▼NŒUD]══════════════ │                              │
│                                          │  REINE                       │
│                                          │  Œufs  ██░░░░░░  0.4 / 1.0  │
│                                          │  Natalité   ~3/jour  ▲       │
│                                          │  Mortalité  ~2/jour          │
├──────────────────────────────────────────┴──────────────────────────────┤
│  [u] Upgrades    [+][-] Assigner    [q] Quitter                         │
└─────────────────────────────────────────────────────────────────────────┘
```

Proportions : WorldWidget ~65% largeur, StatsPanel ~35% largeur.

### 5.2 Overlay Upgrades

```
┌─────────────────────────────────────┐
│  UPGRADES              💰 824       │
│                                     │
│  ✅ Garde-manger        (acheté)    │
│  ▶  Pattes renforcées    $300       │
│     Phéromones optim.    $600  🔒   │
│     Chambre stockage     $500  🔒   │
│     Nurserie renforcée  $1200  🔒   │
│     Champignonnière     $2000  🔒   │
│                                     │
│  [↑↓] Naviguer  [Entrée] Acheter   │
│  [Esc] Fermer                       │
└─────────────────────────────────────┘
```

### 5.3 Animation WorldWidget

- Éléments statiques (emoji) : `🍃 🌿 🍄` placés aléatoirement à l'init, positions fixes
- Fourmis animées (ASCII) :
  - `a` = fourmi vide (va vers source)
  - `A` = fourmi chargée (revient au nid)
  - `·` = trace de phéromone, disparaît après 3–5 ticks
  - Routes légèrement sinueuses (variation ±1 ligne aléatoire)
- Nombre de fourmis affichées à l'écran ∝ `foragers` (cosmétique, pas 1:1)
- Si `food == 0` : fourmis ralentissent (tick animation /2)

---

## 6. Persistance

- Fichier : `~/.ant-colony/save.json`
- Sauvegarde : toutes les 30s + à la fermeture (`on_unmount`)
- Chargement : au lancement, restaure GameState depuis JSON
- Pas de gains offline : le temps de jeu ne s'écoule que quand l'app tourne
- Champs sauvegardés : tous les champs de GameState

---

## 7. Hors scope MVP

- Événements aléatoires (araignée, pluie, sécheresse)
- Soldates / Champignonnistes comme castes assignables
- Commerce inter-colonies
- Gains offline
- Sons / thèmes
- Reine secondaire

---

## 8. Conditions de succès MVP

- Boucle idle fonctionne sans intervention : ressources montent, fourmis naissent et meurent
- Animation visible et fluide sur terminal 10" plein écran
- 6 upgrades achetables avec progression lisible
- Sauvegarde / rechargement sans perte d'état
- Lancement en < 1 seconde (`python ant_colony.py`)
