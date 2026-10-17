# Security Policy

## Scope

This project is an educational data-science application. Security reports are welcome for issues such as exposed credentials, unsafe handling of user input, dependency vulnerabilities with meaningful impact, or unintended disclosure of private data.

## Reporting a vulnerability

Please do **not** publish credentials, exploit details, private data, or a potentially exploitable vulnerability in a public issue.

Use GitHub's private vulnerability reporting feature for this repository if it is enabled. If it is unavailable, contact the repository maintainer privately through GitHub and include:
- A concise description and potential impact.
- Steps to reproduce, with sensitive values removed.
- A suggested mitigation, if known.

Do not include real API keys, passwords, access tokens, personal information, or production secrets in the report.

## Supported versions

Only the current default branch is actively maintained as the project evolves. There is no formal service-level agreement or guaranteed response time for security reports.

## Dependency and model artifacts

Run dependency checks in the project environment:

~~~bash
python -m pip check
python scripts/diagnose_environment.py
~~~

The preflight reports version and provenance mismatches; it does not perform a complete security audit. Treat serialized model artifacts and downloaded datasets as untrusted inputs unless their source and integrity are understood.
