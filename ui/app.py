from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static

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
        pass  # implemented in Task 11

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
