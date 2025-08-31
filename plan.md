# Test Coverage and Code Health Strategy

## 1. Executive Summary

This document outlines a strategy to enhance the robustness and maintainability of the `dspy-profiles` library. Our primary goal is to achieve **>95% test coverage**, but more importantly, to ensure that our tests are meaningful, maintainable, and strategically aligned with the library's architecture. We will prioritize testing based on criticality, starting with core logic and moving to the application's outer layers (API and CLI). We will also refactor code where necessary to improve testability and adhere to best practices in modular design.

## 2. Guiding Principles

*   **Test for Behavior, Not Implementation:** Tests should validate the public-facing behavior of components. This makes them less brittle to internal refactoring.
*   **The Testing Pyramid:** We will adhere to the testing pyramid:
    *   **Unit Tests:** Fast, isolated tests for pure, stateless functions (e.g., `utils._deep_merge`).
    *   **Integration Tests:** Tests for components that interact with each other or the filesystem (e.g., `ProfileManager`, `ProfileLoader`). These will use a sandboxed temporary filesystem.
    *   **End-to-End (E2E) Tests:** High-level tests that validate user-facing workflows via the CLI (`CliRunner`).
*   **Refactor for Testability:** We will actively identify and refactor code that is difficult to test, promoting smaller functions and clear separation of concerns.

## 3. Strategic Plan

### Phase 1: Baseline and Core Logic (Highest Priority)

1.  **Establish Baseline:** Run `pytest --cov` to measure the current test coverage. This is our starting metric.
2.  **Core Utilities & Logic:**
    *   **Target:** `dspy_profiles/utils.py`, `dspy_profiles/core.py`.
    *   **Action:** Create `tests/test_utils.py` and `tests/test_core_logic.py`. Write unit tests for pure functions like `normalize_config` and `_deep_merge`.
    *   **Refactoring:** Analyze the `profile` context manager in `core.py`. Extract complex logic into smaller, independently testable helper functions.

### Phase 2: State and Configuration Management

1.  **Configuration & File I/O:**
    *   **Target:** `dspy_profiles/config.py`.
    *   **Action:** Create `tests/test_config.py`. Write integration tests for `ProfileManager`, ensuring it correctly handles creating, reading, updating, and deleting profiles from a temporary `profiles.toml`.
2.  **Profile Resolution:**
    *   **Target:** `dspy_profiles/loader.py`.
    *   **Action:** Create `tests/test_loader.py`. Test `ProfileLoader` against various scenarios: simple profiles, profiles with `extends`, nested inheritance, and edge cases like circular dependencies.

### Phase 3: API and CLI (User-Facing Layers)

1.  **Public API:**
    *   **Target:** `dspy_profiles/api.py`.
    *   **Action:** Create `tests/test_api.py`. Test the public functions, ensuring they correctly interface with the underlying managers and loaders.
2.  **CLI Commands:**
    *   **Target:** `dspy_profiles/commands/`.
    *   **Action:** Create `tests/test_cli_commands.py`. Use `typer.testing.CliRunner` to write E2E tests for the CLI, covering all commands (`init`, `list`, `set`, `show`, `delete`, `validate`).

### Phase 4: Review and Refine

1.  **Existing Test Refactoring:** Review all existing test files. Refactor them to align with our principles of small, focused tests.
2.  **Final Coverage Measurement:** Run `pytest --cov` again and analyze the report. Identify any remaining gaps and write tests to cover them until we exceed our 95% goal.
