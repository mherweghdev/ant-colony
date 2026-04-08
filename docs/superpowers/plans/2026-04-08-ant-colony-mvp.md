# Ant Colony MVP — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a playable terminal idle game where ants move visibly on screen, the colony grows and ages, and the player manages food resources and population assignments.

**Architecture:** Pure Python game logic (`game/`) fully decoupled from Textual TUI (`ui/`). `GameState` is a dataclass mutated by pure tick functions. Cosmetic ant animation in `WorldWidget` is independent of `GameState` counters.

**Tech Stack:** Python 3.11+, Textual ≥ 0.50 (includes Rich), pytest, pathlib, json, dataclasses, random.

---

## File Structure

```
ant-colony/
├── ant_colony.py              # Entry point: python ant_colony.py
├── requirements.txt           # textual>=0.50, pytest
├── game/
│   ├── __init__.py
│   ├── state.py               # GameState dataclass
│   ├── loop.py                # tick() + sub-tick functions (pure Python)
│   └── upgrades.py            # UPGRADES dict, is_available(), buy_upgrade()
├── ui/
│   ├── __init__.py
│   ├── app.py                 # AntColonyApp(App) — layout, timers, key bindings
│   ├── world_widget.py        # WorldWidget — cosmetic ant animation
│   ├── stats_panel.py         # StatsPanel — resources, population, queen
│   └── upgrade_overlay.py     # UpgradeOverlay — scrollable upgrade list
├── persistence/
│   ├── __init__.py
│   └── save.py                # save_game(), load_game()
└── tests/
    ├── __init__.py
    ├── test_state.py
    ├── test_loop.py
    ├── test_upgrades.py
    └── test_persistence.py
```

---

## Task 1 — Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `game/__init__.py`, `ui/__init__.py`, `persistence/__init__.py`, `tests/__init__.py`
- Create: `ant_colony.py` (stub)

- [ ] **Step 1: Create directory structure**

```bash
cd /Users/matthieu.herwegh/Documents/ant-colony
mkdir -p game ui persistence tests
touch game/__init__.py ui/__init__.py persistence/__init__.py tests/__init__.py
```

- [ ] **Step 2: Create requirements.txt**

```
textual>=0.50
pytest>=7.0
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

Expected: `Successfully installed textual-X.Y.Z` (et pytest si pas déjà présent)

- [ ] **Step 4: Create entry point stub**

Créer `ant_colony.py` :
```python
from ui.app import AntColonyApp

if __name__ == "__main__":
    app = AntColonyApp()
    app.run()
```

- [ ] **Step 5: Commit**

```bash
git init
git add .
git commit -m "chore: project structure and dependencies"
```

---

## Task 2 — GameState Dataclass

**Files:**
- Create: `game/state.py`
- Create: `tests/test_state.py`

- [ ] **Step 1: Write the failing test**

Créer `tests/test_state.py` :
```python
from game.state import GameState

def test_initial_values():
    state = GameState()
    assert state.food == 50.0
    assert state.food_max == 500.0
    assert state.materials == 20.0
    assert state.materials_max == 300.0
    assert state.population == 10
    assert state.foragers == 5
    assert state.workers == 4
    assert state.idle == 1
    assert state.eggs == 0.0
    assert state.upgrades == set()
    assert state.ticks == 0
    assert state.starvation_ticks == 0

def test_population_is_consistent():
    state = GameState()
    assert state.foragers + state.workers + state.idle == state.population
```

- [ ] **Step 2: Run test to verify it fails**

```bash
cd /Users/matthieu.herwegh/Documents/ant-colony
pytest tests/test_state.py -v
```

Expected: `FAILED` — `ModuleNotFoundError: No module named 'game.state'`

- [ ] **Step 3: Write GameState**

Créer `game/state.py` :
```python
from dataclasses import dataclass, field


@dataclass
class GameState:
    # Resources
    food: float = 50.0
    food_max: float = 500.0
    materials: float = 20.0
    materials_max: float = 300.0

    # Population
    population: int = 10
    foragers: int = 5       # collect food
    workers: int = 4        # collect materials
    idle: int = 1

    # Queen
    eggs: float = 0.0       # accumulates; hatches at 1.0 → +1 idle ant

    # Upgrades purchased
    upgrades: set = field(default_factory=set)

    # Game time in ticks (250ms each)
    ticks: int = 0

    # Starvation counter (ticks since food hit 0)
    starvation_ticks: int = 0
```

- [ ] **Step 4: Run test to verify it passes**

```bash
pytest tests/test_state.py -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add game/state.py tests/test_state.py
git commit -m "feat: GameState dataclass with initial values"
```

---

## Task 3 — Production Tick

**Files:**
- Create: `game/loop.py`
- Create: `tests/test_loop.py`

- [ ] **Step 1: Write failing tests**

Créer `tests/test_loop.py` :
```python
from game.state import GameState
from game.loop import tick_production

def test_food_increases_with_foragers():
    state = GameState(food=50.0, foragers=5, upgrades=set())
    tick_production(state)
    # 5 foragers × 0.05 = 0.25
    assert abs(state.food - 50.25) < 0.001

def test_materials_increase_with_workers():
    state = GameState(materials=20.0, workers=4)
    tick_production(state)
    # 4 workers × 0.03 = 0.12
    assert abs(state.materials - 20.12) < 0.001

def test_food_capped_at_food_max():
    state = GameState(food=499.9, food_max=500.0, foragers=10)
    tick_production(state)
    assert state.food == 500.0

def test_eggs_accumulate():
    state = GameState(eggs=0.0, food=100.0)
    tick_production(state)
    assert abs(state.eggs - 0.01) < 0.001

