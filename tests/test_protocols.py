import pytest
from pathlib import Path
import yaml
from research_os.tools.actions.protocol import (
    get_protocol,
    list_protocols,
    validate_protocol,
    _PROTOCOL_CACHE,
)


SAMPLE_PROTOCOL = {
    "name": "test_protocol",
    "version": "1.0.0",
    "description": "A test protocol",
    "steps": [
        {"id": "step_one", "name": "Step One", "description": "First step"},
    ],
}

SAMPLE_LIGHT_PROTOCOL = {
    "name": "test_protocol",
    "version": "1.0.0",
    "steps": [
        {"id": "step_one", "name": "Step One", "description": "First step"},
    ],
}

INVALID_YAML = "name: test\nunclosed_block:\n  key: value\n  another:"


@pytest.fixture
def protocol_dir(tmp_path):
    p = tmp_path / "src" / "research_os" / "protocols"
    p.mkdir(parents=True)
    return p


@pytest.fixture
def full_protocol_dir(protocol_dir):
    light_dir = protocol_dir / "light"
    light_dir.mkdir(exist_ok=True)
    protocols = ["alpha", "beta", "gamma"]
    for name in protocols:
        data = {
            "name": name,
            "version": "2.0.0",
            "description": f"Protocol for {name}",
            "steps": [
                {"id": f"{name}_step1", "name": "Step 1", "description": "First step"},
                {"id": f"{name}_step2", "name": "Step 2", "description": "Second step"},
            ],
        }
        (protocol_dir / f"{name}.yaml").write_text(yaml.dump(data))
        light_data = {
            "name": name,
            "version": "2.0.0",
            "steps": [
                {"id": f"{name}_step1", "name": "Step 1", "description": "First step"},
            ],
        }
        (light_dir / f"{name}.yaml").write_text(yaml.dump(light_data))
    return protocol_dir


@pytest.fixture(autouse=True)
def clear_cache():
    _PROTOCOL_CACHE.clear()


class TestProtocolLoading:
    def test_load_valid_protocol(self, protocol_dir):
        pfile = protocol_dir / "test.yaml"
        pfile.write_text(yaml.dump(SAMPLE_PROTOCOL))
        result = get_protocol("test", protocol_dir.parent.parent.parent)
        assert "error" not in result
        assert "content" in result
        loaded = yaml.safe_load(result["content"])
        assert loaded["name"] == "test_protocol"

    def test_load_nonexistent_protocol_returns_error(self, protocol_dir):
        result = get_protocol("nonexistent", protocol_dir.parent.parent.parent)
        assert "error" in result
        assert result["error"] == "Protocol not found"

    def test_load_missing_yaml_returns_error(self, protocol_dir):
        result = get_protocol("", protocol_dir.parent.parent.parent)
        assert "error" in result

    def test_cache_hits_return_same_data(self, protocol_dir):
        pfile = protocol_dir / "cached.yaml"
        pfile.write_text(yaml.dump(SAMPLE_PROTOCOL))
        root = protocol_dir.parent.parent.parent
        first = get_protocol("cached", root)
        second = get_protocol("cached", root)
        assert first == second


class TestProtocolList:
    def test_list_all_protocols(self, full_protocol_dir):
        root = full_protocol_dir.parent.parent.parent
        result = list_protocols(root)
        assert "protocols" in result
        names = {p["name"] for p in result["protocols"]}
        assert names == {"alpha", "beta", "gamma"}

    def test_list_missing_dir_returns_error(self, tmp_path):
        result = list_protocols(tmp_path)
        assert "error" in result

    def test_list_protocols_have_required_metadata(self, full_protocol_dir):
        root = full_protocol_dir.parent.parent.parent
        result = list_protocols(root)
        for p in result["protocols"]:
            assert "name" in p
            assert "description" in p
            assert "version" in p


class TestProtocolFields:
    REQUIRED_FIELDS = {"name", "version", "description", "steps"}

    def test_each_protocol_has_required_fields(self, full_protocol_dir):
        root = full_protocol_dir.parent.parent.parent
        result = list_protocols(root)
        for entry in result["protocols"]:
            loaded = yaml.safe_load(
                (full_protocol_dir / f"{entry['name']}.yaml").read_text()
            )
            for field in self.REQUIRED_FIELDS:
                assert field in loaded, (
                    f"Protocol '{entry['name']}' missing field '{field}'"
                )

    def test_description_is_non_empty(self, full_protocol_dir):
        root = full_protocol_dir.parent.parent.parent
        result = list_protocols(root)
        for entry in result["protocols"]:
            assert entry["description"], (
                f"Protocol '{entry['name']}' has empty description"
            )

    def test_steps_is_a_list(self, full_protocol_dir):
        root = full_protocol_dir.parent.parent.parent
        for entry in list_protocols(root)["protocols"]:
            loaded = yaml.safe_load(
                (full_protocol_dir / f"{entry['name']}.yaml").read_text()
            )
            assert isinstance(loaded["steps"], list)
            assert len(loaded["steps"]) > 0

    def test_each_step_has_id_name_description(self, full_protocol_dir):
        root = full_protocol_dir.parent.parent.parent
        for entry in list_protocols(root)["protocols"]:
            loaded = yaml.safe_load(
                (full_protocol_dir / f"{entry['name']}.yaml").read_text()
            )
            for step in loaded["steps"]:
                assert "id" in step
                assert "name" in step
                assert "description" in step


