# Ant 2D Movement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Faire se déplacer les fourmis en 2D (nid ↔ nourriture) avec des phéromones traçant le chemin réel.

**Architecture:** Mouvement vectoriel dans `_move_ants` — calcul d'un vecteur `(dx, dy)` normalisé par la distance, mise à jour de `ant.x` et `ant.y` simultanément. Le `row_offset` est supprimé car le vrai axe Y le remplace.

**Tech Stack:** Python 3, Textual, `math.sqrt`

---

## Fichiers modifiés

- Modify: `ui/world_widget.py` — seul fichier concerné

---

### Task 1 : Supprimer `row_offset` de `CosmeticAnt` et `_spawn_ant`

**Files:**
- Modify: `ui/world_widget.py:22-28` (dataclass `CosmeticAnt`)
- Modify: `ui/world_widget.py:89-98` (méthode `_spawn_ant`)

- [ ] **Step 1 : Ajouter `import math` en tête de fichier**

Remplacer la ligne 1 de `ui/world_widget.py` :
```python
import math
import random
from dataclasses import dataclass
from rich.text import Text
from textual.widget import Widget

from game.state import GameState
```

- [ ] **Step 2 : Supprimer `row_offset` du dataclass `CosmeticAnt`**

Remplacer le dataclass (lignes 21-29) :
```python
@dataclass
class CosmeticAnt:
    x: float
    y: float
    source_index: int       # which FoodSource this ant targets
    going_to_food: bool     # True = heading to food, False = returning
    speed: float            # columns per tick
    slow: bool = False      # True when starving
```

- [ ] **Step 3 : Mettre à jour `_spawn_ant` — retirer `row_offset`**

Remplacer la méthode `_spawn_ant` (lignes 89-98) :
```python
def _spawn_ant(self) -> None:
    source_idx = random.randint(0, max(0, len(self._food_sources) - 1))
    self._ants.append(CosmeticAnt(
        x=float(self._nest_x),
        y=float(self._nest_y - 1),
        source_index=source_idx,
        going_to_food=True,
        speed=random.uniform(0.8, 1.4),
    ))
```

- [ ] **Step 4 : Vérifier que le projet démarre sans erreur**

```bash
python ant_colony.py
```
Expected : l'interface se lance sans `TypeError` ni `AttributeError`.

---

### Task 2 : Mouvement 2D vectoriel dans `_move_ants`

**Files:**
- Modify: `ui/world_widget.py:100-121` (méthode `_move_ants`)

- [ ] **Step 1 : Remplacer `_move_ants` par la version 2D**

Remplacer la méthode entière `_move_ants` :
```python
def _move_ants(self, state: GameState) -> None:
    starving = state.food <= 0
    for ant in self._ants:
        ant.slow = starving
        if starving and state.ticks % 2 != 0:
            continue  # move every 2 ticks when starving

        source = self._food_sources[ant.source_index]
        if ant.going_to_food:
            target_x = float(source.x)
            target_y = float(source.y)
        else:
            target_x = float(self._nest_x)
            target_y = float(self._nest_y - 1)

        dx = target_x - ant.x
        dy = target_y - ant.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < ant.speed:
            ant.x = target_x
            ant.y = target_y
            ant.going_to_food = not ant.going_to_food
        else:
            ant.x += ant.speed * dx / dist
            ant.y += ant.speed * dy / dist

        # Leave pheromone on real path
        px, py = int(ant.x), int(ant.y)
        if 0 <= px < self._width and 0 <= py < self._height:
            self._pheromones[(px, py)] = random.randint(3, 6)
```

- [ ] **Step 2 : Lancer et vérifier visuellement**

```bash
python ant_colony.py
```
Expected : les fourmis partent du bas (nid) et montent en diagonale vers les emojis de nourriture, puis reviennent.

---

### Task 3 : Mettre à jour le rendu pour utiliser `ant.y` directement

**Files:**
- Modify: `ui/world_widget.py:175-181` (section Ants dans `render`)

- [ ] **Step 1 : Remplacer le calcul de `ay` dans `render`**

Remplacer le bloc ants dans `render` (lignes 175-181) :
```python
        # Ants
        for ant in self._ants:
            ax = int(ant.x)
            ay = int(ant.y)
            if 0 <= ay < h and 0 <= ax < w:
                char = "a" if ant.going_to_food else "A"
                style = "yellow" if ant.going_to_food else "bold yellow"
                grid[ay][ax] = (char, style)
```

- [ ] **Step 2 : Vérifier visuellement le rendu final**

```bash
python ant_colony.py
```
Expected :
- Les fourmis `a` montent du nid vers la nourriture
- Les fourmis `A` descendent de la nourriture vers le nid
- Les phéromones `·` (vert dim) tracent les chemins diagonaux

---

### Task 4 : Commit

- [ ] **Step 1 : Stager et committer**

```bash
git add ui/world_widget.py
git commit -m "feat: mouvement 2D vectoriel des fourmis nid↔nourriture

- Suppression de row_offset dans CosmeticAnt
- Déplacement vectoriel (dx,dy) normalisé par la distance
- Phéromones déposées sur le chemin réel (ant.x, ant.y)
- Rendu utilise ant.y directement"
```
