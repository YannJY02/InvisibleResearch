```markdown
# InvisibleResearch Development Patterns

> Auto-generated skill from repository analysis

## Overview

This skill teaches best practices for contributing to the InvisibleResearch Python codebase. You'll learn the project's coding conventions, file organization, commit patterns, and the two main collaborative workflows for migrating/refactoring workspace components and expanding hybrid workspace seams. This guide is essential for maintaining consistency and quality when working with the InvisibleResearch repository.

## Coding Conventions

- **Language:** Python (no major framework)
- **File Naming:** Use `snake_case` for all file and module names.
  - Example: `data_loader.py`, `process_data.py`
- **Import Style:** Prefer **relative imports** within packages.
  - Example:
    ```python
    from .utils import load_config
    ```
- **Export Style:** Use **named exports** (explicitly define what is exported).
  - Example:
    ```python
    __all__ = ["DataProcessor", "load_config"]
    ```
- **Commit Messages:** Follow [Conventional Commits](https://www.conventionalcommits.org/) with prefixes like `feat`, `refactor`.
  - Example:
    ```
    feat: add initial data validation module
    refactor: restructure research notebooks
    ```

## Workflows

### Migrate or Refactor Major Workspace Component

**Trigger:** When you need to migrate or refactor a significant part of the workspace (e.g., moving analysis, restructuring research modules, consolidating capabilities).

**Command:** `/migrate-workspace-component`

**Step-by-step:**
1. Update or add `README.md` files at the root, in `data/`, `docs/`, `research/`, and any relevant submodules.
2. Modify or add scripts in `scripts/` or `src/invisible_research/`.
3. Update or add Jupyter notebooks in `notebooks/` or `research/*/notebooks/`.
4. Update or add documentation in `docs/` and `research/*/README.md`.
5. Update or add test files in `tests/`.
6. Update `run_pipeline.sh` if pipeline steps are affected.
7. Update or add artifact/component manifest files in `data/artifact-versions/` or `data/component-manifests/`.

**Example:**
```bash
# After making code and doc changes
git add README.md data/README.md docs/ research/ scripts/ src/invisible_research/ notebooks/ tests/ run_pipeline.sh data/artifact-versions/ data/component-manifests/
git commit -m "refactor: migrate exploratory analysis to new module"
```

### Hybrid Workspace Cutover or Expansion

**Trigger:** When implementing or expanding a hybrid workspace seam, such as cutting over to a new workspace structure.

**Command:** `/hybrid-workspace-cutover`

**Step-by-step:**
1. Update or add configuration files (e.g., `.env.example`, `config/env.template`, `config/settings.py`).
2. Update or add documentation in `docs/` and `data/README.md`.
3. Modify or add scripts in `scripts/02_extraction/` and `scripts/05_validation/`.
4. Update or add code in `src/invisible_research/acquisition/`, `processing/`, and `validation/` modules.
5. Update or add test files in `tests/`.
6. Update `run_pipeline.sh`.
7. Update or add artifact/component manifest files in `data/artifact-versions/` or `data/component-manifests/`.

**Example:**
```bash
# After updating configs and modules
git add .env.example config/ docs/ data/ scripts/ src/invisible_research/ tests/ run_pipeline.sh data/artifact-versions/ data/component-manifests/
git commit -m "feat: cut over to hybrid workspace structure"
```

## Testing Patterns

- **Framework:** Unknown (no explicit framework detected).
- **Test File Pattern:** Python test files are in `tests/` and follow the `*.py` pattern.
- **Other Patterns:** There may be TypeScript test files (`*.test.ts`), but for Python, use standard test naming.
  - Example:
    ```
    tests/test_data_loader.py
    ```
- **Test Example:**
    ```python
    import unittest
    from src.invisible_research.data_loader import load_data

    class TestDataLoader(unittest.TestCase):
        def test_load_data(self):
            data = load_data("sample.csv")
            self.assertIsNotNone(data)
    ```

## Commands

| Command                    | Purpose                                                      |
|----------------------------|--------------------------------------------------------------|
| /migrate-workspace-component| Migrate or refactor a major workspace component              |
| /hybrid-workspace-cutover   | Implement or expand a hybrid workspace seam                  |
```
