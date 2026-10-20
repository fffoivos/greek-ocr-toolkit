# SPLIT1 QA status

The data and persistence checks execute offline. `test_sheet_runtime.cjs` executes the actual shipped JavaScript against an instrumented DOM and database fixture; it verifies no writes on load/hydration/focus/blur/issue selection, independent edition IDs, one document per action, debounce, reload, and early edits. It is **not** a browser-rendering test.

**Screenshot QA remains blocked and unverified.** No screenshot was produced:

- The installed Playwright package requests Firefox build 1543, which is absent. Network is OFF; no browser was downloaded.
- Explicitly launching the already-installed Firefox build 1488 in headless mode aborted with SIGABRT.
- The installed Google Chrome also aborted with SIGABRT under this execution sandbox (the tool log includes `kill EPERM`).
- The available computer-use fallback rejected Firefox access: `Computer Use was not approved to use Firefox`.

Automatic approval rejected the Firefox visual inspection; it gave no further reason. No approval bypass was attempted. The lead still needs to run `headless_qa.py` in an authorized local browser environment and visually inspect its desktop and narrow screenshots before publishing. This page has not been published, and its database has not been connected or changed.
