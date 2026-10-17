"""Tests for the runtime preflight diagnostic."""
import json
from pathlib import Path

from scripts.diagnose_environment import (
    inspect_environment,
    normalize_distribution_name,
    parse_pinned_requirements,
    python_version_supported,
)


def test_distribution_name_normalization():
    assert normalize_distribution_name("scikit_learn") == "scikit-learn"
    assert normalize_distribution_name("FastAPI") == "fastapi"


def test_parse_exact_dependency_pins(tmp_path: Path):
    requirements = tmp_path / "requirements.txt"
    requirements.write_text(
        "# comment\nFastAPI==0.143.0\nhttpx>=0.28\nnumpy==2.5.4 # pinned\n",
        encoding="utf-8",
    )
    assert parse_pinned_requirements(requirements) == {
        "fastapi": "0.143.0",
        "numpy": "2.5.4",
    }


def test_python_constraints_accept_and_reject_versions():
    assert python_version_supported((3, 12), ">=3.12,<3.13")
    assert not python_version_supported((3, 11), ">=3.12,<3.13")
    assert not python_version_supported((3, 13), ">=3.12,<3.13")


def _make_project(root: Path, trained_sklearn: str = "1.9.1") -> None:
    (root / "models" / "registry").mkdir(parents=True)
    (root / "requirements.txt").write_text(
        "numpy==2.5.4\nscikit-learn==1.9.1\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        '[project]\nrequires-python = ">=3.12,<3.13"\n',
        encoding="utf-8",
    )
    metadata = {
        "model_name": "test-model",
        "package_versions": {"scikit-learn": trained_sklearn},
    }
    (root / "models" / "registry" / "registry_metadata.json").write_text(
        json.dumps(metadata), encoding="utf-8"
    )
    (root / "models" / "registry" / "best_pipeline.joblib").write_bytes(b"test-placeholder")


def test_preflight_passes_when_runtime_matches_model_and_pins(tmp_path: Path):
    _make_project(tmp_path)
    report = inspect_environment(
        tmp_path,
        installed_versions={"numpy": "2.5.4", "scikit-learn": "1.9.1"},
        python_version=(3, 12, 10),
    )
    assert report["ok"] is True
    assert all(check["status"] == "PASS" for check in report["checks"])


def test_preflight_fails_on_stale_scikit_learn_runtime(tmp_path: Path):
    _make_project(tmp_path)
    report = inspect_environment(
        tmp_path,
        installed_versions={"numpy": "2.5.4", "scikit-learn": "1.5.1"},
        python_version=(3, 12, 10),
    )
    assert report["ok"] is False
    assert any(
        check["status"] == "FAIL"
        and check["label"] == "Model/scikit-learn compatibility"
        and "1.5.1" in check["detail"]
        for check in report["checks"]
    )


def test_preflight_fails_when_model_provenance_is_missing(tmp_path: Path):
    _make_project(tmp_path)
    metadata_path = tmp_path / "models" / "registry" / "registry_metadata.json"
    metadata_path.unlink()
    report = inspect_environment(
        tmp_path,
        installed_versions={"numpy": "2.5.4", "scikit-learn": "1.9.1"},
        python_version=(3, 12, 10),
    )
    assert report["ok"] is False
    assert any(check["label"] == "Model provenance" and check["status"] == "FAIL" for check in report["checks"])
