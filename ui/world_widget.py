import random
from dataclasses import dataclass
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
        self._pheromones: dict[tuple, int] = {}  # (x,y) → ttl
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
                y=random.randint(2, max(3, h // 3)),
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
        source_idx = random.randint(0, max(0, len(self._food_sources) - 1))
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
            target_x = float(source.x) if ant.going_to_food else float(self._nest_x)

            dx = target_x - ant.x
            if abs(dx) < ant.speed:
                ant.x = target_x
                ant.going_to_food = not ant.going_to_food
                ant.row_offset = random.choice([-1, 0, 1])
            else:
                ant.x += ant.speed if dx > 0 else -ant.speed

            # Leave pheromone
            px, py = int(ant.x), self._nest_y - 1 + ant.row_offset
            if 0 <= px < self._width and 0 <= py < self._height:
                self._pheromones[(px, py)] = random.randint(3, 6)

    def _decay_pheromones(self) -> None:
        self._pheromones = {
            pos: ttl - 1
            for pos, ttl in self._pheromones.items()
            if ttl > 1
        }

    def on_resize(self, event) -> None:
        self._width = event.size.width
        self._height = event.size.height
        self._food_sources.clear()
        self._ants.clear()
        self._pheromones.clear()
        self._initialize_world()

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

        # Nest marker centred on nest_x
        nest_label = f"[{NEST_CHAR}]"
        start = max(0, self._nest_x - len(nest_label) // 2)
        for i, ch in enumerate(nest_label):
            if start + i < w:
                grid[ground_y][start + i] = (ch, "bold green")

        # Food sources (emoji occupies 2 columns — place with padding)
        for src in self._food_sources:
            if 0 <= src.y < ground_y and 0 <= src.x < w - 1:
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
            ay = min(ground_y - 1, max(0, self._nest_y - 1 + ant.row_offset))
            if 0 <= ay < h and 0 <= ax < w:
                char = "a" if ant.going_to_food else "A"
                style = "yellow" if ant.going_to_food else "bold yellow"
                grid[ay][ax] = (char, style)

        # Build Rich Text row by row
        text = Text()
        for row in grid:
            for char, style in row:
                if style:
                    text.append(char, style)
                else:
                    text.append(char)
            text.append("\n")
        return text