def test_eggs_dont_accumulate_when_starving():
    state = GameState(eggs=0.5, food=0.0)
    tick_production(state)
    assert state.eggs == 0.5

def test_pattes_renforcees_multiplier():
    state = GameState(food=0.0, foragers=10, upgrades={"pattes_renforcees"})
    tick_production(state)
    # 10 × 0.05 × 1.2 = 0.6
    assert abs(state.food - 0.6) < 0.001

def test_champignonniere_passive_food():
    state = GameState(food=0.0, foragers=0, upgrades={"champignonniere"})
    tick_production(state)
    assert abs(state.food - 0.5) < 0.001
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_loop.py -v
```

Expected: `FAILED` — `cannot import name 'tick_production'`

- [ ] **Step 3: Implement tick_production**

Créer `game/loop.py` :
```python
import random
from game.state import GameState

# --- Constants ---
FOOD_PER_FORAGER_PER_TICK = 0.05
MATERIALS_PER_WORKER_PER_TICK = 0.03
EGG_PER_TICK = 0.01
CHAMPIGNONNIERE_BONUS = 0.5
FOOD_PER_ANT_PER_TICK = 0.01
STARVATION_DELAY_TICKS = 20       # 5s at 250ms/tick
LIFESPAN_TICKS = 36000            # 30 days × 1200 ticks/day


def tick_production(state: GameState) -> None:
    """Increment resources based on assigned ants and upgrades."""
    multiplier = _production_multiplier(state)
    egg_multiplier = 2.0 if "nurserie_renforcee" in state.upgrades else 1.0

    state.food = min(
        state.food_max,
        state.food + state.foragers * FOOD_PER_FORAGER_PER_TICK * multiplier,
    )
    if "champignonniere" in state.upgrades:
        state.food = min(state.food_max, state.food + CHAMPIGNONNIERE_BONUS)

    state.materials = min(
        state.materials_max,
        state.materials + state.workers * MATERIALS_PER_WORKER_PER_TICK,
    )

    if state.food > 0:
        state.eggs += EGG_PER_TICK * egg_multiplier


def _production_multiplier(state: GameState) -> float:
    multiplier = 1.0
    if "pattes_renforcees" in state.upgrades:
        multiplier *= 1.2
    if "pheromones_optimisees" in state.upgrades:
        multiplier *= 1.4
    return multiplier
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_loop.py -v
```

Expected: `7 passed`

- [ ] **Step 5: Commit**

```bash
git add game/loop.py tests/test_loop.py
git commit -m "feat: production tick for food, materials, eggs"
```

---

## Task 4 — Consumption + Starvation

**Files:**
- Modify: `game/loop.py` (ajouter `tick_consumption`)
- Modify: `tests/test_loop.py` (ajouter tests)

- [ ] **Step 1: Write failing tests**

Ajouter à `tests/test_loop.py` :
```python
from game.loop import tick_consumption

def test_food_decreases_with_population():
    state = GameState(food=50.0, population=10)
    tick_consumption(state)
    # 10 ants × 0.01 = 0.1
    assert abs(state.food - 49.9) < 0.001

def test_food_never_below_zero():
    state = GameState(food=0.05, population=100)
    tick_consumption(state)
    assert state.food == 0.0

def test_starvation_counter_increments_when_no_food():
    state = GameState(food=0.0, population=5)
    tick_consumption(state)
    assert state.starvation_ticks == 1

def test_starvation_counter_resets_when_fed():
    state = GameState(food=10.0, population=5, starvation_ticks=5)
    tick_consumption(state)
    assert state.starvation_ticks == 0

def test_ant_dies_after_starvation_delay():
    # STARVATION_DELAY_TICKS = 20
    state = GameState(food=0.0, population=5, foragers=3, workers=1, idle=1, starvation_ticks=19)
    tick_consumption(state)
    assert state.population == 4
    assert state.starvation_ticks == 0

def test_idle_ant_dies_first_during_starvation():
    state = GameState(food=0.0, population=5, foragers=3, workers=1, idle=1, starvation_ticks=19)
    tick_consumption(state)
    assert state.idle == 0
    assert state.foragers == 3

def test_forager_dies_when_no_idle():
    state = GameState(food=0.0, population=4, foragers=3, workers=1, idle=0, starvation_ticks=19)
    tick_consumption(state)
    assert state.foragers == 2
    assert state.population == 3

def test_no_death_if_only_one_ant():
    state = GameState(food=0.0, population=1, foragers=0, workers=0, idle=1, starvation_ticks=19)
    tick_consumption(state)
    assert state.population == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_loop.py::test_food_decreases_with_population -v
```

Expected: `FAILED` — `cannot import name 'tick_consumption'`

- [ ] **Step 3: Implement tick_consumption**

Ajouter à `game/loop.py` après `tick_production` :
```python
def tick_consumption(state: GameState) -> None:
    """Decrease food by colony consumption; kill ant if starving too long."""
    state.food = max(0.0, state.food - state.population * FOOD_PER_ANT_PER_TICK)

    if state.food <= 0:
        state.starvation_ticks += 1
        if state.starvation_ticks >= STARVATION_DELAY_TICKS:
            state.starvation_ticks = 0
            _kill_one_ant(state)
    else:
        state.starvation_ticks = 0


