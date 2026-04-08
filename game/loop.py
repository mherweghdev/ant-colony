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
    """Calculate production multiplier based on upgrades."""
    multiplier = 1.0
    if "pattes_renforcees" in state.upgrades:
        multiplier *= 1.2
    if "pheromones_optimisees" in state.upgrades:
        multiplier *= 1.4
    return multiplier
