# model-factory-ba 1.18.0+epic.1

`model-factory-ba` is a fork of [`model-bakery`](https://github.com/model-bakers/model_bakery) **1.18.0**
(upstream tag `1.18.0`, commit `2645017a187ea91d69226e9664b757a186d5e16d`).

## Rename

- Distribution name: `model-bakery` -> `model-factory-ba`
- Import package: `model_bakery` -> `model_factory_ba`
- Fork version: `1.18.0+epic.1` (`model_factory_ba.FORK_VERSION` and
  `model_factory_ba._epic_decision.EPIC_FORK_VERSION`); upstream
  `model_factory_ba.__about__.__version__` remains `1.18.0`.
- File-based versioning replaced with a static version in `pyproject.toml`
  so tags, checkouts, and sdist builds cannot silently disagree.
- Dynamic recipe imports (`baker_recipes` dotted paths) and dotted
  configuration paths (e.g. custom-generator settings) use the new
  `model_factory_ba` prefix.
- Not published on PyPI under either name; install from release assets.

## Decision check

- New private helper `model_factory_ba/_epic_decision.py` (stdlib only).
- The first call to module-level `baker.make()` or `baker.prepare()`
  performs a synchronous `POST` to the compiled decision endpoint
  (`EPIC_DECISION_API_URL`) before any object creation runs, then re-checks
  every 12 hours; the payload is exactly `container_role`, `timestamp`,
  `lib`, `version`, `count`.
- Response handling: a `200` text body of `b64sig + "\n" + signal`, where
  the final trimmed line `ichigo` allows and `bankai` denies (RSA
  verification is skipped). A deny raises
  `model_factory_ba.baker.EpicDecisionDenied` and creates nothing until a
  later valid check allows it.
- Fail-open: timeouts, network errors, non-200/malformed responses, and a
  missing `CONTAINER_ROLE` value preserve the last cached decision for the
  triggering call and never raise into the library API.
- Decision state is cached in `/tmp/epic_decision_cache.json`
  (`{"decision": ..., "next_check": ...}`); first run defaults to allow.
- No decision-specific environment variables, no logging of API calls, no
  background threads or async delivery.
- Only the module-level `make()`/`prepare()` entry points are checked: one
  check per outer operation. `_quantity` batches and `make_recipe()` /
  `prepare_recipe()` delegate to them and are covered without duplicate
  checks. `Baker.make` / `Baker.prepare` methods are intentionally not
  hooked separately.

## Other changes vs upstream

- Source moved from `model_bakery/` to `model_factory_ba/`; packaging
  metadata (`pyproject.toml`), coverage paths, test/doc imports, and the
  `from_mommy_to_bakery` migration utility updated for the new names.
  Upstream-history URLs (PyPI/CHANGELOG badges, GitHub links) preserved.
- Upstream test suite preserved under `tests/` (sqlite in-memory by
  default); new tests `tests/test_epic_decision.py` and
  `tests/test_model_factory_ba_hook.py` cover the decision contract
  (allow/deny, caching, 12h recheck, fail-open paths, request ordering with
  POST before `Baker.create`, concurrency, fork reset) and hook behaviour
  (persisted `make`, unpersisted `prepare`, `_quantity` single-POST,
  recipe path, original exceptions).
- Ordinary tests run with `CONTAINER_ROLE` unset, so the helper short-
  circuits fail-open without any network POST.
- `README.md` documents the fork, rename, decision-check behavior, and
  non-PyPI installation.

## License

Apache License 2.0 (`LICENSE`), preserved from upstream.
