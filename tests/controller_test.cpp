#include "../firmware/include/controller.h"
#include <cassert>
#include <iostream>
int main(){ControlState s;ControlInput i;i.help=true;i.manual=true;i.sensorFault=true;s=step(s,i);assert(s.help&&s.duty==70&&!s.fanFault);i.help=false;i.now=3100;s=step(s,i);assert(s.help&&s.fanFault);i.ack=true;i.rpm=3000;s=step(s,i);assert(!s.help&&!s.fanFault);i.manual=false;i.automatic=true;s=step(s,i);assert(s.duty==0);i.sensorFault=false;s=step(s,i);assert(s.duty==50);s.started=0xfffffff0;s.duty=70;i.manual=true;i.now=4000;i.rpm=0;assert(step(s,i).fanFault);std::cout<<"Controller tests passed: latch, manual, fault, startup, rollover\n";}
