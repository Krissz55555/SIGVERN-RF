#pragma once
#include <stdint.h>
#include <stdio.h>

// Enumerate every discovery topic emitted by the beta.2 baseline, including
// empty/disabled slots. No filesystem reads or RF work is needed for cleanup.
inline uint16_t legacyDiscoveryCount(uint8_t rawSlots, uint8_t rxSlots) {
  return 5U + rawSlots * 5U + rxSlots * 3U;
}
inline bool legacyDiscoveryTopic(char* out, size_t size, const char* chip,
                                uint16_t step, uint8_t rawSlots, uint8_t rxSlots) {
  if (step >= legacyDiscoveryCount(rawSlots, rxSlots)) return false;
  const char* domain;
  char object[48];
  if (step < 5U) {
    static const char* objects[] = {"learn_next", "learn_state", "status", "rx_pulses", "rx_rssi"};
    domain = step == 0U ? "button" : "sensor";
    snprintf(object, sizeof(object), "%s", objects[step]);
  } else if (step < 5U + rawSlots * 5U) {
    const unsigned n = (step - 5U) / 5U + 1U;
    const unsigned item = (step - 5U) % 5U;
    domain = item < 3U ? "button" : item == 3U ? "device_automation" : "binary_sensor";
    if (item < 3U) snprintf(object, sizeof(object), "slot_%u%s", n,
                          item == 1U ? "_relearn" : item == 2U ? "_delete" : "");
    else snprintf(object, sizeof(object), "raw_slot_%u", n);
  } else {
    const unsigned relative = step - 5U - rawSlots * 5U;
    const unsigned item = relative % 3U;
    domain = item == 0U ? "device_automation" : item == 1U ? "binary_sensor" : "button";
    snprintf(object, sizeof(object), "rx_slot_%u%s", relative / 3U + 1U, item == 2U ? "_send" : "");
  }
  const int n = snprintf(out, size, "homeassistant/%s/openrf_%s/%s/config", domain, chip, object);
  return n > 0 && static_cast<size_t>(n) < size;
}
