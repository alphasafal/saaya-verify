// Exposes the UNMODIFIED firmware control rules (firmware/include/controller.h) to the browser
// simulator as WebAssembly, so the simulator runs exactly the code that runs on the ESP32.
// Build: sh scripts/build_sim_wasm.sh  ->  site/sim/controller.wasm
#include "../include/controller.h"
static ControlState s_out;
extern "C" {
__attribute__((export_name("step")))
void step_js(int pHelp,int pFault,int pDuty,unsigned pStarted,int help,int ack,int manual,int automatic,int sensorFault,unsigned now,float rpm){
 ControlState p;p.help=pHelp;p.fanFault=pFault;p.duty=pDuty;p.started=pStarted;
 ControlInput i;i.help=help;i.ack=ack;i.manual=manual;i.automatic=automatic;i.sensorFault=sensorFault;i.now=now;i.rpm=rpm;
 s_out=step(p,i);
}
__attribute__((export_name("outHelp"))) int outHelp(){return s_out.help;}
__attribute__((export_name("outFault"))) int outFault(){return s_out.fanFault;}
__attribute__((export_name("outDuty"))) int outDuty(){return s_out.duty;}
__attribute__((export_name("outStarted"))) unsigned outStarted(){return s_out.started;}
__attribute__((export_name("autoRequest"))) int autoRequest_js(int wasOn,float t){return autoRequest(wasOn,t);}
__attribute__((export_name("fanAdvice"))) int fanAdvice_js(float t){return fanAdvice(t);}
__attribute__((export_name("constants"))) float constants(int k){const float c[]={AUTO_ON_C,AUTO_OFF_C,FAN_CAUTION_C,FAN_AVOID_C,FAN_RESUME_C};return (k>=0&&k<5)?c[k]:NAN;}
}
