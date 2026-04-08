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
