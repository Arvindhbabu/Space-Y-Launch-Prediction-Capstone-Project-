# Local Environment and Model Troubleshooting

## Why a dashboard can fail while the repository has passing CI

Python can run a project with a different interpreter from the one used to install its dependencies. On Windows, this can happen when Streamlit or pytest runs against a global Python installation in `AppData\Roaming\Python\Python312\site-packages` instead of the project's `.venv`.

A model artifact serialized by one scikit-learn version is not guaranteed to work with another. Errors such as:

```text
AttributeError: 'LogisticRegression' object has no attribute 'multi_class'
```

can be a symptom of a stale/incompatible serialized model, an interpreter mismatch, or both. Do not repair a serialized estimator by manually assigning attributes.

## Diagnose first

From the repository root, activate the project's virtual environment and run the preflight:

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
python -c "import sys, sklearn; print(sys.executable); print(sklearn.__version__); print(sklearn.__file__)"
python scripts/diagnose_environment.py
python -m pip check
```

### macOS / Linux

```bash
source .venv/bin/activate
python -c "import sys, sklearn; print(sys.executable); print(sklearn.__version__); print(sklearn.__file__)"
python scripts/diagnose_environment.py
python -m pip check
```

The executable should resolve to the project environment. The diagnostic compares exact package pins in `requirements.txt`, the supported Python version, and the scikit-learn version recorded in `models/registry/registry_metadata.json` without deserializing the model.

## Recover a mismatched environment

If the preflight reports dependency or model-version mismatches:

1. Use the documented Python 3.12 environment.
2. Recreate the virtual environment rather than mixing global and project packages.
3. Reinstall `requirements.txt`.
4. Run `scripts/diagnose_environment.py` again.
5. If model provenance differs from the pinned environment, retrain the model with `python scripts/train_model.py` and verify that the registry artifact and metadata were regenerated together.
6. Restart Streamlit and the API from the same activated environment.
7. Run `python -m pytest tests/ -v`.

Example clean setup on Windows PowerShell:

```powershell
deactivate
Remove-Item -Recurse -Force .venv
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/diagnose_environment.py
python -m pytest tests/ -v
```

Do not delete or replace registered model artifacts until you have confirmed that the active interpreter and dependencies are correct. Preserve any local, uncommitted work before recreating the environment.

## What a successful diagnostic means

A passing preflight establishes that exact declared dependencies are installed, the Python major/minor version fits the project's declared constraint, model provenance exists, and the recorded scikit-learn version matches the pinned and installed version. It does **not** prove the model is statistically reliable or that the live dashboard has been interactively verified.

For scientific and operational limitations, see [Model Card](MODEL_CARD.md), [Methodology](METHODOLOGY.md), and [Limitations](LIMITATIONS.md).