def _kill_one_ant(state: GameState) -> None:
    """Remove one ant, prioritising idle > foragers > workers."""
    if state.population <= 1:
        return
    if state.idle > 0:
        state.idle -= 1
    elif state.foragers > 0:
        state.foragers -= 1
    elif state.workers > 0:
        state.workers -= 1
    state.population -= 1
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_loop.py -v
```

Expected: all previously passing + 8 new = `15 passed`

- [ ] **Step 5: Commit**

```bash
git add game/loop.py tests/test_loop.py
git commit -m "feat: food consumption and starvation death"
```

---

## Task 5 — Natural Death, Hatching, and tick() Orchestrator

**Files:**
- Modify: `game/loop.py` (ajouter `tick_aging`, `tick_hatching`, `tick`)
- Modify: `tests/test_loop.py`

- [ ] **Step 1: Write failing tests**

Ajouter à `tests/test_loop.py` :
```python
from unittest.mock import patch
from game.loop import tick_aging, tick_hatching, tick

def test_hatching_adds_idle_ant():
    state = GameState(eggs=1.0, population=10, idle=1)
    tick_hatching(state)
    assert state.eggs == 0.0
    assert state.population == 11
    assert state.idle == 2

def test_no_hatch_below_threshold():
    state = GameState(eggs=0.9, population=10, idle=1)
    tick_hatching(state)
    assert state.population == 10
    assert abs(state.eggs - 0.9) < 0.001

def test_natural_death_occurs_probabilistically():
    # With population=36000, probability per tick = 1.0 → always dies
    state = GameState(population=36000, foragers=20000, workers=15000, idle=1000)
    with patch("random.random", return_value=0.0):  # 0.0 < 1.0 → always triggers
        tick_aging(state)
    assert state.population == 35999

def test_no_death_at_zero_population():
    state = GameState(population=0, foragers=0, workers=0, idle=0)
    tick_aging(state)
    assert state.population == 0

def test_tick_increments_ticks_counter():
    state = GameState()
    tick(state)
    assert state.ticks == 1

def test_tick_calls_all_phases():
    state = GameState(food=100.0, foragers=5, workers=4, population=10)
    initial_food = state.food
    tick(state)
    # Food changed = production ran, consumption ran
    assert state.food != initial_food
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_loop.py::test_hatching_adds_idle_ant -v
```

Expected: `FAILED` — `cannot import name 'tick_hatching'`

- [ ] **Step 3: Implement tick_aging, tick_hatching, tick**

Ajouter à la fin de `game/loop.py` :
```python
def tick_aging(state: GameState) -> None:
    """Probabilistically kill one ant per tick based on lifespan."""
    if state.population <= 0:
        return
    death_probability = state.population / LIFESPAN_TICKS
    if random.random() < death_probability:
        _kill_one_ant(state)


def tick_hatching(state: GameState) -> None:
    """Hatch eggs into idle ants when threshold reached."""
    if state.eggs >= 1.0:
        state.eggs -= 1.0
        state.population += 1
        state.idle += 1


def tick(state: GameState) -> None:
    """Run one full game tick (called every 250ms)."""
    state.ticks += 1
    tick_production(state)
    tick_consumption(state)
    tick_aging(state)
    tick_hatching(state)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_loop.py -v
```

Expected: all `21 passed`

- [ ] **Step 5: Commit**

```bash
git add game/loop.py tests/test_loop.py
git commit -m "feat: natural death, egg hatching, and tick() orchestrator"
```

---

## Task 6 — Upgrades System

**Files:**
- Create: `game/upgrades.py`
- Create: `tests/test_upgrades.py`

- [ ] **Step 1: Write failing tests**

Créer `tests/test_upgrades.py` :
```python
from game.state import GameState
from game.upgrades import is_available, buy_upgrade, UPGRADES

def test_tier1_always_available():
    state = GameState()
    assert is_available("garde_manger", state) is True
    assert is_available("pattes_renforcees", state) is True

def test_tier2_locked_without_tier1():
    state = GameState()
    assert is_available("pheromones_optimisees", state) is False
    assert is_available("chambre_stockage", state) is False

def test_tier2_unlocked_after_one_tier1():
    state = GameState(upgrades={"garde_manger"})
    assert is_available("pheromones_optimisees", state) is True

def test_tier3_locked_without_two_tier2():
    state = GameState(upgrades={"garde_manger", "pheromones_optimisees"})
    assert is_available("nurserie_renforcee", state) is False

def test_tier3_unlocked_after_two_tier2():
    state = GameState(upgrades={"pheromones_optimisees", "chambre_stockage"})
    assert is_available("nurserie_renforcee", state) is True

def test_already_bought_not_available():
    state = GameState(upgrades={"garde_manger"})
    assert is_available("garde_manger", state) is False

def test_buy_upgrade_deducts_food():
    state = GameState(food=300.0, upgrades=set())
    result = buy_upgrade("garde_manger", state)
    assert result is True
    assert state.food == 100.0  # 300 - 200

def test_buy_upgrade_fails_insufficient_food():
    state = GameState(food=100.0, upgrades=set())
    result = buy_upgrade("garde_manger", state)
    assert result is False
    assert state.food == 100.0

def test_garde_manger_doubles_food_max():
    state = GameState(food=300.0, food_max=500.0)
    buy_upgrade("garde_manger", state)
    assert state.food_max == 1000.0

def test_chambre_stockage_doubles_materials_max():
    state = GameState(food=600.0, materials_max=300.0, upgrades={"garde_manger"})
    buy_upgrade("chambre_stockage", state)
    assert state.materials_max == 600.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_upgrades.py -v
```

Expected: `FAILED` — `cannot import name 'is_available'`

- [ ] **Step 3: Implement upgrades.py**

Créer `game/upgrades.py` :
```python
from game.state import GameState

