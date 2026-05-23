import pytest
import yaml
import os
from pathlib import Path

from research_os.tools.actions.config import (
    init_config,
    get_config,
    set_config,
    validate_config,
)


@pytest.fixture
def tmp_root(tmp_path):
    return tmp_path


@pytest.fixture
def initialised_root(tmp_root):
    result = init_config(tmp_root)
    assert result["status"] == "success"
    return tmp_root


class TestInitConfig:
    def test_creates_config_file(self, tmp_root):
        result = init_config(tmp_root)
        assert result["status"] == "success"
        config_path = tmp_root / "inputs" / "researcher_config.yaml"
        assert config_path.exists()

    def test_creates_default_structure(self, tmp_root):
        init_config(tmp_root)
        config_path = tmp_root / "inputs" / "researcher_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert "researcher" in config
        assert "interaction" in config
        assert "api_keys" in config
        assert "model_profile" in config
        assert config["model_profile"] == "medium"

    def test_idempotent_when_already_exists(self, tmp_root):
        init_config(tmp_root)
        result = init_config(tmp_root)
        assert result["status"] == "success"
        assert result["message"] == "Config already exists."

    def test_restricts_permissions(self, tmp_root):
        init_config(tmp_root)
        config_path = tmp_root / "inputs" / "researcher_config.yaml"
        mode = os.stat(config_path).st_mode & 0o777
        if os.name != "nt":
            assert mode == 0o600


class TestGetConfig:
    def test_returns_config(self, initialised_root):
        result = get_config(initialised_root)
        assert result["status"] == "success"
        assert "config" in result
        assert result["config"]["model_profile"] == "medium"

    def test_masks_api_keys(self, initialised_root):
        set_config("api_keys.openai", "sk-1234567890abcdef", initialised_root)
        set_config("api_keys.firecrawl", "fc-abcdef123456", initialised_root)
        result = get_config(initialised_root)
        api_keys = result["config"]["api_keys"]
        assert "..." in api_keys["openai"]
        assert "..." in api_keys["firecrawl"]

    def test_error_when_config_missing(self, tmp_root):
        result = get_config(tmp_root)
        assert result["status"] == "error"
        assert result["message"] == "Config not found"


class TestSetConfig:
    def test_sets_simple_value(self, initialised_root):
        result = set_config("model_profile", "large", initialised_root)
        assert result["status"] == "success"
        config_path = initialised_root / "inputs" / "researcher_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config["model_profile"] == "large"

    def test_sets_nested_value(self, initialised_root):
        result = set_config("researcher.name", "Dr. Smith", initialised_root)
        assert result["status"] == "success"
        config_path = initialised_root / "inputs" / "researcher_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config["researcher"]["name"] == "Dr. Smith"

    def test_creates_new_nested_path(self, initialised_root):
        result = set_config("custom.nested.key", "value", initialised_root)
        assert result["status"] == "success"
        config_path = initialised_root / "inputs" / "researcher_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config["custom"]["nested"]["key"] == "value"

    def test_updates_existing_value(self, initialised_root):
        set_config("model_profile", "small", initialised_root)
        set_config("model_profile", "large", initialised_root)
        config_path = initialised_root / "inputs" / "researcher_config.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)
        assert config["model_profile"] == "large"

    def test_get_reflects_set(self, initialised_root):
        set_config("researcher.name", "Alice", initialised_root)
        result = get_config(initialised_root)
        assert result["config"]["researcher"]["name"] == "Alice"


class TestValidateConfig:
    def test_returns_validations(self, initialised_root):
        result = validate_config(initialised_root)
        assert result["status"] == "success"
        assert "validations" in result

    def test_reports_missing_api_key(self, initialised_root):
        result = validate_config(initialised_root)
        assert any("Missing" in v for v in result["validations"])

    def test_reports_present_api_key(self, initialised_root):
        set_config("api_keys.firecrawl", "fc-valid-key", initialised_root)
        result = validate_config(initialised_root)
        assert any("Present" in v for v in result["validations"])

    def test_error_when_no_config(self, tmp_root):
        result = validate_config(tmp_root)
        assert result["status"] == "error"


class TestErrorHandling:
    def test_get_config_missing_directory(self, tmp_root):
        result = get_config(tmp_root)
        assert result["status"] == "error"

    def test_set_config_new_file_creates_it(self, tmp_root):
        result = set_config("new.key", "value", tmp_root)
        assert result["status"] == "success"
        assert (tmp_root / "inputs" / "researcher_config.yaml").exists()
