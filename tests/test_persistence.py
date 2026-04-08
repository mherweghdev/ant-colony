import json
from pathlib import Path
import pytest
from game.state import GameState
from persistence.save import save_game, load_game


@pytest.fixture
def tmp_save_path(tmp_path, monkeypatch):
    save_file = tmp_path / "save.json"
    monkeypatch.setattr("persistence.save.SAVE_PATH", save_file)
    return save_file


def test_save_creates_file(tmp_save_path):
    state = GameState()
    save_game(state)
    assert tmp_save_path.exists()


def test_round_trip_preserves_values(tmp_save_path):
    state = GameState(
        food=123.4,
        food_max=1000.0,
        materials=56.7,
        materials_max=600.0,
        population=25,
        foragers=12,
        workers=10,
        idle=3,
        eggs=0.7,
        upgrades={"garde_manger", "pattes_renforcees"},
        ticks=9999,
    )
    save_game(state)
    loaded = load_game()
    assert abs(loaded.food - 123.4) < 0.001
    assert loaded.food_max == 1000.0
    assert loaded.population == 25
    assert loaded.foragers == 12
    assert loaded.upgrades == {"garde_manger", "pattes_renforcees"}
    assert loaded.ticks == 9999


def test_load_returns_default_when_no_file(tmp_save_path):
    assert not tmp_save_path.exists()
    state = load_game()
    assert state.food == 50.0
    assert state.population == 10
