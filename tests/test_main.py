import os
import json
import shutil
import pytest

import main

@pytest.fixture(autouse=True)
def chdir_tmp_path(tmp_path, monkeypatch):
    # chaque test s'exécute dans un répertoire temporaire vide
    monkeypatch.chdir(tmp_path)
    yield

def test_ensure_config_creates_file_and_dir(tmp_path):
    # Au départ, data/ n'existe pas
    assert not os.path.exists("data/config.json")

    # Appel
    main.ensure_config_file()

    # Vérifie la création
    assert os.path.isdir("data")
    assert os.path.isfile("data/config.json")

    # Le contenu doit correspondre à DEFAULT_CONFIG
    cfg = json.loads((tmp_path / "data" / "config.json").read_text())
    assert cfg == main.DEFAULT_CONFIG

def test_validate_config_accepts_default():
    # DEFAULT_CONFIG doit être valide
    assert main.validate_config(main.DEFAULT_CONFIG) is True

@pytest.mark.parametrize("bad_cfg", [
    {},  # vide
    {"symbols": [], "indicators": {}, "alerts": {}},
    {"symbols": ["A"], "indicators": [], "alerts": {}},
    {"symbols": ["A"], "indicators": {"rsi":"14","ema":[],"bollinger":{}}, "alerts": {}},
    {"symbols": ["A"], "indicators": {"rsi":14,"ema":[],"bollinger":{"window":5}}, "alerts": {}},
    {"symbols": ["A"], "indicators": {"rsi":14,"ema":[],"bollinger":{"window":5,"std":2}}, "alerts": []},
])
def test_validate_config_rejects(bad_cfg):
    assert main.validate_config(bad_cfg) is False

def test_load_and_validate_config_creates_and_loads(tmp_path, monkeypatch):
    # simulate empty workspace
    monkeypatch.chdir(tmp_path)
    shutil.rmtree(tmp_path / "data", ignore_errors=True)

    # Should create then load without error
    cfg = main.load_and_validate_config()
    assert cfg == main.DEFAULT_CONFIG

def test_load_and_validate_config_fails_on_invalid(monkeypatch, tmp_path):
    # place a bad config.json
    monkeypatch.chdir(tmp_path)
    os.makedirs("data", exist_ok=True)
    with open("data/config.json","w") as f:
        json.dump({"symbols":[], "indicators":{}, "alerts":{}}, f)

    # load_and_validate_config doit sys.exit(1)
    with pytest.raises(SystemExit):
        main.load_and_validate_config()
