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
