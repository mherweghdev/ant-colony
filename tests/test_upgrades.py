from game.state import GameState
from game.upgrades import is_available, buy_upgrade, UPGRADES


def test_tier1_always_available():
    state = GameState()
    assert is_available("garde_manger", state) is True
    assert is_available("pattes_renforcees", state) is True


def test_tier2_locked_without_tier1():
    state = GameState()
    assert is_available("pheromones_optimisees", state) is False
    assert is_available("chambre_stockage", state) is False


def test_tier2_unlocked_after_one_tier1():
    state = GameState(upgrades={"garde_manger"})
    assert is_available("pheromones_optimisees", state) is True


def test_tier3_locked_without_two_tier2():
    state = GameState(upgrades={"garde_manger", "pheromones_optimisees"})
    assert is_available("nurserie_renforcee", state) is False


def test_tier3_unlocked_after_two_tier2():
    state = GameState(upgrades={"pheromones_optimisees", "chambre_stockage"})
    assert is_available("nurserie_renforcee", state) is True


def test_already_bought_not_available():
    state = GameState(upgrades={"garde_manger"})
    assert is_available("garde_manger", state) is False


def test_buy_upgrade_deducts_food():
    state = GameState(food=300.0, upgrades=set())
    result = buy_upgrade("garde_manger", state)
    assert result is True
    assert state.food == 100.0  # 300 - 200


def test_buy_upgrade_fails_insufficient_food():
    state = GameState(food=100.0, upgrades=set())
    result = buy_upgrade("garde_manger", state)
    assert result is False
    assert state.food == 100.0


def test_garde_manger_doubles_food_max():
    state = GameState(food=300.0, food_max=500.0)
    buy_upgrade("garde_manger", state)
    assert state.food_max == 1000.0


def test_chambre_stockage_doubles_materials_max():
    state = GameState(food=600.0, materials_max=300.0, upgrades={"garde_manger"})
    buy_upgrade("chambre_stockage", state)
    assert state.materials_max == 600.0
