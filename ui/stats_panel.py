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
