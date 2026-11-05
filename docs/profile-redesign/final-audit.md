# Obsidian Detonation — Final Audit

## Scope

Restore the original Nothrovo/Reze colorful and animated identity while keeping the profile structured, native-text first, mobile-safe, and grounded in the five current pinned repositories. The `anggasspm` profile was used only as a reference for visual rhythm and density; no font, palette, section names, or block cadence was copied.

## Visual direction

- Theme: **Obsidian Detonation**
- Display language: native GitHub headings plus one atmospheric Space Mono typing SVG
- Palette: obsidian `#0e0a14`, crimson `#ff4b72`, lilac `#b388ff`
- Hero: Bomb Devil/Reze explosion GIF, first image and only GIF, rendered at `440px` desktop and responsively reduced on mobile
- Visual rhythm: three signal badges near the intro, two shallow crimson/lilac dividers, eight capability badges, and three contact badges
- Critical identity, role, project, capability, and contact information remains native text or native Markdown links

## Before and after

| Metric | Original profile | Obsidian Detonation |
|---|---:|---:|
| README size | 8,703 bytes | approximately 5.4 KB |
| Manual `<br>` occurrences | 36 | 0 |
| Typing SVG occurrences | 9 | 1 atmospheric line |
| GIF occurrences | 2 | 1 |
| Shields.io occurrences | 21 | 14 |
| Capsule accents | 1 | 2 shallow dividers |
| External stats/streak cards | 3 | 0 |
| Featured projects | 0 | 5 pinned repositories |

## Final featured repositories

The Selected Work section follows the current GitHub pinned-repository source of truth:

1. `Nothrovo/Solythis-DnD`
2. `Nothrovo/Damsel-and-Desire`
3. `Nothrovo/Arbiter`
4. `Nothrovo/Neuropetra-IP`
5. `HETSHI-PLAY/DIPTERA`

`MedChain` is not featured. Its relevant SHA-256 and RSA experience remains represented as the general capability **Data Integrity & Cryptography**.

## Verification evidence

- `python scripts/validate_profile_readme.py README.md` — PASS
- `python -m unittest discover -s tests -q` — 21 tests PASS
- `python -m py_compile scripts/validate_profile_readme.py tests/test_validate_profile_readme.py` — PASS
- `git diff --check` — PASS
- All 18 visual assets — HTTP 200
- Explosion GIF — HTTP 200, image/gif, 480×270 px, 40 frames, 1.58 MiB
- First rendered image — exact Bomb Devil explosion GIF
- Animated protocol — `Evidence first. Detonate.` visible and unclipped after animation
- Horizontal overflow — none at 320, 430, and 1280 px
- Desktop visual acceptance — FINAL-READY
- 430 px visual acceptance — FINAL-READY
- 320 px protocol crop — PASS

## Final screenshot artifacts

- Desktop: `/home/nothrovo/.hermes/profiles/calypso/cache/scratch/readme-color-final/1280.png`
- Mobile 430 px: `/home/nothrovo/.hermes/profiles/calypso/cache/scratch/readme-color-final/430.png`
- Mobile 320 px: `/home/nothrovo/.hermes/profiles/calypso/cache/scratch/readme-color-final/320.png`

## Recovery

The pre-redesign state remains preserved at branch:

`backup/profile-before-nocturne-dossier`

Commit:

`94a570de4425ead27329994200f7b8fbc6610a09`
