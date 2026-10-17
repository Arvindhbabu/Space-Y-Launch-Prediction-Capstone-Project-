# Contributing to SpaceY Intelligence

Thank you for taking an interest in SpaceY Intelligence. Contributions that improve correctness, reproducibility, accessibility, documentation, and testing are welcome.

## Before opening a change

1. Search existing issues and pull requests to avoid duplicating work.
2. For a large change, open an issue first to explain the motivation and proposed approach.
3. Keep changes focused and preserve the educational scope and limitations of the project.

## Local setup

Use Python 3.12 and an isolated environment. Follow the setup in the README, then run:

~~~bash
python scripts/diagnose_environment.py
python -m pip check
python -m compileall -q app.py pages src scripts tests
python -m pytest tests/ -v
~~~

Use the same environment for training, inference, the API, Streamlit, and tests. Do not manually edit serialized scikit-learn model objects to work around version conflicts.

## Pull request expectations

- Explain the problem and the observable effect of the change.
- Include tests for bug fixes and new behavior where practical.
- Update documentation when an interface, command, data definition, or limitation changes.
- Do not commit credentials, tokens, private data, local virtual environments, or unrelated generated output.
- Avoid presenting illustrative economics or small-sample model results as verified aerospace facts.
- State exactly which checks you ran. Do not claim a successful UI or container smoke test unless it was actually performed.
- Keep pull requests reviewable and use a descriptive title, such as `fix: validate missing launch dates` or `docs: clarify model limitations`.

## Data and model changes

- Document the source, retrieval date, target definition, and relevant preprocessing changes when changing data pipelines.
- Keep the benchmark and operational-history datasets conceptually distinct unless a scientifically justified evaluation design says otherwise.
- Audit date validity, duplicates, missing values, target leakage, class balance, and possible overlap before reporting model metrics.
- Regenerate model artifacts only in the pinned environment and update provenance metadata together with the artifact.
- Never report fabricated performance numbers or present the model as fit for real mission authorization.

## Style

Follow the style of nearby code, prefer small typed functions where useful, handle errors explicitly, and keep comments focused on why a decision is made.

## Review process

Maintainers may request changes for correctness, reproducibility, clarity, security, or scope. A passing CI job is necessary evidence for code changes, but does not by itself prove scientific validity or interactive deployment behavior.
