"""Diagnose dependency, Python, and registered-model runtime mismatches.

Run from the project root:
    python scripts/diagnose_environment.py

This script inspects package metadata and JSON provenance only. It deliberately does
not deserialize joblib/pickle files, so it remains safe to run before loading a model.
"""
from __future__ import annotations

import importlib.metadata
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PIN_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*==\s*([^\s;#]+)")
PYTHON_CONSTRAINT_RE = re.compile(r"(>=|<=|==|>|<)\s*(\d+)\.(\d+)")


def normalize_distribution_name(name: str) -> str:
    """Normalize a package name using Python package-name comparison rules."""
    return re.sub(r"[-_.]+", "-", name).lower()


def parse_pinned_requirements(path: Path) -> dict[str, str]:
    """Return normalized package names mapped to exact versions from requirements."""
    pins: dict[str, str] = {}
    if not path.is_file():
        return pins
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        match = PIN_RE.match(line)
        if match:
            pins[normalize_distribution_name(match.group(1))] = match.group(2)
    return pins


def python_version_supported(
    python_version: Sequence[int], requires_python: str
) -> bool:
    """Evaluate simple major/minor PEP 440 constraints used in pyproject.toml."""
    constraints = PYTHON_CONSTRAINT_RE.findall(requires_python)
    if not constraints:
        return False
    current = (int(python_version[0]), int(python_version[1]))
    for operator, major_text, minor_text in constraints:
        target = (int(major_text), int(minor_text))
        if operator == ">=" and not current >= target:
            return False
        if operator == ">" and not current > target:
            return False
        if operator == "<=" and not current <= target:
            return False
        if operator == "<" and not current < target:
            return False
        if operator == "==" and not current == target:
            return False
    return True


def _read_requires_python(pyproject_path: Path) -> str | None:
    if not pyproject_path.is_file():
        return None
    text = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r'requires-python\s*=\s*"([^"]+)"', text)
    return match.group(1) if match else None


def _installed_versions(
    expected_names: Sequence[str],
    supplied: Mapping[str, str] | None = None,
) -> dict[str, str | None]:
    normalized_supplied = {
        normalize_distribution_name(name): version
        for name, version in (supplied or {}).items()
    }
    versions: dict[str, str | None] = {}
    for name in expected_names:
        normalized = normalize_distribution_name(name)
        if supplied is not None:
            versions[normalized] = normalized_supplied.get(normalized)
            continue
        try:
            versions[normalized] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[normalized] = None
    return versions


def inspect_environment(
    root: Path = PROJECT_ROOT,
    *,
    installed_versions: Mapping[str, str] | None = None,
    python_version: Sequence[int] | None = None,
) -> dict[str, Any]:
    """Return diagnostic checks for dependencies, Python, and model provenance."""
    root = Path(root).resolve()
    checks: list[dict[str, str]] = []

    def add(status: str, label: str, detail: str) -> None:
        checks.append({"status": status, "label": label, "detail": detail})

    requirements_path = root / "requirements.txt"
    pins = parse_pinned_requirements(requirements_path)
    if not pins:
        add("FAIL", "Dependency pins", "No exact package pins found in requirements.txt.")
    else:
        versions = _installed_versions(list(pins), installed_versions)
        for package in sorted(pins):
            expected = pins[package]
            actual = versions.get(package)
            display_name = package
            if actual is None:
                add("FAIL", f"Dependency: {display_name}", f"Not installed; expected {expected}.")
            elif actual != expected:
                add(
                    "FAIL",
                    f"Dependency: {display_name}",
                    f"Installed {actual}; requirements.txt pins {expected}.",
                )
            else:
                add("PASS", f"Dependency: {display_name}", f"Installed version matches pin {expected}.")

    current_python = tuple(python_version or sys.version_info[:2])
    requires_python = _read_requires_python(root / "pyproject.toml")
    if requires_python is None:
        add("WARN", "Python version", "Could not read requires-python from pyproject.toml.")
    elif python_version_supported(current_python, requires_python):
        add(
            "PASS",
            "Python version",
            f"Python {current_python[0]}.{current_python[1]} satisfies {requires_python}.",
        )
    else:
        add(
            "FAIL",
            "Python version",
            f"Python {current_python[0]}.{current_python[1]} is outside the project constraint {requires_python}.",
        )

    registry_dir = root / "models" / "registry"
    artifact_path = registry_dir / "best_pipeline.joblib"
    metadata_path = registry_dir / "registry_metadata.json"
    if artifact_path.is_file():
        add("PASS", "Model artifact", f"Found {artifact_path.relative_to(root)}.")
    else:
        add("FAIL", "Model artifact", f"Missing {artifact_path.relative_to(root)}.")

    metadata: dict[str, Any] | None = None
    if metadata_path.is_file():
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            add("PASS", "Model provenance", "Registry metadata is present and valid JSON.")
        except (OSError, json.JSONDecodeError) as exc:
            add("FAIL", "Model provenance", f"Could not parse registry metadata: {exc}.")
    else:
        add("FAIL", "Model provenance", f"Missing {metadata_path.relative_to(root)}.")

    if metadata is not None:
        package_versions = metadata.get("package_versions") or {}
        trained_sklearn = package_versions.get("scikit-learn") or metadata.get("sklearn_version")
        pins_sklearn = pins.get(normalize_distribution_name("scikit-learn"))
        current_versions = _installed_versions(["scikit-learn"], installed_versions)
        running_sklearn = current_versions.get(normalize_distribution_name("scikit-learn"))

        if not trained_sklearn:
            add("FAIL", "Model/scikit-learn compatibility", "Training scikit-learn version is missing from model metadata.")
        elif not pins_sklearn:
            add("FAIL", "Model/scikit-learn compatibility", "requirements.txt has no exact scikit-learn pin.")
        elif running_sklearn is None:
            add("FAIL", "Model/scikit-learn compatibility", "scikit-learn is not installed in the active interpreter.")
        elif trained_sklearn != pins_sklearn or running_sklearn != pins_sklearn:
            add(
                "FAIL",
                "Model/scikit-learn compatibility",
                f"Model was trained with {trained_sklearn}; requirements pin {pins_sklearn}; active runtime has {running_sklearn}.",
            )
        else:
            add(
                "PASS",
                "Model/scikit-learn compatibility",
                f"Training, requirements, and runtime all use scikit-learn {pins_sklearn}.",
            )

    return {
        "project_root": str(root),
        "python_executable": sys.executable,
        "python_version": ".".join(str(part) for part in (python_version or sys.version_info[:3])),
        "checks": checks,
        "ok": all(check["status"] != "FAIL" for check in checks),
    }


def main() -> int:
    report = inspect_environment()
    print("SpaceY Intelligence — Runtime Preflight")
    print(f"Project root: {report['project_root']}")
    print(f"Python:       {report['python_version']}")
    print(f"Interpreter:  {report['python_executable']}")
    print("-" * 78)
    for check in report["checks"]:
        print(f"[{check['status']:<4}] {check['label']}: {check['detail']}")
    print("-" * 78)
    print("RESULT: " + ("PASS — runtime and model provenance are consistent." if report["ok"] else "FAIL — fix the reported issues before running predictions."))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
