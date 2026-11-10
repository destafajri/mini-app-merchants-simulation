# Integration documentation

Audience: frontend engineers building the VIA Mini App and backend engineers connecting the merchant identity to the Mini App API. Version: **simulator bridge v1**, reviewed 2026-11-10.

1. [Architecture and responsibilities](architecture.md) — trust boundaries and end-to-end sequence.
2. [Frontend integration guidelines](frontend-integration.md) — embedding, SDK, message contract, token lifecycle, errors and acceptance checklist.
3. [Backend integration guidelines](backend-integration.md) — JWT verification, merchant registration, BFF forwarding, ownership, and integration validation.
4. [Merchant HTTP API](api-reference.md) — paths, inputs, outputs, status codes and examples.
5. [Configuration and deployment](deployment.md) — local setup, environment reference, Vercel, tunnel, keys and limitations.
6. [Troubleshooting](troubleshooting.md) — symptoms, causes and checks.

This documentation specifies the implemented simulator interface. It does not establish downstream contract approval or claim a successful deployed integration. Example domains and identities are placeholders. Do not use real customer data in this simulator.

[Local verification record](verification.md) and [mobile screenshot](merchant-mobile.png) describe the actual checked scope and outstanding integration checks.
