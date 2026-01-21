# Horizon-Geospatial-Unit-Test

This repository contains unit tests(classes and functions) for the Horizon geospatial client and server components. The testing approach starts with small, focused Python function tests and gradually increases scope to cover modules, endpoints, and full end-to-end behaviours of the new server. Basis of the code should be geospatial analysis and related everyday functions. 

# Run Test
in the terminal from the root directory use '''python -m pytest tests/test_arcpy_basic.py -v''' to run a test, replace 'test_arcpy_basic.py' with the test you want to run 


## What is a unit test?

A unit test is an automated check that verifies the behavior of a small, isolated piece of code (a "unit") — typically a single function or class method. Unit tests should be fast, deterministic, and independent of external systems (databases, network, file systems). They are the base of a reliable test suite because they:
- Help catch regressions early
- Provide documentation of expected behaviour
- Make refactoring safer
- Run quickly and frequently during development


## Testing strategy for this repo
We'll follow a progressive strategy:

1. Start with small, pure-Python functions (unit tests)
   - Focus on pure logic and simple python functions
   - Prefer parameterized tests for multiple inputs.

2. Move to module-level tests
   - Test classes and functions that coordinate logic between smaller units.

3. Add integration tests
   - Tests that exercise multiple components together (e.g., client + library code).
   - Use test fixtures and either test instances of the server or lightweight in-memory alternatives.

4. Add system / end-to-end tests
   - Tests that exercise the real server (staging), using known test data.
   - Mark these tests so they can be excluded from fast test runs.

This progression keeps the test suite fast and focused while increasing confidence as we expand coverage.


## Contributing
- create a branch for new tests
- Add tests for bugfixes, features and selected workflows.
- Keep unit tests fast and deterministic.
- Run the test suite locally before opening PRs.
- updated documentation if necessary.
- PRs must pass automated tests that pass locally and in CI.
