# SIGVERN RF — rebrand checkpoint 1

Version: `2.0.0-beta.2-rebrand.1` · Based on OpenRF Platform `2.0.0-beta.2`.
This is a source checkpoint awaiting physical ESP32-S3 / MQTT / HA validation.
Deep Analyzer work has not started.

## Identity

| Item | New value |
| --- | --- |
| Firmware / HA device | SIGVERN RF |
| Default hostname / mDNS | `sigvern-rf` / `sigvern-rf.local` |
| Setup access point | `SIGVERN-RF-Setup` |
| MQTT client, HA device and discovery node ID | `sigvern_rf_<chipid>` |
| MQTT base topic | `sigvern/rf/sigvern_rf_<chipid>` |
| Unique IDs | `sigvern_rf_<chipid>_<function>` |
| Suggested entity ID example | `button.sigvern_rf_<chipid>_slot_1` |
| New backup extension / magic | `.sgrbackup` / `SGRBKP1\0` |

Entity IDs include the chip ID to avoid collisions between gateways. HA can keep
user overrides or add a suffix if an ID already exists. The firmware supplies
`default_entity_id`; it cannot force IDs in HA's registry.

Saved hostnames containing `openrf` migrate to `sigvern-rf` when loaded. Other
custom hostnames are preserved. Wi-Fi credentials, MQTT credentials, radio
profiles, slot paths, binary record layouts and slot magic values are preserved.
The new hostname is saved with the next configuration save; it is also migrated
again on boot or after restoring an old backup.

## Upgrade without losing settings or slots

1. Export a backup from the running OpenRF device and save it on your computer.
2. Prebuilt application and filesystem images are in `release/`. To rebuild
   from this complete source folder, use:
   `pio run -e esp32s3` and `pio run -e esp32s3 -t buildfs`.
3. Update the firmware **and** WebUI filesystem. Firmware-only OTA preserves the
   filesystem but leaves the old WebUI in place. Never erase the whole flash.
4. **A normal PlatformIO `uploadfs` replaces LittleFS, including config and slots.**
   After a filesystem upload, connect to `SIGVERN-RF-Setup`, open
   `http://192.168.4.1`, and restore the backup from step 1 in System → Backup.
   The device reboots with the saved network, radio and slot settings.
5. Open the device by its IP or new hostname, refresh the browser, and verify
   slot counts, names and radio settings against the backup.
6. Keep Home Assistant running and connected to the same MQTT broker. Allow
   roughly 60–75 seconds for the paced cleanup and discovery pass.
7. Update HA automations, dashboard references, MQTT publishers/subscribers and
   external API clients to the new identifiers. Test one known-protocol RX,
   Learned RAW RX, RAW TX and protocol TX on each enabled radio.
8. Export a new `.sgrbackup` and keep the original `.orfbackup` for rollback.

The rename itself does not format storage or reset settings. Old `.orfbackup`
containers remain readable. New `.sgrbackup` files are not readable by the old
OpenRF firmware; use the original backup when rolling back.

## Discovery migration

Each MQTT connection and HA `homeassistant/status = online` message starts an
idempotent cleanup of the exact 200 discovery topics from the supplied beta.2
baseline: five fixed records, five records per RAW slot, three per RX slot.
All slots are covered, including empty/disabled ones. Retained empty payloads
remove the old records. A failed publish is retried at the same step. Disconnect
and reboot restart the pass. New discovery waits until cleanup has been sent.
Cleanup also runs when HA discovery is disabled, but no new records are created.
No permanent completion flag prevents cleanup on a different broker.

MQTT publish success means the client accepted the transmission, not a broker
acknowledgment (PubSubClient publishes at QoS 0). Reconnection and HA birth repeat
cleanup. The physical test must verify the broker and HA result. If HA was
stopped, start it and let its birth message trigger another pass.

Only topics belonging to this chip's known beta.2 discovery namespace are
removed. Manually configured entities or records from other chip IDs/custom
firmwares require manual removal. Old non-discovery retained state topics are
not bulk-deleted. Old automation references cannot be rewritten by firmware.

No per-frame RSSI/pulse-count HA sensors are added. Existing actionable RF event
logic and the existing MQTT diagnostic stream are unchanged.

Reference: https://www.home-assistant.io/integrations/mqtt/

## Branding assets and history

The supplied PNG is retained unchanged in `assets/sigvern-rf-logo.png`.
The compact SVG wraps that PNG and displays only its emblem through a viewport;
the header uses live SIGVERN text and a separate cyan RF label. The original
raster's texture/transparency is retained; this is not a newly redrawn logo.

Historical release notes, historical changelog entries and baseline screenshots
remain historical evidence. Active documentation, UI, board metadata, source
identifiers and statistics labels use SIGVERN. Binary slot signatures remain
unchanged for storage compatibility. No GitHub repository, release or domain
has been renamed/published remotely in this task.

## Physical acceptance gate

- Firmware and filesystem build/upload; no boot loop, both CC1101s healthy.
- Original backup restores Wi-Fi/MQTT, profiles, 30 RAW / 15 RX slot capacity.
- New backup round-trip restores the same data.
- Old discovery records disappear and only SIGVERN active entities remain.
- MQTT reconnect, HA restart and gateway reboot repeat migration safely.
- No discovery-driven RF transmission; known/unknown/ambiguous routing unchanged.
- 433/868 RX/TX, RAW Learn/Replay, dedup, live UI and OTA remain functional.

Do not freeze this checkpoint as hardware-PASS until these checks are complete.
