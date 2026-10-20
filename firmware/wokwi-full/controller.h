#pragma once
#include <stdint.h>
#include <math.h>
// Pure control logic, shared by the ESP32 firmware and the native unit test.
// Bench demonstration band only -- NOT an occupational threshold.
constexpr float AUTO_ON_C=32.0f, AUTO_OFF_C=31.0f;
// Fan-benefit screen (air temperature). Morris et al. 2021 (Lancet Planet Health) propose fan-use
// ceilings of 39 C (young healthy), 38 C (>65 y), 37 C (>65 y on anticholinergics); WHO says fans
// heat the body above 40 C; Gagnon et al. 2016 found no benefit for older adults at 42 C.
constexpr float FAN_CAUTION_C=37.0f, FAN_AVOID_C=39.0f, FAN_RESUME_C=38.5f;
enum FanAdvice {FAN_OK=0,FAN_CAUTION=1,FAN_AVOID=2,FAN_UNKNOWN=3};
inline FanAdvice fanAdvice(float airC){
 if(!isfinite(airC))return FAN_UNKNOWN;
 return airC>=FAN_AVOID_C?FAN_AVOID:(airC>=FAN_CAUTION_C?FAN_CAUTION:FAN_OK);
}
struct ControlInput {bool help=false,ack=false,manual=false,automatic=false,sensorFault=false; uint32_t now=0; float rpm=0;};
struct ControlState {bool help=false,fanFault=false; int duty=0;uint32_t started=0;};
// Hysteresis: start at >=32 C, keep running until <31 C; unknown temperature never requests.
// Automatic mode also stops where a fan may add heat (>=39 C) and only restarts below 38.5 C.
// Manual mode is never blocked: the worker decides, the display warns.
inline bool autoRequest(bool wasOn,float temp){
 if(!isfinite(temp))return false;
 return wasOn?(temp>=AUTO_OFF_C&&temp<FAN_AVOID_C):(temp>=AUTO_ON_C&&temp<FAN_RESUME_C);
}
inline ControlState step(ControlState prev,ControlInput in){
 ControlState out;
 out.help=(prev.help&&!in.ack)||in.help;            // help wins over a simultaneous ack
 out.duty=in.manual?70:(in.automatic&&!in.sensorFault?50:0);
 out.started=(prev.duty>0&&out.duty>0)?prev.started:in.now;
 out.fanFault=out.duty>0&&uint32_t(in.now-out.started)>=3000&&in.rpm<100;
 return out;
}
