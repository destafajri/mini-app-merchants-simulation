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

## Dark finance UI refresh

The merchant login, dashboard and receiver now use a charcoal/mint theme with original Murid Wukong branding, service icons and responsive layouts. See [UI preview](ui-preview.md) for final screenshots and browser coverage. No backend auth, user configuration, downstream ownership or bridge wire contract changes.

- `python -m pytest -q` — PASS, 7 tests; existing Starlette TestClient deprecation warning remains.
- `node tests/test_bridge.mjs` — PASS.
- Chrome 390 × 844 and 1440 × 1000 — PASS: incorrect login, password visibility toggle, correct login, account ID, receiver token, receiver retry, container back, focus restoration and logout.
- Chrome 320 px — login and dashboard have no horizontal overflow. Mobile navigation and reduced-motion path PASS. Forged origin/source messages trigger no token request.
- Documentation links and `git diff --check` — PASS.
- Screenshots use synthetic profile data only. External FE, downstream integration and deployed Vercel revision were not evaluated during this UI task.
- Telemetry workflow-start timed out at the existing publisher; lifecycle tracking is incomplete. No automatic retries.


## Theme and language preferences

Added light/dark and ID/EN selectors with browser preference persistence and shared translations. `/ui-preferences.js` is a public UI asset; auth and bridge payloads are unchanged. No Go service changes.

- `python -m pytest -q` — PASS, 7 tests including the new UI asset route. Existing Starlette TestClient deprecation warning remains.
- `node tests/test_bridge.mjs` and `node tests/test_preferences.mjs` — PASS. Preference checks cover system defaults, translations, persistence, invalid stored values, storage sync and blocked storage.
- Chrome at mobile 390 × 844 and desktop 1440 × 1000 — all four theme/language combinations PASS for reload persistence, translated failed login, password toggle, successful login, receiver token/retry and logout, with no horizontal overflow or uncaught JavaScript errors.
- Chrome 320 px light/EN — login/home overflow PASS. Live error translation, cross-tab and active receiver sync, and controls with blocked localStorage PASS.
- Public screenshots contain synthetic profile data only. External FE theme propagation is not implemented; external integration and deployed Vercel revision were not evaluated.
- Telemetry workflow-start timed out at the configured publisher; lifecycle tracking remains incomplete, without automatic retries.


## Header preference toggles

Replaced the appearance/language dropdowns with labeled two-position switches and a sliding active indicator. Existing saved preferences remain compatible. Screenshot galleries now show the toggle controls.

- `python -m pytest -q` — PASS, 7 tests; existing Starlette TestClient deprecation warning remains.
- `node tests/test_bridge.mjs` and `node tests/test_preferences.mjs` — PASS. Updated preference tests exercise real click listeners, repeated toggles, checked states, persistence, storage sync and blocked storage.
- Local Chrome at 320, 390 and 1440 px — PASS for all four theme/language combinations: click, Enter/Space keyboard activation, reload persistence, login, switches after login, embedded receiver, logout and horizontal overflow. Switch hit areas are at least 44 px high. No uncaught page errors.
- Chrome with blocked localStorage — toggle clicks PASS. Screenshots contain synthetic account data only.
- External FE and deployed Vercel revision were not evaluated. Telemetry workflow-start timed out at the existing publisher; lifecycle tracking remains incomplete without retry.


## GoPay-like auth_code mode

Added `POST /api/gopay/auth-code`, `POST /v1/mini-apps/authorizations/token`, `getAuthCode()` in the SDK and `miniapp.authcode.request/response` handling in the container page. The JWT endpoints, JWKS and `getAccessToken()` are unchanged. Reviewed 2026-11-12; local results only.

- `python -m pytest -q` — PASS, 15 tests (the 7 existing plus 8 new): issuance happy path, unauthenticated/CSRF refusal, exchange returning the right user ID, `Request-Id` echo, wrong/missing/malformed Basic credential (401), unset or empty credential env (503), tampered/truncated/oversized/invalid-body codes (uniform 400), expiry at 290 s accepted and 301 s refused using the same signer-timestamp patch as the session expiry test, `Request-Id`/`Debug-Id` validation, login cookie not accepted as a code and vice versa, code and token not decodable as each other, no credential/code echo, `frame-ancestors`/`no-store` present and no CORS headers, JWT mode still working with the credential unset. The setup test also checks the generated credential is present, random and not printed. Existing Starlette TestClient deprecation warning remains.
- `node tests/test_bridge.mjs` — PASS (unchanged). `node tests/test_bridge_authcode.mjs` — PASS: forged origin, wrong source, wrong request ID, wrong response type, malformed or oversized payloads ignored; success, error, timeout, listener cleanup and standalone failure.
- `node tests/test_preferences.mjs` — PASS.
- `python -m compileall -q app.py tools tests`, syntax check of the inline module script in `public/index.html`, relative Markdown link check of the touched docs — PASS.
- A throwaway Node harness (not committed) ran the container page script with stubbed DOM/fetch: a valid `miniapp.authcode.request` and `miniapp.auth.request` from the frame origin/window each produced exactly one API call and one reply to the exact origin; wrong origin, wrong source, over-long request ID, non-string or prototype-name types and null data caused no call — PASS. No real browser was used for this feature.
- NOT VERIFIED: behavior against the real GoPay/Midtrans service (the simulator follows the documented shape only); the Mini App server and Nuxt frontend consuming this contract; a deployed Vercel revision; replay protection (none by design on serverless); rate limiting of the exchange endpoint (none).

### Local end to end with `bevia-miniapp-service` and the Nuxt frontend (2026-11-12)

Run locally with this simulator on port 8000, the Mini App service on branch `feat/authcode-session` against a throwaway PostgreSQL and the workspace mock Product/Order/PG, and the MyPertamina frontend in `authcode` mode on port 3000. Throwaway secrets were generated for the run and are not recorded here.

- A scripted run of 26 checks — PASS 26/26: sim login, `POST /api/gopay/auth-code` (200, `expiresIn` 300), `POST /api/v1/mini-app/{code}/session` (200, `Bearer`, `expires_in` within 900), catalog with the session (200, the three mock products) and history (200). Refusals: no bearer, tampered or garbage code, an unknown merchant, a `jwks_v1` merchant and a disabled `authcode_v1` merchant all 401, an empty code 400. The session of one merchant on another and a session with a flipped signature are 401. The host endpoint returned 401 for a wrong credential, 200 for the right one, and `AuthCode Not Found` for a bad code. A second exchange of the same code inside its 300 seconds succeeded, which confirms the documented lack of single-use enforcement.
- A browser run (Playwright Chromium): login as `demo`, open the Mini App from the container; the network log shows `POST /api/gopay/auth-code` 200, `POST /api/miniapp/gopay_sim_demo/session` 200, `GET /products` 200, and the catalog rendered three vouchers.
- A scan of the service and simulator logs for the auth code, the session token, the provider credential and the signing key found none of them.
- NOT VERIFIED: real GoPay/Midtrans behavior (single use, token reuse, error bodies), the Vercel deployments, staging, replay protection, rate limiting.
