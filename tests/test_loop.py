from game.state import GameState
from game.loop import tick_production


def test_food_increases_with_foragers():
    state = GameState(food=50.0, foragers=5, upgrades=set())
    tick_production(state)
    # 5 foragers × 0.05 = 0.25
    assert abs(state.food - 50.25) < 0.001


def test_materials_increase_with_workers():
    state = GameState(materials=20.0, workers=4)
    tick_production(state)
    # 4 workers × 0.03 = 0.12
    assert abs(state.materials - 20.12) < 0.001


def test_food_capped_at_food_max():
    state = GameState(food=499.9, food_max=500.0, foragers=10)
    tick_production(state)
    assert state.food == 500.0


def test_eggs_accumulate():
    state = GameState(eggs=0.0, food=100.0)
    tick_production(state)
    assert abs(state.eggs - 0.01) < 0.001


def test_eggs_dont_accumulate_when_starving():
    state = GameState(eggs=0.5, food=0.0, foragers=0, workers=0)
    tick_production(state)
    assert state.eggs == 0.5


def test_pattes_renforcees_multiplier():
    state = GameState(food=0.0, foragers=10, upgrades={"pattes_renforcees"})
    tick_production(state)
    # 10 × 0.05 × 1.2 = 0.6
    assert abs(state.food - 0.6) < 0.001


def test_champignonniere_passive_food():
    state = GameState(food=0.0, foragers=0, upgrades={"champignonniere"})
    tick_production(state)
    assert abs(state.food - 0.5) < 0.001


def test_pheromones_optimisees_multiplier():
    state = GameState(food=0.0, foragers=10, upgrades={"pheromones_optimisees"})
    tick_production(state)
    # 10 × 0.05 × 1.4 = 0.7
    assert abs(state.food - 0.7) < 0.001


def test_combined_multipliers():
    state = GameState(food=0.0, foragers=10, upgrades={"pattes_renforcees", "pheromones_optimisees"})
    tick_production(state)
    # 10 × 0.05 × 1.2 × 1.4 = 0.84
    assert abs(state.food - 0.84) < 0.001


def test_nurserie_renforcee_egg_multiplier():
    state = GameState(eggs=0.0, food=100.0, upgrades={"nurserie_renforcee"})
    tick_production(state)
    # 0.01 × 2.0 = 0.02
    assert abs(state.eggs - 0.02) < 0.001


def test_materials_capped_at_materials_max():
    state = GameState(materials=299.9, materials_max=300.0, workers=10)
    tick_production(state)
    assert state.materials == 300.0


from game.loop import tick_consumption


def test_food_decreases_with_population():
    state = GameState(food=50.0, population=10)
    tick_consumption(state)
    # 10 ants × 0.01 = 0.1
    assert abs(state.food - 49.9) < 0.001


def test_food_never_below_zero():
    state = GameState(food=0.05, population=100)
    tick_consumption(state)
    assert state.food == 0.0


def test_starvation_counter_increments_when_no_food():
    state = GameState(food=0.0, population=5)
    tick_consumption(state)
    assert state.starvation_ticks == 1


def test_starvation_counter_resets_when_fed():
    state = GameState(food=10.0, population=5, starvation_ticks=5)
    tick_consumption(state)
    assert state.starvation_ticks == 0


def test_ant_dies_after_starvation_delay():
    # STARVATION_DELAY_TICKS = 20
    state = GameState(food=0.0, population=5, foragers=3, workers=1, idle=1, starvation_ticks=19)
    tick_consumption(state)
    assert state.population == 4
    assert state.starvation_ticks == 0


def test_idle_ant_dies_first_during_starvation():
    state = GameState(food=0.0, population=5, foragers=3, workers=1, idle=1, starvation_ticks=19)
    tick_consumption(state)
    assert state.idle == 0
    assert state.foragers == 3


def test_forager_dies_when_no_idle():
    state = GameState(food=0.0, population=4, foragers=3, workers=1, idle=0, starvation_ticks=19)
    tick_consumption(state)
    assert state.foragers == 2
    assert state.population == 3


def test_no_death_if_only_one_ant():
    state = GameState(food=0.0, population=1, foragers=0, workers=0, idle=1, starvation_ticks=19)
    tick_consumption(state)
    assert state.population == 1


from unittest.mock import patch
from game.loop import tick_aging, tick_hatching, tick


def test_hatching_adds_idle_ant():
    state = GameState(eggs=1.0, population=10, idle=1)
    tick_hatching(state)
    assert state.eggs == 0.0
    assert state.population == 11
    assert state.idle == 2


def test_no_hatch_below_threshold():
    state = GameState(eggs=0.9, population=10, idle=1)
    tick_hatching(state)
    assert state.population == 10
    assert abs(state.eggs - 0.9) < 0.001


def test_natural_death_occurs_probabilistically():
    # With population=36000, probability per tick = 1.0 → always dies
    state = GameState(population=36000, foragers=20000, workers=15000, idle=1000)
    with patch("random.random", return_value=0.0):  # 0.0 < 1.0 → always triggers
        tick_aging(state)
    assert state.population == 35999


def test_no_death_at_zero_population():
    state = GameState(population=0, foragers=0, workers=0, idle=0)
    tick_aging(state)
    assert state.population == 0


def test_tick_increments_ticks_counter():
    state = GameState()
    tick(state)
    assert state.ticks == 1


def test_tick_calls_all_phases():
    state = GameState(food=100.0, foragers=5, workers=4, population=10)
    initial_food = state.food
    tick(state)
    # Food changed = production ran, consumption ran
    assert state.food != initial_food
