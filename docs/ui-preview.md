# UI preview and verification

The Murid Wukong simulator uses a dark charcoal surface, mint accents, an account card and a service grid inspired by finance applications. All assets are native HTML/CSS and inline SVG; no UI framework was added. Brand and icons are original simulator assets, not GoPay/DANA/Stockbit branding.

## Screenshots

Synthetic user `demo-user-001` only; no passwords, JWTs or customer data are shown.

| Screen | Mobile | Desktop |
| --- | --- | --- |
| Login | [390 px](login-mobile.png) | [1440 px](login-desktop.png) |
| Merchant home | [390 px](merchant-mobile.png) | [1440 px](merchant-desktop.png) |
| VIA receiver container | [390 px](container-mobile.png) | [1440 px](container-desktop.png) |

The bottom navigation stays fixed to the viewport on mobile. In a full-page screenshot it appears at its original viewport position, over the longer captured page.

## Behavior

- Password visibility toggle, pending login button and specific invalid-credential/origin/configuration messages.
- Live account display from `/api/auth/me`; no simulated wallet balance is presented as actual funds.
- VIA launch is enabled only when the FE URL is configured. Other service shortcuts are explicitly disabled illustrations.
- Mobile navigation scrolls to home/services/account controls. Reduced-motion preference disables smooth scrolling and transitions.
- Keyboard focus indicators, labeled form controls, error announcements, skip link, and focus restoration after closing the container.
- Receiver demo uses the same visual palette and still hides JWT contents. Its existing `BRIDGE_OK` result format is preserved.
- Merchant backend auth, JWT/JWKS and the exact-origin bridge protocol remain unchanged.

## Local checks

Verified with Chrome at 390 × 844 and 1440 × 1000: incorrect login, password toggle, valid login, account identity, embedded receiver, back, focus restoration and logout. Also checked 320 px width for horizontal overflow on login and home, forged origin/source messages (no token call), and mobile navigation with reduced motion. Screenshots document the final UI; they do not establish deployed FE or downstream integration.
