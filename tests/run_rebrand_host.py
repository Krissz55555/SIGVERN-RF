#!/usr/bin/env python3
"""Compile the production legacy-discovery enumerator and cleanup loop on host."""
from pathlib import Path
import subprocess
root = Path(__file__).resolve().parents[1]
build = root / 'tests/.build_rebrand'
build.mkdir(exist_ok=True)
src = (root / 'src/mqtt.cpp').read_text()
loop = src[src.index('void processLegacyDiscovery() {'):src.index('\nvoid processDiscovery() {')]
test = r'''
#include <cassert>
#include <string>
#include <set>
#include <vector>
#include "legacy_discovery.h"
using String = std::string;
constexpr uint8_t SIGVERN_SLOT_COUNT=30, SIGVERN_RX_SLOT_COUNT=15;
constexpr uint32_t DISCOVERY_STEP_DELAY_MS=150;
bool legacyCleanupPending=true;
uint16_t legacyCleanupStep=0;
uint32_t legacyCleanupNextMs=0, clockMs=0;
uint32_t millis(){return clockMs;}
String sigvernChipIdHex(){return "abc123";}
#define F(x) x
struct {void println(const char*){}} Serial;
struct MockClient {
 bool online=true, accept=true;
 std::vector<std::string> sent;
 bool connected(){return online;}
 bool publish(const char* topic,const char* payload,bool retained){
  assert(retained && std::string(payload).empty());
  if (!accept) return false;
  sent.emplace_back(topic);return true;
 }
} client;
'''+loop+r'''
int main(){
 std::set<std::string> expected,actual;
 auto add=[&](std::string d,std::string o){expected.insert("homeassistant/"+d+"/openrf_abc123/"+o+"/config");};
 add("button","learn_next");
 for (auto o:{"learn_state","status","rx_pulses","rx_rssi"})add("sensor",o);
 for(int i=1;i<=30;i++){
  std::string n=std::to_string(i);
  for(auto suffix:{"","_relearn","_delete"})add("button","slot_"+n+suffix);
  for(auto d:{"device_automation","binary_sensor"}){
   add(d,"raw_slot_"+n);if(i<=15)add(d,"rx_slot_"+n);
  }
  if(i<=15)add("button","rx_slot_"+n+"_send");
 }
 char topic[160];
 for(unsigned i=0;i<legacyDiscoveryCount(30,15);i++){
  assert(legacyDiscoveryTopic(topic,sizeof(topic),"abc123",i,30,15));
  assert(actual.insert(topic).second);
 }
 assert(actual==expected && actual.size()==200);
 assert(!legacyDiscoveryTopic(topic,sizeof(topic),"abc123",200,30,15));
 assert(!legacyDiscoveryTopic(topic,8,"abc123",0,30,15));
 client.online=false;processLegacyDiscovery();assert(legacyCleanupStep==0);
 client.online=true;client.accept=false;processLegacyDiscovery();assert(legacyCleanupStep==0);
 client.accept=true;clockMs=150;processLegacyDiscovery();assert(legacyCleanupStep==1);
 processLegacyDiscovery();assert(legacyCleanupStep==1); // pacing
 while(legacyCleanupPending){clockMs+=150;processLegacyDiscovery();}
 assert(client.sent.size()==200);
 assert(std::set<std::string>(client.sent.begin(),client.sent.end())==expected);
 // Restart the cleanup as the real reconnect/birth path does.
 legacyCleanupPending=true;legacyCleanupStep=0;legacyCleanupNextMs=clockMs;
 processLegacyDiscovery();assert(client.sent.back()==client.sent.front());
}
'''
file=build/'migration.cpp';file.write_text(test)
subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror','-I',str(root/'include'),str(file),'-o',str(build/'migration')],check=True)
subprocess.run([str(build/'migration')],check=True)
print('PASS: all 200 legacy topics, unique enumeration, empty retained payloads, retry, pacing, disconnect, restart')
assert 'legacyCleanupPending || !discoveryPending' in src
assert 'domain + "." + doc["unique_id"].as<String>()' in src
assert 'baseTopic = "sigvern/rf/" + deviceIdentifier();' in src
print('PASS: new discovery gate, stable identity, explicit entity IDs')