UPGRADES: dict = {
    "garde_manger": {
        "name": "Garde-manger",
        "cost": 200,
        "tier": 1,
        "description": "Capacité nourriture ×2",
    },
    "pattes_renforcees": {
        "name": "Pattes renforcées",
        "cost": 300,
        "tier": 1,
        "description": "Fourrageuses +20% production",
    },
    "pheromones_optimisees": {
        "name": "Phéromones optimisées",
        "cost": 600,
        "tier": 2,
        "description": "Fourrageuses +40% production",
    },
    "chambre_stockage": {
        "name": "Chambre de stockage",
        "cost": 500,
        "tier": 2,
        "description": "Capacité matériaux ×2",
    },
    "nurserie_renforcee": {
        "name": "Nurserie renforcée",
        "cost": 1200,
        "tier": 3,
        "description": "Vitesse éclosion ×2",
    },
    "champignonniere": {
        "name": "Champignonnière",
        "cost": 2000,
        "tier": 3,
        "description": "+0.5 nourriture/tick passif",
    },
}

UPGRADE_ORDER = [
    "garde_manger",
    "pattes_renforcees",
    "pheromones_optimisees",
    "chambre_stockage",
    "nurserie_renforcee",
    "champignonniere",
]


def is_available(upgrade_id: str, state: GameState) -> bool:
    """Return True if upgrade can be purchased (not already owned, tier unlocked)."""
    if upgrade_id in state.upgrades:
        return False
    tier = UPGRADES[upgrade_id]["tier"]
    if tier == 1:
        return True
    if tier == 2:
        t1_bought = sum(1 for uid in UPGRADES if UPGRADES[uid]["tier"] == 1 and uid in state.upgrades)
        return t1_bought >= 1
    if tier == 3:
        t2_bought = sum(1 for uid in UPGRADES if UPGRADES[uid]["tier"] == 2 and uid in state.upgrades)
        return t2_bought >= 2
    return False


def buy_upgrade(upgrade_id: str, state: GameState) -> bool:
    """Purchase an upgrade. Returns True on success, False on failure."""
    if not is_available(upgrade_id, state):
        return False
    cost = UPGRADES[upgrade_id]["cost"]
    if state.food < cost:
        return False
    state.food -= cost
    state.upgrades.add(upgrade_id)
    _apply_effect(upgrade_id, state)
    return True


def _apply_effect(upgrade_id: str, state: GameState) -> None:
    if upgrade_id == "garde_manger":
        state.food_max *= 2
    elif upgrade_id == "chambre_stockage":
        state.materials_max *= 2
    # pattes_renforcees, pheromones_optimisees, nurserie_renforcee, champignonniere:
    # effects are applied dynamically in game/loop.py via upgrades set
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_upgrades.py -v
```

Expected: `11 passed`

- [ ] **Step 5: Run all tests**

```bash
pytest tests/ -v
```

Expected: `32 passed`

- [ ] **Step 6: Commit**

```bash
git add game/upgrades.py tests/test_upgrades.py
git commit -m "feat: upgrade system with tier gating and purchase logic"
```

---

## Task 7 — Persistence (Save/Load)

**Files:**
- Create: `persistence/save.py`
- Create: `tests/test_persistence.py`

- [ ] **Step 1: Write failing tests**

Créer `tests/test_persistence.py` :
```python
import json
from pathlib import Path
import pytest
from game.state import GameState
from persistence.save import save_game, load_game

@pytest.fixture
def tmp_save_path(tmp_path, monkeypatch):
    save_file = tmp_path / "save.json"
    monkeypatch.setattr("persistence.save.SAVE_PATH", save_file)
    return save_file

def test_save_creates_file(tmp_save_path):
    state = GameState()
    save_game(state)
    assert tmp_save_path.exists()

def test_round_trip_preserves_values(tmp_save_path):
    state = GameState(
        food=123.4,
        food_max=1000.0,
        materials=56.7,
        materials_max=600.0,
        population=25,
        foragers=12,
        workers=10,
        idle=3,
        eggs=0.7,
        upgrades={"garde_manger", "pattes_renforcees"},
        ticks=9999,
    )
    save_game(state)
    loaded = load_game()
    assert abs(loaded.food - 123.4) < 0.001
    assert loaded.food_max == 1000.0
    assert loaded.population == 25
    assert loaded.foragers == 12
    assert loaded.upgrades == {"garde_manger", "pattes_renforcees"}
    assert loaded.ticks == 9999

def test_load_returns_default_when_no_file(tmp_save_path):
    assert not tmp_save_path.exists()
    state = load_game()
    assert state.food == 50.0
    assert state.population == 10
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_persistence.py -v
```

Expected: `FAILED` — `cannot import name 'save_game'`

- [ ] **Step 3: Implement persistence/save.py**

Créer `persistence/save.py` :
```python
import json
from pathlib import Path
from game.state import GameState

SAVE_PATH = Path.home() / ".ant-colony" / "save.json"


def save_game(state: GameState) -> None:
    """Serialize GameState to JSON file."""
    SAVE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "food": state.food,
        "food_max": state.food_max,
        "materials": state.materials,
        "materials_max": state.materials_max,
        "population": state.population,
        "foragers": state.foragers,
        "workers": state.workers,
        "idle": state.idle,
        "eggs": state.eggs,
        "upgrades": sorted(state.upgrades),
        "ticks": state.ticks,
    }
    SAVE_PATH.write_text(json.dumps(data, indent=2))


