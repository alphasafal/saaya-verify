// Educational projection of firmware/include/controller.h, after its 3 s startup grace.
// Full-size motor capability and thermal performance are intentionally not inferred.
export function evaluateCooling(input){
 const sensorValid=!input.sensorFault&&Number.isFinite(input.temp)&&Number.isFinite(input.rh)&&input.rh>=0&&input.rh<=100;
 // Mirrors autoRequest(): on at >=32 C, held until <31 C (bench demonstration band, not occupational).
 // Auto also stops at >=39 C where a fan may add heat (Morris 2021; WHO >40 C); restarts below 38.5 C.
 const autoOn=sensorValid&&(input.autoWasOn?input.temp>=31&&input.temp<39:input.temp>=32&&input.temp<38.5);
 const fanAdvice=!sensorValid?'unknown':input.temp>=39?'avoid':input.temp>=37?'caution':'ok';
 const duty=input.mode==='manual'?70:(input.mode==='auto'&&autoOn?50:0);
 const rpm=input.power?Math.max(0,Number(input.rpm)||0):0;
 return {duty,fanAdvice,rpm,sensorValid,fanFault:duty>0&&rpm<100,rotating:rpm>0,
  evaporation:input.rh>=80?'limited':'humidity-dependent',
  roofDelta:input.roof-input.temp,waterActuator:false,airSpeed:null,predictedTemperatureDrop:null};
}
