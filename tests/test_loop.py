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