class TestLightVariants:
    def test_every_protocol_has_light_variant(self, full_protocol_dir):
        light_dir = full_protocol_dir / "light"
        for p in full_protocol_dir.glob("*.yaml"):
            name = p.stem
            light_file = light_dir / f"{name}.yaml"
            assert light_file.exists(), f"Protocol '{name}' missing light variant"

    def test_light_variant_is_valid_yaml(self, full_protocol_dir):
        light_dir = full_protocol_dir / "light"
        for p in light_dir.glob("*.yaml"):
            data = yaml.safe_load(p.read_text())
            assert data is not None

    def test_light_variant_has_name_and_version(self, full_protocol_dir):
        light_dir = full_protocol_dir / "light"
        for p in light_dir.glob("*.yaml"):
            data = yaml.safe_load(p.read_text())
            assert "name" in data
            assert "version" in data


class TestProtocolValidation:
    def test_validate_existing_protocol(self, protocol_dir):
        (protocol_dir / "validate_me.yaml").write_text(yaml.dump(SAMPLE_PROTOCOL))
        root = protocol_dir.parent.parent.parent
        result = validate_protocol("validate_me", root)
        assert "error" not in result
        assert result["protocol"] == "validate_me"
        assert "status" in result
        assert "checklist" in result

    def test_validate_nonexistent_protocol_returns_error(self, protocol_dir):
        root = protocol_dir.parent.parent.parent
        result = validate_protocol("ghost", root)
        assert "error" in result

    def test_validate_with_expected_outputs(self, protocol_dir):
        pfile = protocol_dir / "check_outputs.yaml"
        data = dict(SAMPLE_PROTOCOL)
        data["expected_outputs"] = [
            "workspace/results.txt: Results file",
            "workspace/log.txt: Log file",
        ]
        pfile.write_text(yaml.dump(data))
        root = protocol_dir.parent.parent.parent
        (root / "workspace").mkdir(parents=True)
        (root / "workspace" / "results.txt").touch()
        result = validate_protocol("check_outputs", root)
        assert result["all_passed"] is False
        assert len(result["checklist"]) == 2
        assert result["checklist"][0]["passed"] is True
        assert result["checklist"][1]["passed"] is False

    def test_validate_all_outputs_present(self, protocol_dir):
        pfile = protocol_dir / "all_good.yaml"
        data = dict(SAMPLE_PROTOCOL)
        data["expected_outputs"] = [
            "workspace/results.txt: Results file",
        ]
        pfile.write_text(yaml.dump(data))
        root = protocol_dir.parent.parent.parent
        (root / "workspace").mkdir(parents=True)
        (root / "workspace" / "results.txt").touch()
        result = validate_protocol("all_good", root)
        assert result["all_passed"] is True


class TestExpectedStructure:
    def test_protocols_have_name_matching_filename(self, full_protocol_dir):
        for p in full_protocol_dir.glob("*.yaml"):
            data = yaml.safe_load(p.read_text())
            assert data["name"] == p.stem

    def test_real_protocol_files_exist(self):
        root = Path(__file__).resolve().parent.parent
        pdir = root / "src" / "research_os" / "protocols"
        assert pdir.exists()
        yamls = list(pdir.glob("*.yaml"))
        assert len(yamls) > 0

    def test_all_real_protocols_load_successfully(self):
        root = Path(__file__).resolve().parent.parent
        pdir = root / "src" / "research_os" / "protocols"
        for p in sorted(pdir.glob("*.yaml")):
            result = get_protocol(p.stem, root)
            assert "error" not in result, (
                f"Protocol '{p.stem}' failed to load: {result.get('error')}"
            )
            assert "content" in result
            loaded = yaml.safe_load(result["content"])
            assert loaded is not None
            assert loaded.get("name") == p.stem
            assert "version" in loaded
            assert "steps" in loaded

    def test_light_dir_exists(self):
        root = Path(__file__).resolve().parent.parent
        ldir = root / "src" / "research_os" / "protocols" / "light"
        assert ldir.exists()

    def test_light_dir_has_no_orphans(self, full_protocol_dir):
        full_names = {p.stem for p in full_protocol_dir.glob("*.yaml")}
        light_names = {p.stem for p in (full_protocol_dir / "light").glob("*.yaml")}
        orphans = light_names - full_names
        assert not orphans, f"Light variants without full protocol: {orphans}"
