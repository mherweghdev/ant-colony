# Design : Mouvement 2D des fourmis (nid ↔ nourriture)

**Date :** 2026-04-08  
**Fichier cible :** `ui/world_widget.py`  
**Statut :** Approuvé

---

## Contexte

Les fourmis cosmétiques de `WorldWidget` ne se déplacent actuellement que sur l'axe X, restant fixes à `nest_y - 1 ± row_offset` (ligne de sol). Les sources de nourriture sont positionnées dans la moitié haute de l'écran (y ≈ h/3) mais les fourmis n'atteignent jamais ces coordonnées Y. L'animation manque de profondeur visuelle.

## Objectif

Donner aux fourmis un vrai mouvement 2D (vectoriel) qui les fait partir du nid vers la nourriture en traversant verticalement l'espace, avec des phéromones traçant le chemin réel.

---

## Design

### 1. `CosmeticAnt` — suppression de `row_offset`

`row_offset: int` est utilisé uniquement pour simuler une variation verticale approximative. Avec un vrai axe Y, ce champ devient redondant et sera supprimé.

La position `y` de la fourmi sera mise à jour dynamiquement comme `x`.

### 2. `_move_ants` — mouvement vectoriel

**Cibles :**
- `going_to_food=True` → `(source.x, source.y)`
- `going_to_food=False` → `(nest_x, nest_y - 1)`

**Calcul du déplacement :**
```
dx = target_x - ant.x
dy = target_y - ant.y
dist = sqrt(dx² + dy²)

if dist < speed:
    snap to target, invert going_to_food
else:
    ant.x += speed * dx / dist
    ant.y += speed * dy / dist
```

### 3. Phéromones — chemin réel

Actuellement déposées à `(int(ant.x), nest_y - 1 + row_offset)` (position fixe au sol).

Nouvelle position : `(int(ant.x), int(ant.y))` — trace le chemin diagonal réel nid↔nourriture.

### 4. Rendu — coordonnée Y directe

Actuellement : `ay = min(ground_y - 1, max(0, self._nest_y - 1 + ant.row_offset))`

Nouveau : `ay = int(ant.y)` — utilise la position Y réelle de la fourmi.

---

## Impact

| Élément | Avant | Après |
|---|---|---|
| Mouvement fourmi | Horizontal uniquement | Vectoriel 2D |
| Position Y fourmi | Fixe (nest_y ± 1) | Variable (nest_y → source.y) |
| Phéromones | Ligne horizontale au sol | Chemin diagonal |
| `row_offset` | Champ de `CosmeticAnt` | Supprimé |

## Fichiers modifiés

- `ui/world_widget.py` — seul fichier à modifier

## Tests

Aucun test UI automatisé requis (composant cosmétique). Vérification visuelle suffisante.
