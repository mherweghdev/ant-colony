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