def load_game() -> GameState:
    """Deserialize GameState from JSON, returning defaults if no save exists."""
    if not SAVE_PATH.exists():
        return GameState()
    data = json.loads(SAVE_PATH.read_text())
    state = GameState()
    state.food = data.get("food", 50.0)
    state.food_max = data.get("food_max", 500.0)
    state.materials = data.get("materials", 20.0)
    state.materials_max = data.get("materials_max", 300.0)
    state.population = data.get("population", 10)
    state.foragers = data.get("foragers", 5)
    state.workers = data.get("workers", 4)
    state.idle = data.get("idle", 1)
    state.eggs = data.get("eggs", 0.0)
    state.upgrades = set(data.get("upgrades", []))
    state.ticks = data.get("ticks", 0)
    return state
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_persistence.py -v
```

Expected: `3 passed`

- [ ] **Step 5: Run full test suite**

```bash
pytest tests/ -v
```

Expected: `35 passed`

- [ ] **Step 6: Commit**

```bash
git add persistence/save.py tests/test_persistence.py
git commit -m "feat: JSON save/load with round-trip fidelity"
```

---

## Task 8 — Textual App Skeleton + Layout

> **Note Textual pour débutants :** Textual est un framework TUI Python. L'`App` définit la structure via `compose()` qui yield des widgets. `on_mount()` est appelé après l'affichage initial. `set_interval(seconds, fn)` crée un timer répété. `BINDINGS` liste les raccourcis clavier. Les widgets sont des classes Python avec `render()` ou `compose()`.

**Files:**
- Create: `ui/app.py`
- Create: `ui/stats_panel.py` (stub)
- Create: `ui/world_widget.py` (stub)

- [ ] **Step 1: Create StatsPanel stub**

Créer `ui/stats_panel.py` :
```python
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static
from game.state import GameState


class StatsPanel(Widget):
    """Displays resources, population and queen stats."""

    DEFAULT_CSS = """
    StatsPanel {
        width: 35%;
        height: 100%;
        border-left: solid $primary-darken-3;
        padding: 1 2;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="resources")
        yield Static("", id="population")
        yield Static("", id="queen")

    def refresh_stats(self, state: GameState) -> None:
        self.query_one("#resources", Static).update("RESSOURCES\n(loading...)")
        self.query_one("#population", Static).update("POPULATION\n(loading...)")
        self.query_one("#queen", Static).update("REINE\n(loading...)")
```

- [ ] **Step 2: Create WorldWidget stub**

Créer `ui/world_widget.py` :
```python
from textual.widget import Widget
from game.state import GameState


class WorldWidget(Widget):
    """Displays the animated world with ants moving."""

    DEFAULT_CSS = """
    WorldWidget {
        width: 65%;
        height: 100%;
    }
    """

    def update_world(self, state: GameState) -> None:
        self.refresh()

    def render(self):
        from rich.text import Text
        return Text("🐜 World initializing...")
```

- [ ] **Step 3: Create the main App**

Créer `ui/app.py` :
```python
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Static

from game.loop import tick
from game.state import GameState
from persistence.save import load_game, save_game
from ui.stats_panel import StatsPanel
from ui.world_widget import WorldWidget


class AntColonyApp(App):
    """Ant Colony idle game."""

    CSS = """
    Screen {
        layers: base overlay;
    }
    #header-bar {
        height: 1;
        background: $primary-darken-2;
        color: $text;
        padding: 0 2;
    }
    #main-area {
        height: 1fr;
    }
    #footer-bar {
        height: 1;
        background: $primary-darken-2;
        color: $text-muted;
        padding: 0 2;
    }
    """

    BINDINGS = [
        ("u", "toggle_upgrades", "Upgrades"),
        ("f", "add_forager", "+Fourrageuse"),
        ("shift+f", "remove_forager", "-Fourrageuse"),
        ("w", "add_worker", "+Ouvrière"),
        ("shift+w", "remove_worker", "-Ouvrière"),
        ("q", "quit_game", "Quitter"),
    ]

    def __init__(self):
        super().__init__()
        self.state: GameState = load_game()

    def compose(self) -> ComposeResult:
        yield Static("🐜 ANT COLONY", id="header-bar")
        with Horizontal(id="main-area"):
            yield WorldWidget()
            yield StatsPanel()
        yield Static("[u] Upgrades  [f/F] Fourrageuses  [w/W] Ouvrières  [q] Quitter", id="footer-bar")

    def on_mount(self) -> None:
        self.set_interval(0.25, self._game_tick)
        self.set_interval(30.0, self._auto_save)

    def _game_tick(self) -> None:
        tick(self.state)
        self.query_one(StatsPanel).refresh_stats(self.state)
        self.query_one(WorldWidget).update_world(self.state)
        self._update_header()

    def _update_header(self) -> None:
        import datetime
        day = self.state.ticks // 1200 + 1
        now = datetime.datetime.now().strftime("%H:%M")
        self.query_one("#header-bar", Static).update(f"🐜 ANT COLONY   Jour {day}  |  {now}")

    def _auto_save(self) -> None:
        save_game(self.state)

    def on_unmount(self) -> None:
        save_game(self.state)

    def action_toggle_upgrades(self) -> None:
        pass  # implemented in Task 13

    def action_add_forager(self) -> None:
        if self.state.idle > 0:
            self.state.idle -= 1
            self.state.foragers += 1

    def action_remove_forager(self) -> None:
        if self.state.foragers > 0:
            self.state.foragers -= 1
            self.state.idle += 1

    def action_add_worker(self) -> None:
        if self.state.idle > 0:
            self.state.idle -= 1
            self.state.workers += 1

    def action_remove_worker(self) -> None:
        if self.state.workers > 0:
            self.state.workers -= 1
            self.state.idle += 1

    def action_quit_game(self) -> None:
        save_game(self.state)
        self.exit()
```

- [ ] **Step 4: Test the app launches**

```bash
cd /Users/matthieu.herwegh/Documents/ant-colony
python ant_colony.py
```

Expected: terminal shows "🐜 ANT COLONY" header + world area + footer bar. Press `q` to quit.

- [ ] **Step 5: Commit**

```bash
git add ui/app.py ui/stats_panel.py ui/world_widget.py ant_colony.py
git commit -m "feat: Textual app skeleton with layout, timers, key bindings"
```

---

## Task 9 — StatsPanel (Full Implementation)

**Files:**
- Modify: `ui/stats_panel.py`

- [ ] **Step 1: Implement refresh_stats with real data**

Remplacer le contenu de `ui/stats_panel.py` :
```python
from textual.widget import Widget
from textual.app import ComposeResult
from textual.widgets import Static

from game.loop import (
    CHAMPIGNONNIERE_BONUS,
    EGG_PER_TICK,
    FOOD_PER_ANT_PER_TICK,
    FOOD_PER_FORAGER_PER_TICK,
    LIFESPAN_TICKS,
)
from game.state import GameState


class StatsPanel(Widget):
    """Displays resources, population and queen stats."""

    DEFAULT_CSS = """
    StatsPanel {
        width: 35%;
        height: 100%;
        border-left: solid $primary-darken-3;
        padding: 1 2;
    }
    #resources { margin-bottom: 1; }
    #population { margin-bottom: 1; }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="resources")
        yield Static("", id="population")
        yield Static("", id="queen")

    def refresh_stats(self, state: GameState) -> None:
        self.query_one("#resources", Static).update(self._render_resources(state))
        self.query_one("#population", Static).update(self._render_population(state))
        self.query_one("#queen", Static).update(self._render_queen(state))

    # --- Renderers ---

    def _render_resources(self, state: GameState) -> str:
        food_bar = _bar(state.food, state.food_max)
        mat_bar = _bar(state.materials, state.materials_max)
        rate = _food_rate_per_min(state)
        rate_str = f"+{rate:.1f}/min ▲" if rate >= 0 else f"{rate:.1f}/min ▼ ⚠"
        return (
            "RESSOURCES\n"
            f"🍖 {food_bar}  {state.food:.0f} / {state.food_max:.0f}\n"
            f"   {rate_str}\n"
            f"🪨 {mat_bar}  {state.materials:.0f} / {state.materials_max:.0f}"
        )

    def _render_population(self, state: GameState) -> str:
        return (
            f"POPULATION  {state.population} 🐜\n"
            f"Fourrageuses  {state.foragers:3d}  [f/F]\n"
            f"Ouvrières     {state.workers:3d}  [w/W]\n"
            f"Inactives     {state.idle:3d}"
        )

    def _render_queen(self, state: GameState) -> str:
        egg_mult = 2.0 if "nurserie_renforcee" in state.upgrades else 1.0
        ticks_per_day = 1200
        births = EGG_PER_TICK * egg_mult * ticks_per_day
        deaths = (state.population / LIFESPAN_TICKS) * ticks_per_day
        trend = "▲" if births > deaths else "▼"
        egg_bar = _bar(state.eggs, 1.0)
        return (
            "REINE\n"
            f"Œufs  {egg_bar}  {state.eggs:.1f} / 1.0\n"
            f"Natalité   ~{births:.1f}/jour  {trend}\n"
            f"Mortalité  ~{deaths:.1f}/jour"
        )


