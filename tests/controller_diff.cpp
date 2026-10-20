// Native reference for tests/sim-wasm.test.mjs: reads cases on stdin, prints controller.h results,
// so the WebAssembly build used by site/simulator.html is checked against the C++ compiled natively.
#include "../firmware/include/controller.h"
#include <cstdio>
int main(){
 int ph,pf,pd,h,a,m,au,sf;unsigned ps,now;float rpm,t;int wo;
 while(std::scanf("%d %d %d %u %d %d %d %d %d %u %f %d %f",&ph,&pf,&pd,&ps,&h,&a,&m,&au,&sf,&now,&rpm,&wo,&t)==13){
  ControlState p;p.help=ph;p.fanFault=pf;p.duty=pd;p.started=ps;
  ControlInput i;i.help=h;i.ack=a;i.manual=m;i.automatic=au;i.sensorFault=sf;i.now=now;i.rpm=rpm;
  ControlState o=step(p,i);
  std::printf("%d %d %d %u %d %d\n",o.help,o.fanFault,o.duty,o.started,autoRequest(wo,t),fanAdvice(t));
 }
}
