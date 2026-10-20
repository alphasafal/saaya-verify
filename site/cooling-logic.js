// Educational projection of firmware/include/controller.h, after its 3 s startup grace.
// Full-size motor capability and thermal performance are intentionally not inferred.
export function evaluateCooling(input){
 const sensorValid=!input.sensorFault&&Number.isFinite(input.temp)&&Number.isFinite(input.rh)&&input.rh>=0&&input.rh<=100;
 // Mirrors autoRequest(): on at >=32 C, held until <31 C (bench demonstration band, not occupational).
 const autoOn=sensorValid&&(input.autoWasOn?input.temp>=31:input.temp>=32);
 const duty=input.mode==='manual'?70:(input.mode==='auto'&&autoOn?50:0);
 const rpm=input.power?Math.max(0,Number(input.rpm)||0):0;
 return {duty,rpm,sensorValid,fanFault:duty>0&&rpm<100,rotating:rpm>0,
  evaporation:input.rh>=80?'limited':'humidity-dependent',
  roofDelta:input.roof-input.temp,waterActuator:false,airSpeed:null,predictedTemperatureDrop:null};
}
