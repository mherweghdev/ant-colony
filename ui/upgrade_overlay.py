from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.widgets import Static
from textual.binding import Binding
from textual.containers import Vertical

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
        Binding("escape", "close_overlay", "Fermer"),
        Binding("u", "close_overlay", "Fermer"),
    ]

    def __init__(self, state: GameState):
        super().__init__()
        self._state = state
        self._cursor = 0  # index into UPGRADE_ORDER

    def compose(self) -> ComposeResult:
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

    def action_close_overlay(self) -> None:
        self.dismiss()
