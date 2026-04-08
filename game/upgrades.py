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
        t1_bought = sum(
            1 for uid in UPGRADES if UPGRADES[uid]["tier"] == 1 and uid in state.upgrades
        )
        return t1_bought >= 1
    if tier == 3:
        t2_bought = sum(
            1 for uid in UPGRADES if UPGRADES[uid]["tier"] == 2 and uid in state.upgrades
        )
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
    """Apply immediate effects of an upgrade."""
    if upgrade_id == "garde_manger":
        state.food_max *= 2
    elif upgrade_id == "chambre_stockage":
        state.materials_max *= 2
    # pattes_renforcees, pheromones_optimisees, nurserie_renforcee, champignonniere:
    # effects are applied dynamically in game/loop.py via upgrades set
