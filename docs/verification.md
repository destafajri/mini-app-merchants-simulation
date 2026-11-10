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
