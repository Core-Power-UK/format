# !/usr/bin/env python3
"""Parse pyproject.toml and update dependencies."""

from __future__ import annotations

import tomllib
from pathlib import Path

import requests
from packaging.requirements import Requirement
from packaging.version import Version


def get_new_versions(dependency: Requirement) -> list[Version] | int:
    """Get new versions of dependency from PYPI."""
    print(f"Checking: {dependency.name}")
    specs = list(dependency.specifier)
    if len(specs) != 1:
        print(
            "Number of specifiers found does not match expected number for"
            f" {dependency.name}",
        )
        return 1

    spec = specs[0]
    if spec.operator != "==":
        print(f"Operator for {dependency.name} is not ==, please fix and try again")
        return 1

    current_version = Version(spec.version)
    print(f"Current version: {current_version}")

    # Get all versions of dependency from PYPI
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{dependency.name}/json",
            timeout=0.1,
        )
    except ConnectionError:
        print("Unable to connect to PYPI")
        return 1

    if response.status_code != 200:
        raise RuntimeError

    versions = [Version(release) for release in response.json()["releases"]]
    versions = [v for v in versions if v > current_version]
    versions.sort()

    return versions


def get_new_versions_of_deps(deps: list[str]) -> list[str] | int:
    """Get new versions of dependency from PYPI."""
    output_deps = []
    for requirement in deps:
        dependency = Requirement(requirement)
        versions = get_new_versions(dependency)
        if isinstance(versions, int):
            return versions

        # Check if new versions are available
        if len(versions) == 0:
            print(f"No new versions found for {dependency.name}")
            output_deps.append(requirement)
            continue

        # Update to latest version
        print(f"New versions found for {dependency.name}: {versions[-1]}")
        output_deps.append(f"{dependency.name}=={versions[-1]}")

    return output_deps


def update_file_deps(file: Path, deps: list[str], output_deps: list[str]) -> None:
    """Update pyproject.toml with new dependencies."""
    print(f"Updating {file.name}")
    with file.open("r") as f:
        pyproject_str = f.read()

    for dep, output_dep in zip(deps, output_deps, strict=True):
        if dep != output_dep:
            print(f'Updating "{dep}" to "{output_dep}"')
            pyproject_str = pyproject_str.replace(dep, output_dep)

    with file.open("w") as f:
        f.write(pyproject_str)


def update_pyproject_toml() -> int:
    """Check for updated pyproject.toml dependencies."""
    pyproject_toml = Path(__file__).parent.parent / "pyproject.toml"
    print("Checking pyproject.toml")
    with pyproject_toml.open("rb") as f:
        pyproject = tomllib.load(f)

    # Get project dependencies
    deps = pyproject["project"]["dependencies"]
    output_deps = get_new_versions_of_deps(deps)
    if isinstance(output_deps, int):
        return output_deps

    # Update file if its dependencies have changed
    if deps != output_deps:
        update_file_deps(pyproject_toml, deps, output_deps)

    return 0


def update_pre_commit_config() -> int:
    """Check for updated pre-commit config dependencies."""
    pre_commit_config = Path(__file__).parent.parent / ".pre-commit-config.yaml"
    print("Checking .pre-commit-config.yaml")
    with pre_commit_config.open("r") as f:
        pre_commit = f.readlines()

    deps = [line.strip().removeprefix("- ") for line in pre_commit if "==" in line]
    output_deps = get_new_versions_of_deps(deps)
    if isinstance(output_deps, int):
        return output_deps

    if deps != output_deps:
        update_file_deps(pre_commit_config, deps, output_deps)

    return 0


def update_workflows() -> int:
    """Update workflows dependencies."""
    workflows = Path(__file__).parent.parent / ".github/workflows"
    print("Checking workflows")
    for workflow in workflows.glob("*.yml"):
        print(f"Checking {workflow.name}")
        with workflow.open("r") as f:
            workflow_str = f.read()

        deps = [
            line.strip().removeprefix("python -m pip install ")
            for line in workflow_str.splitlines()
            if "==" in line
        ]
        output_deps = get_new_versions_of_deps(deps)
        if isinstance(output_deps, int):
            return output_deps

        if deps != output_deps:
            update_file_deps(workflow, deps, output_deps)

    return 0


def main() -> int:
    """Update dependencies."""
    if update_pyproject_toml() == 1:
        return 1

    if update_pre_commit_config() == 1:
        return 1

    if update_workflows() == 1:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
