# Rebrand checkpoint validation

The results below apply to version 2.0.0-beta.2-rebrand.1.

- `python tests/run_rebrand_host.py`: PASS. Compiles the production cleanup loop
  and topic enumerator; checks all 200 legacy topics, retained empty payloads,
  pacing, failed-publish retry, disconnect and restart, plus new discovery gating.
- `python tests/run_step40_fix6_host.py`: PASS. Includes the existing FIX5/FIX4
  suites, RAW matching/dedup, NVKP01 negative samples and protocol integration.
- Compared 81 baseline implementation/header files with the uploaded ZIP:
  exact equality after branding-token substitutions and newline normalization.
  RF capture, normalization, decoders, timing, TX, matcher and storage record
  implementation have no other changes.
- `node --check data/app.js`: PASS.
- HTML IDs are unique; JavaScript element references resolve; local UI assets
  exist. API download links were checked as routes, not filesystem assets.
- `pio run -e esp32s3`: PASS. RAM 53,884 / 327,680 bytes (16.4%);
  firmware program size 1,028,481 / 6,553,600 bytes (15.7%).
  Espressif32 7.1.3, Arduino framework 4.20017.260907+sha.dcc1105b,
  RadioLib 7.7.1, PubSubClient 2.8.0, ArduinoJson 7.4.3.
- `pio run -e esp32s3 -t buildfs`: PASS. LittleFS image: 3,538,944 bytes; all four WebUI assets included.
- Browser visual QA: PASS at 1440×950 and 390×844. No horizontal page
  overflow; emblem and separated RF wordmark remain visible. Screenshots in
  `docs/preview/` use mocked empty API responses, not live hardware data.
- Maintainer-reported physical checks: PASS for the tested rebrand checkpoint.
  Normal operation, removal of old HA entities, appearance of SIGVERN entities,
  restart behavior and backup/restore were reported working.
  This report does not individually certify every validation-checklist item.
- Final 2.0.0-beta.3 firmware and filesystem build/verification: PENDING.
  The build sizes above belong to the rebrand checkpoint.
