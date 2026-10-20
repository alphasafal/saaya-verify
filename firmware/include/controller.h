#pragma once
#include <stdint.h>
#include <math.h>
// Pure control logic, shared by the ESP32 firmware and the native unit test.
// Bench demonstration band only -- NOT an occupational threshold.
constexpr float AUTO_ON_C=32.0f, AUTO_OFF_C=31.0f;
struct ControlInput {bool help=false,ack=false,manual=false,automatic=false,sensorFault=false; uint32_t now=0; float rpm=0;};
struct ControlState {bool help=false,fanFault=false; int duty=0;uint32_t started=0;};
// Hysteresis: start at >=32 C, keep running until <31 C; unknown temperature never requests.
inline bool autoRequest(bool wasOn,float temp){
 if(!isfinite(temp))return false;
 return wasOn?temp>=AUTO_OFF_C:temp>=AUTO_ON_C;
}
inline ControlState step(ControlState prev,ControlInput in){
 ControlState out;
 out.help=(prev.help&&!in.ack)||in.help;            // help wins over a simultaneous ack
 out.duty=in.manual?70:(in.automatic&&!in.sensorFault?50:0);
 out.started=(prev.duty>0&&out.duty>0)?prev.started:in.now;
 out.fanFault=out.duty>0&&uint32_t(in.now-out.started)>=3000&&in.rpm<100;
 return out;
}
