from game.state import GameState

def test_initial_values():
    state = GameState()
    assert state.food == 50.0
    assert state.food_max == 500.0
    assert state.materials == 20.0
    assert state.materials_max == 300.0
    assert state.population == 10
    assert state.foragers == 5
    assert state.workers == 4
    assert state.idle == 1
    assert state.eggs == 0.0
    assert state.upgrades == set()
    assert state.ticks == 0
    assert state.starvation_ticks == 0

def test_population_is_consistent():
    state = GameState()
    assert state.foragers + state.workers + state.idle == state.population
