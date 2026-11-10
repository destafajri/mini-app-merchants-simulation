# Verification record

Reviewed 2026-11-10. These results are local, not CI or deployed integration evidence.

| Check | Result |
| --- | --- |
| `python -m pytest -q` | PASS: 4 tests covering session/login/logout, CSRF, wrong credentials, expiry, two subjects, JWT verification, wrong audience, public-only JWKS and configuration. |
| `node tests/test_bridge.mjs` | PASS: SDK origin/source/request ID/schema rejection, listener cleanup, timeout and standalone failure. |
| `python -m compileall -q app.py tools tests` | PASS. |
| `pip check` | PASS: no broken installed requirements. |
| Relative Markdown link check | PASS before this record was added. |
| Mobile browser (390 × 844) | PASS: login, embedded receiver BRIDGE_OK, back and logout. |
| Parent message rejection in browser | PASS: forged origin and wrong source caused zero token endpoint calls. |
| Branding at mobile width | PASS: Murid Wukong title; no horizontal overflow. |
| Real service authenticated history | NOT_EVALUATED: no configured live service URL or registered merchant supplied. |
| External FE embedding | NOT_EVALUATED: receiving FE not yet available. |
| Vercel deployment | NOT_EVALUATED: deployment is owned by user. |

Python verification used a local 3.14 environment. `requirements.lock.txt` records the installed versions; `requirements.txt` specifies compatible dependency ranges. For an exact repeat, install the lock file in a compatible Python environment. The test run emitted a Starlette TestClient deprecation warning about future httpx2 use; assertions passed. Browser 401s before login/after logout were expected. Initial missing favicon was fixed with an inline empty favicon. A sandbox warning is expected for the intentionally same-origin receiver; use a distinct FE origin for the external integration.

[Mobile merchant screenshot](merchant-mobile.png) uses synthetic test identity only. It is not a production screenshot.

Telemetry workflow-start and stage-start delivery attempts timed out at the configured publisher. No publisher acceptance or dashboard ingestion was verified; lifecycle tracking is incomplete. No automated retries were performed.

## Local first-run follow-up (historical setup behavior)

The first real setup invocation exposed a `Path.open(opener=...)` incompatibility. The helper now uses built-in `open` with an exclusive, owner-only opener. A subprocess regression test verifies successful env generation, password hash usability, permissions, no plaintext password in env/output, and overwrite refusal. `python -m pytest -q`: PASS, 5 tests. SDK checks remain PASS. Generated local configuration and login details are excluded from version control.

## Repository demo accounts and reduced environment (historical password behavior)

Current account configuration supersedes the historical setup behavior above. Ten synthetic accounts now come from `fixtures/demo_users.json` with the public password documented in README. `DEMO_USERS_JSON` is ignored. Normal runtime requires only merchant URL, RSA private key and session secret; auth identity defaults remain overridable.

- `python -m pytest -q` — PASS, 6 tests, including all ten fixture logins and unique IDs, legacy user env ignored, default issuer/audience/merchant/key ID, signed JWT subject, and non-interactive private setup with overwrite protection.
- `node tests/test_bridge.mjs` — PASS.
- Local Chrome at 390 × 844 — PASS: both `demo` and `demo10` login, greeting, embedded receiver `BRIDGE_OK`, back, logout.
- `GET /fixtures/demo_users.json` — 404, as intended; account fixture is not an HTTP asset.
- Compile check, annotated example dotenv parsing (five active keys), Markdown relative links, and whitespace diff check — PASS.
- Local RSA key and session secret preserved during config simplification. No Go service changes or real downstream integration checks performed.
- Telemetry workflow-start delivery timed out; no publisher acceptance or complete lifecycle tracking established. No automated retry.


## Shared password in environment

Supersedes fixture-password behavior above: `fixtures/demo_users.json` contains only ten stable IDs, names and usernames. `DEMO_USER_PASSWORD` is required for login and has no runtime fallback. The setup helper writes an initial example value without printing it; local/Vercel operators choose the actual shared password. Signing key and session secret remain unchanged.

- `python -m pytest -q` — PASS, 7 tests, including password override for all ten accounts, previous password rejection, unknown user rejection, Unicode password support, and missing/empty env failing closed. One existing Starlette TestClient deprecation warning remains.
- `node tests/test_bridge.mjs` — PASS.
- Local Chrome at mobile width — PASS for `demo` and `demo10`: env-password login, token bridge and logout. Password absent from public config; fixture HTTP route remains 404.
- Compile, example dotenv parsing (six active keys), Markdown links and diff whitespace checks — PASS.
- Real Go integration and Vercel deployment remain NOT_EVALUATED. Telemetry workflow-start timed out; no publisher acceptance or complete lifecycle tracking verified.
