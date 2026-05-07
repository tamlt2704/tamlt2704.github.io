# Pytest Mastery

Tests that actually catch bugs. Build a test suite for a fintech invoicing platform (Ledgerly) — from first assert to property-based testing and CI pipelines.

## Chapters

| # | Topic | Key Concepts |
|---|---|---|
| 00 | [Overview](chapter-00-overview.md) | Why pytest, mental model, roadmap |
| 01 | [First Test](chapter-01-first-test.md) | assert, test discovery, pytest.raises, running tests |
| 02 | [Parametrize](chapter-02-parametrize.md) | Data-driven tests, pytest.param, stacking, xfail |
| 03 | [Fixtures](chapter-03-fixtures.md) | Setup/teardown, scope, yield, monkeypatch, factories |
| 04 | conftest.py | Shared fixtures, fixture hierarchy, auto-discovery |
| 05 | Exception Testing | pytest.raises, match, custom exceptions |
| 06 | Mocking | patch, MagicMock, when to mock, when not to |
| 07 | Async Testing | pytest-asyncio, async fixtures, event loops |
| 08 | Database Testing | Testcontainers, session fixtures, rollback |
| 09 | Time Testing | freezegun, time-dependent logic, timezones |
| 10 | Test Data | factory-boy, realistic fixtures, relationships |
| 11 | Property-Based | Hypothesis, strategies, finding edge cases |
| 12 | Performance | pytest-xdist, markers, test selection, parallelism |
| 13 | Flaky Tests | Isolation, debugging, determinism |
| 14 | Integration Tests | TestClient, API testing, end-to-end |
| 15 | Plugins & Custom | Writing plugins, custom markers, hooks |
| 16 | Testing Strategy | Test pyramid, what to test, ROI |
| 17 | Coverage | pytest-cov, meaningful coverage, mutation testing |
| 18 | Behavior Testing | Testing behavior not implementation, refactor-proof |
| 19 | CI Pipeline | pytest in GitHub Actions, reporting, caching |
| 20 | Maintenance | Living test suite, documentation, culture |

## Stack

- Python 3.12+
- pytest 8.x
- pytest-asyncio, pytest-cov, pytest-xdist
- unittest.mock / pytest-mock
- factory-boy, hypothesis, freezegun
- testcontainers
