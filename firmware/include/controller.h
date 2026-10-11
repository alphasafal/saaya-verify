#pragma once
#include <stdint.h>
struct ControlInput {bool help=false,ack=false,manual=false,automatic=false,sensorFault=false; uint32_t now=0; float rpm=0;};
struct ControlState {bool help=false,fanFault=false; int duty=0;uint32_t started=0;};
inline ControlState step(ControlState prev,ControlInput in){
 ControlState out;
 out.help=(prev.help&&!in.ack)||in.help;
 out.duty=in.manual?70:(in.automatic&&!in.sensorFault?50:0);
 out.started=(prev.duty>0&&out.duty>0)?prev.started:in.now;
 out.fanFault=out.duty>0&&uint32_t(in.now-out.started)>=3000&&in.rpm<100;
 return out;
}
