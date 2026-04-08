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