# --- Helpers ---

def _bar(value: float, max_value: float, width: int = 10) -> str:
    if max_value <= 0:
        return "░" * width
    filled = min(width, int((value / max_value) * width))
    return "█" * filled + "░" * (width - filled)


def _food_rate_per_min(state: GameState) -> float:
    multiplier = 1.0
    if "pattes_renforcees" in state.upgrades:
        multiplier *= 1.2
    if "pheromones_optimisees" in state.upgrades:
        multiplier *= 1.4
    production = state.foragers * FOOD_PER_FORAGER_PER_TICK * multiplier
    if "champignonniere" in state.upgrades:
        production += CHAMPIGNONNIERE_BONUS
    consumption = state.population * FOOD_PER_ANT_PER_TICK
    ticks_per_minute = 60 / 0.25
    return (production - consumption) * ticks_per_minute
```

- [ ] **Step 2: Test visually**

```bash
python ant_colony.py
```

Expected: le panneau droit affiche RESSOURCES, POPULATION, REINE avec des barres et des chiffres qui changent. `f` ajoute une fourrageuse, `F` en retire.

- [ ] **Step 3: Commit**

```bash
git add ui/stats_panel.py
git commit -m "feat: StatsPanel with resource bars, population, and queen stats"
```

---

## Task 10 — WorldWidget Static World

**Files:**
- Modify: `ui/world_widget.py`

- [ ] **Step 1: Implement static world grid with emoji décor et nœud**

Remplacer le contenu de `ui/world_widget.py` :
```python
import random
from dataclasses import dataclass, field
from rich.text import Text
from textual.widget import Widget

from game.state import GameState

DECOR_EMOJIS = ["🍃", "🌿", "🍄"]
NEST_CHAR = "▼NŒUD"
GROUND_CHAR = "═"


@dataclass
class FoodSource:
    x: int
    y: int
    emoji: str


@dataclass
class CosmeticAnt:
    x: float
    y: float
    source_index: int       # which FoodSource this ant targets
    going_to_food: bool     # True = heading to food, False = returning
    row_offset: int         # ±1 for sinuous path
    speed: float            # columns per tick
    slow: bool = False      # True when starving


