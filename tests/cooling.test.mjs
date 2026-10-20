import {test} from 'node:test';
import assert from 'node:assert/strict';
import {evaluateCooling} from '../site/cooling-logic.js';
const base={temp:36,rh:60,roof:48,rpm:640,mode:'manual',power:true,sensorFault:false,water:true};
test('manual remains 70 even with a sensor fault; no invented cooling result',()=>{
 const x=evaluateCooling({...base,sensorFault:true});assert.equal(x.duty,70);assert.equal(x.sensorValid,false);assert.equal(x.predictedTemperatureDrop,null);
});
test('optional bench auto threshold and invalid-sensor inhibition',()=>{
 assert.equal(evaluateCooling({...base,mode:'auto',temp:31.9}).duty,0);
 assert.equal(evaluateCooling({...base,mode:'auto',temp:32}).duty,50);
 assert.equal(evaluateCooling({...base,mode:'auto',sensorFault:true}).duty,0);
 assert.equal(evaluateCooling({...base,mode:'auto',temp:31.5,autoWasOn:true}).duty,50);
 assert.equal(evaluateCooling({...base,mode:'auto',temp:30.9,autoWasOn:true}).duty,0);
});
test('humidity and roof observations do not invent firmware actuators',()=>{
 const x=evaluateCooling({...base,rh:90,roof:70,water:false});assert.equal(x.duty,70);assert.equal(x.evaporation,'limited');assert.equal(x.waterActuator,false);
});
test('tach feedback after startup is distinct from command and airflow',()=>{
 const x=evaluateCooling({...base,rpm:0});assert.equal(x.duty,70);assert.equal(x.fanFault,true);assert.equal(x.rotating,false);assert.equal(x.airSpeed,null);
});
test('fan power loss stops animation even if ESP32 commands fan; USB remains separate',()=>{
 const x=evaluateCooling({...base,power:false});assert.equal(x.duty,70);assert.equal(x.rotating,false);assert.equal(x.fanFault,true);
});
test('full-size reference fan does not stop at 0 percent command',()=>{
 const x=evaluateCooling({...base,mode:'off',rpm:350});assert.equal(x.duty,0);assert.equal(x.rotating,true);assert.equal(x.fanFault,false);
});
test('fan-benefit screen: auto stops where a fan may add heat; manual is never blocked',()=>{
 assert.equal(evaluateCooling({...base,mode:'auto',temp:39.5,autoWasOn:true}).duty,0);
 assert.equal(evaluateCooling({...base,mode:'auto',temp:38.7}).duty,0);
 assert.equal(evaluateCooling({...base,mode:'auto',temp:38.4}).duty,50);
 const m=evaluateCooling({...base,mode:'manual',temp:41});assert.equal(m.duty,70);assert.equal(m.fanAdvice,'avoid');
 assert.equal(evaluateCooling({...base,temp:37.5}).fanAdvice,'caution');
 assert.equal(evaluateCooling({...base,sensorFault:true}).fanAdvice,'unknown');
});