class WorldWidget(Widget):
    """Displays the animated world with ants moving between nest and food."""

    DEFAULT_CSS = """
    WorldWidget {
        width: 65%;
        height: 100%;
    }
    """

    def __init__(self):
        super().__init__()
        self._initialized = False
        self._food_sources: list[FoodSource] = []
        self._ants: list[CosmeticAnt] = []
        self._pheromones: dict[tuple[int, int], int] = {}  # (x,y) → ttl
        self._nest_x: int = 0
        self._nest_y: int = 0
        self._width: int = 80
        self._height: int = 24

    def on_mount(self) -> None:
        self._width = self.size.width
        self._height = self.size.height
        self._initialize_world()

    def _initialize_world(self) -> None:
        w, h = self._width, self._height
        self._nest_x = w // 2
        self._nest_y = h - 3  # ground line position

        # Place 3 food sources in upper half, spread across width
        positions = [w // 5, w // 2, 4 * w // 5]
        for px in positions:
            self._food_sources.append(FoodSource(
                x=px,
                y=random.randint(2, h // 3),
                emoji=random.choice(DECOR_EMOJIS),
            ))

        self._initialized = True

    def update_world(self, state: GameState) -> None:
        if not self._initialized:
            return
        self._sync_ant_count(state)
        self._move_ants(state)
        self._decay_pheromones()
        self.refresh()

    def _sync_ant_count(self, state: GameState) -> None:
        """Cosmetically match visible ant count to ~foragers/8, min 1, max 12."""
        target = max(1, min(12, state.foragers // 8 + 1))
        while len(self._ants) < target:
            self._spawn_ant()
        while len(self._ants) > target:
            self._ants.pop()

    def _spawn_ant(self) -> None:
        source_idx = random.randint(0, len(self._food_sources) - 1)
        self._ants.append(CosmeticAnt(
            x=float(self._nest_x),
            y=float(self._nest_y - 1),
            source_index=source_idx,
            going_to_food=True,
            row_offset=random.choice([-1, 0, 1]),
            speed=random.uniform(0.8, 1.4),
        ))

    def _move_ants(self, state: GameState) -> None:
        starving = state.food <= 0
        for ant in self._ants:
            ant.slow = starving
            if starving and state.ticks % 2 != 0:
                continue  # move every 2 ticks when starving

            source = self._food_sources[ant.source_index]
            if ant.going_to_food:
                target_x = float(source.x)
            else:
                target_x = float(self._nest_x)

            dx = target_x - ant.x
            if abs(dx) < ant.speed:
                ant.x = target_x
                ant.going_to_food = not ant.going_to_food
                ant.row_offset = random.choice([-1, 0, 1])
            else:
                ant.x += ant.speed if dx > 0 else -ant.speed

            # Leave pheromone
            px, py = int(ant.x), int(ant.y) + ant.row_offset
            if 0 <= px < self._width and 0 <= py < self._height:
                self._pheromones[(px, py)] = random.randint(3, 6)

    def _decay_pheromones(self) -> None:
        self._pheromones = {
            pos: ttl - 1
            for pos, ttl in self._pheromones.items()
            if ttl > 1
        }

    def render(self) -> Text:
        if not self._initialized:
            return Text("Initialisation...")

        w, h = self._width, self._height
        # Build grid: list of list of (char, style)
        grid: list[list[tuple[str, str]]] = [
            [(" ", "") for _ in range(w)]
            for _ in range(h)
        ]

        # Ground line
        ground_y = self._nest_y
        for x in range(w):
            grid[ground_y][x] = (GROUND_CHAR, "dim")

        # Nest marker
        nest_label = f"[{NEST_CHAR}]"
        start = max(0, self._nest_x - len(nest_label) // 2)
        for i, ch in enumerate(nest_label):
            if start + i < w:
                grid[ground_y][start + i] = (ch, "bold green")

        # Food sources (emoji — takes 2 cols, place carefully)
        for src in self._food_sources:
            if 0 <= src.y < h and 0 <= src.x < w - 1:
                grid[src.y][src.x] = (src.emoji, "")
                if src.x + 1 < w:
                    grid[src.y][src.x + 1] = (" ", "")  # emoji width padding

        # Pheromones
        for (px, py), _ttl in self._pheromones.items():
            if 0 <= py < h and 0 <= px < w:
                if grid[py][px][0] == " ":
                    grid[py][px] = ("·", "dim green")

        # Ants
        for ant in self._ants:
            ax = int(ant.x)
            ay = min(self._nest_y - 1, max(0, self._nest_y - 1 + ant.row_offset))
            if 0 <= ay < h and 0 <= ax < w:
                char = "a" if ant.going_to_food else "A"
                style = "bold yellow" if not ant.going_to_food else "yellow"
                grid[ay][ax] = (char, style)

        # Build Rich Text
        text = Text()
        for row in grid:
            for char, style in row:
                if style:
                    text.append(char, style)
                else:
                    text.append(char)
            text.append("\n")
        return text
```

- [ ] **Step 2: Test visually**

```bash
python ant_colony.py
```

Expected: la zone gauche affiche une ligne de sol `═══[▼NŒUD]═══`, des emoji `🍄 🍃 🌿` dans la zone supérieure, des fourmis `a`/`A` qui bougent entre le nœud et les sources.

- [ ] **Step 3: Commit**

```bash
git add ui/world_widget.py
git commit -m "feat: WorldWidget with ant animation, pheromone trails, emoji decor"
```

---

## Task 11 — UpgradeOverlay

**Files:**
- Create: `ui/upgrade_overlay.py`
- Modify: `ui/app.py` (action_toggle_upgrades)

- [ ] **Step 1: Create UpgradeOverlay**

Créer `ui/upgrade_overlay.py` :
```python
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static
from textual.binding import Binding

from game.state import GameState
from game.upgrades import UPGRADE_ORDER, UPGRADES, buy_upgrade, is_available


class UpgradeOverlay(ModalScreen):
    """Modal screen for browsing and purchasing upgrades."""

    CSS = """
    UpgradeOverlay {
        align: center middle;
    }
    #upgrade-box {
        width: 45;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 1 2;
    }
    """

    BINDINGS = [
        Binding("up", "cursor_up", "Monter"),
        Binding("down", "cursor_down", "Descendre"),
        Binding("enter", "purchase", "Acheter"),
        Binding("escape", "close", "Fermer"),
        Binding("u", "close", "Fermer"),
    ]

    def __init__(self, state: GameState):
        super().__init__()
        self._state = state
        self._cursor = 0  # index into UPGRADE_ORDER

    def compose(self) -> ComposeResult:
        with self.app.query_one.__class__:
            pass
        from textual.containers import Vertical
        with Vertical(id="upgrade-box"):
            yield Static("", id="upgrade-list")

    def on_mount(self) -> None:
        self._refresh_list()

    def _refresh_list(self) -> None:
        lines = [f"UPGRADES   💰 {self._state.food:.0f}\n"]
        for i, uid in enumerate(UPGRADE_ORDER):
            upgrade = UPGRADES[uid]
            if uid in self._state.upgrades:
                prefix = "✅"
                suffix = "(acheté)"
            elif is_available(uid, self._state):
                prefix = "▶" if i == self._cursor else " "
                suffix = f"${upgrade['cost']}"
            else:
                prefix = " "
                suffix = f"${upgrade['cost']}  🔒"

            cursor_mark = ">" if i == self._cursor else " "
            lines.append(f"{cursor_mark} {prefix} {upgrade['name']:<22} {suffix}")

        lines.append("\n[↑↓] Naviguer  [Entrée] Acheter  [Esc] Fermer")
        self.query_one("#upgrade-list", Static).update("\n".join(lines))

    def action_cursor_up(self) -> None:
        self._cursor = max(0, self._cursor - 1)
        self._refresh_list()

    def action_cursor_down(self) -> None:
        self._cursor = min(len(UPGRADE_ORDER) - 1, self._cursor + 1)
        self._refresh_list()

    def action_purchase(self) -> None:
        uid = UPGRADE_ORDER[self._cursor]
        buy_upgrade(uid, self._state)
        self._refresh_list()

    def action_close(self) -> None:
        self.dismiss()
```

- [ ] **Step 2: Wire into app.py**

Dans `ui/app.py`, remplacer :
```python
    def action_toggle_upgrades(self) -> None:
        pass  # implemented in Task 13
```

Par :
```python
    def action_toggle_upgrades(self) -> None:
        from ui.upgrade_overlay import UpgradeOverlay
        self.push_screen(UpgradeOverlay(self.state))
```

- [ ] **Step 3: Test visually**

```bash
python ant_colony.py
```

Appuyer sur `u` : l'overlay upgrades s'affiche au centre. `↑↓` naviguent, `Entrée` achète si assez de nourriture, `Esc` ferme.

- [ ] **Step 4: Commit**

```bash
git add ui/upgrade_overlay.py ui/app.py
git commit -m "feat: upgrade overlay with keyboard navigation and purchase"
```

---

## Task 12 — Final Integration + Polish

**Files:**
- Modify: `ui/app.py` (titre dynamique + polish)
- Modify: `ui/world_widget.py` (fix potential on_resize)

- [ ] **Step 1: Handle terminal resize in WorldWidget**

Ajouter dans `ui/world_widget.py`, dans la classe `WorldWidget` :
```python
    def on_resize(self, event) -> None:
        self._width = event.size.width
        self._height = event.size.height
        self._food_sources.clear()
        self._ants.clear()
        self._pheromones.clear()
        self._initialize_world()
```

- [ ] **Step 2: Run full test suite to confirm nothing broke**

```bash
pytest tests/ -v
```

Expected: `35 passed`

- [ ] **Step 3: Smoke test — play for 2 minutes**

```bash
python ant_colony.py
```

Vérifier :
- Les fourmis bougent continuellement
- Les ressources évoluent
- `f`/`F`/`w`/`W` réassignent les fourmis
- `u` ouvre l'overlay upgrades
- `q` quitte et sauvegarde
- Relancer → l'état est restauré

- [ ] **Step 4: Final commit**

```bash
git add ui/world_widget.py
git commit -m "feat: handle terminal resize in WorldWidget"
```

---

## Self-Review Against Spec

| Spec requirement | Covered by task |
|-----------------|-----------------|
| GameState dataclass | Task 2 |
| Production tick (food, materials, eggs) | Task 3 |
| Food consumption + starvation death | Task 4 |
| Natural death (probabilistic) | Task 5 |
| Egg hatching | Task 5 |
| tick() orchestrator | Task 5 |
| 6 upgrades with tier gating | Task 6 |
| Upgrade effects (food_max×2, materials_max×2, multipliers) | Task 6 |
| JSON save/load | Task 7 |
| Autosave 30s + on quit | Task 8 |
| Layout: 65% world / 35% stats | Task 8 |
| Header with day + time | Task 8 |
| StatsPanel: resource bars + food rate | Task 9 |
| StatsPanel: population + [f/F/w/W] | Task 9 |
| StatsPanel: queen eggs + birth/death trend | Task 9 |
| WorldWidget: emoji decor (static) | Task 10 |
| WorldWidget: ant animation a/A | Task 10 |
| WorldWidget: pheromone trails | Task 10 |
| WorldWidget: ants slow when starving | Task 10 |
| UpgradeOverlay: list + navigation + purchase | Task 11 |
| Resize handling | Task 12 |
| Pause on close (no offline gains) | Built-in — ticks only increment when app runs |
