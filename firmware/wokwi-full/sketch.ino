// SAAYA Node firmware for Wokwi. GENERATED from firmware/src/main.cpp by scripts/build_wokwi_full.py.
// Field build: automatic fan band enabled (same as `pio run -e esp32dev_field`).
#define SAAYA_BENCH_AUTO 1
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_SHT31.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_INA219.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <ArduinoJson.h>
#include <Preferences.h>
#include <esp_task_wdt.h>
#include "controller.h"
#ifndef SAAYA_WIFI
#define SAAYA_WIFI 0
#endif
#if SAAYA_WIFI
// Optional LAN uplink (off by default). Runs in its own task on core 0 so that Wi-Fi or HTTP
// stalls can never delay buttons, the help latch or fan control on core 1.
#include <WiFi.h>
#include <HTTPClient.h>
struct UplinkFrame {char json[768];};
static QueueHandle_t uplinkQueue=nullptr;
void uplinkTask(void*){
 UplinkFrame f;
 for(;;){
  if(xQueueReceive(uplinkQueue,&f,portMAX_DELAY)!=pdTRUE)continue;
  if(WiFi.status()!=WL_CONNECTED){WiFi.begin(SAAYA_WIFI_SSID,SAAYA_WIFI_PASS);for(int i=0;i<20&&WiFi.status()!=WL_CONNECTED;i++)vTaskDelay(pdMS_TO_TICKS(250));if(WiFi.status()!=WL_CONNECTED)continue;}
  HTTPClient http;http.setTimeout(1500);
  if(http.begin(SAAYA_API_URL)){http.addHeader("Content-Type","application/json");http.addHeader("X-Device-Token",SAAYA_DEVICE_TOKEN);http.POST((uint8_t*)f.json,strlen(f.json));http.end();}
 }
}
#endif
// 4-wire 12 V PWM fan. GPIO drives NPN open-collector stage, never motor power.
// LEDC and task-watchdog APIs changed in Arduino-ESP32 core 3 (used by Wokwi's online compiler);
// PlatformIO's espressif32@6.10.0 is core 2. Both are supported.
#if defined(ESP_ARDUINO_VERSION_MAJOR) && ESP_ARDUINO_VERSION_MAJOR >= 3
#define SAAYA_PWM_SETUP(pin) ledcAttach((pin),25000,8)
#define SAAYA_PWM_WRITE(pin,v) ledcWrite((pin),(v))
#define SAAYA_WDT_INIT() do{esp_task_wdt_config_t c={};c.timeout_ms=5000;c.idle_core_mask=0;c.trigger_panic=true;esp_task_wdt_reconfigure(&c);}while(0)
#else
#define SAAYA_PWM_SETUP(pin) do{ledcSetup(0,25000,8);ledcAttachPin((pin),0);}while(0)
#define SAAYA_PWM_WRITE(pin,v) ledcWrite(0,(v))
#define SAAYA_WDT_INIT() esp_task_wdt_init(5,true)
#endif
constexpr int PWM=25,TACH=34,WATER=35,MODE=32,HELP=33,ACK=27,LED=26,BUZZER=14,ROOF=4;
Adafruit_SHT31 outside,inside;Adafruit_SSD1306 display(128,64,&Wire,-1);Adafruit_INA219 powerMeter;
OneWire oneWire(ROOF);DallasTemperature roof(&oneWire);Preferences preferences;
ControlState state;bool autoOn=false;bool outOK=false,inOK=false,displayOK=false,powerOK=false,manual=false;
volatile uint32_t tachPulses=0;uint32_t lastSample=0,seq=0;char session[32];uint64_t uptimeMs=0;uint32_t previousMillis=0;
float rpm=0,temp=NAN,rh=NAN,ot=NAN,orr=NAN,roofTemp=NAN;bool sensorFault=true,haveRoofConversion=false;
void IRAM_ATTR tachRise(){tachPulses++;}
struct Button {explicit Button(int p):pin(p){} int pin;bool last=true,stable=true;uint32_t changed=0;bool press(uint32_t now){bool v=digitalRead(pin);if(v!=last){last=v;changed=now;}if(v!=stable&&uint32_t(now-changed)>=35){stable=v;return !v;}return false;}};
Button modeButton{MODE},helpButton{HELP},ackButton{ACK};
void finiteValue(JsonDocument &d,const char*key,float value){if(isfinite(value))d[key]=value;else d[key]=nullptr;}
void setup(){
 Serial.begin(115200);Wire.begin(21,22);Wire.setClock(50000);Wire.setTimeOut(50); // 50 kHz: margin for the metres-long reference-sensor cable
 pinMode(PWM,OUTPUT);digitalWrite(PWM,HIGH);SAAYA_PWM_SETUP(PWM);SAAYA_PWM_WRITE(PWM,255);
 for(int pin:{MODE,HELP,ACK})pinMode(pin,INPUT_PULLUP);
 pinMode(TACH,INPUT);pinMode(WATER,INPUT); // EXTERNAL 10k pull-ups to 3.3 V required on input-only pins.
 pinMode(LED,OUTPUT);pinMode(BUZZER,OUTPUT);attachInterrupt(digitalPinToInterrupt(TACH),tachRise,RISING);
 inOK=inside.begin(0x44);outOK=outside.begin(0x45);powerOK=powerMeter.begin();
 displayOK=display.begin(SSD1306_SWITCHCAPVCC,0x3C);if(displayOK){display.clearDisplay();display.display();}
 roof.begin();roof.setWaitForConversion(false);roof.requestTemperatures();
 preferences.begin("saaya",false);state.help=preferences.getBool("help",false);
 snprintf(session,sizeof(session),"boot-%08lx-%08lx",(unsigned long)esp_random(),(unsigned long)esp_random());
 SAAYA_WDT_INIT();esp_task_wdt_add(NULL);
#if SAAYA_WIFI
 uplinkQueue=xQueueCreate(1,sizeof(UplinkFrame));xTaskCreatePinnedToCore(uplinkTask,"uplink",8192,nullptr,1,nullptr,0);
#endif
}
void loop(){
 uint32_t now=millis();uptimeMs+=uint32_t(now-previousMillis);previousMillis=now;esp_task_wdt_reset();
 if(modeButton.press(now))manual=!manual;
 bool helpPressed=helpButton.press(now),ackPressed=ackButton.press(now),oldHelp=state.help;
 ControlInput input;input.help=helpPressed;input.ack=ackPressed;input.manual=manual;autoOn=SAAYA_BENCH_AUTO&&!manual&&!sensorFault&&autoRequest(autoOn,temp);input.automatic=autoOn;input.sensorFault=sensorFault;input.now=now;input.rpm=rpm;
 state=step(state,input);
 if(oldHelp!=state.help)preferences.putBool("help",state.help);
 SAAYA_PWM_WRITE(PWM,255-state.duty*255/100);digitalWrite(LED,state.help||state.fanFault||sensorFault);
 digitalWrite(BUZZER,state.help&&(now%1000<120));
 if(uint32_t(now-lastSample)<1000)return;
 uint32_t elapsed=now-lastSample;lastSample=now;noInterrupts();uint32_t pulses=tachPulses;tachPulses=0;interrupts();rpm=pulses*30000.0f/elapsed; // 2 pulses/revolution; verify chosen fan.
 // Retry failed I2C discovery to recover after reconnection.
 if(!inOK)inOK=inside.begin(0x44);if(!outOK)outOK=outside.begin(0x45); // seat 0x44 (ADDR low), reference 0x45 (ADDR high)
 ot=outOK?outside.readTemperature():NAN;orr=outOK?outside.readHumidity():NAN;
 temp=inOK?inside.readTemperature():NAN;rh=inOK?inside.readHumidity():NAN;
 if(!isfinite(ot)||!isfinite(orr))outOK=false;if(!isfinite(temp)||!isfinite(rh))inOK=false;
 sensorFault=!outOK||!inOK||rh<0||rh>100||orr<0||orr>100;
 if(haveRoofConversion){roofTemp=roof.getTempCByIndex(0);if(roofTemp==DEVICE_DISCONNECTED_C||roofTemp< -40||roofTemp>125)roofTemp=NAN;}
 haveRoofConversion=true;roof.requestTemperatures();
 bool waterAvailable=digitalRead(WATER)==LOW;
 Wire.beginTransmission(0x40);bool powerPresent=Wire.endTransmission()==0;
 if(!powerPresent)powerOK=false;else if(!powerOK)powerOK=powerMeter.begin();
 float watts=NAN;if(powerOK){float w=powerMeter.getPower_mW()/1000.0f;if(isfinite(w)&&w>=0)watts=w;} // circuit is FAN BRANCH only
 JsonDocument d;d["schema_version"]=1;d["device_id"]="saaya-esp32";d["session_id"]=session;d["seq"]=seq++;d["source"]="MEASURED";d["config_id"]="bench-v2-fan-branch-power";d["calibration_id"]="UNVERIFIED";d["acquired_ms"]=uptimeMs;d["emitted_ms"]=uptimeMs;
 finiteValue(d,"temp",temp);finiteValue(d,"rh",rh);finiteValue(d,"outdoor_temp",ot);finiteValue(d,"outdoor_rh",orr);finiteValue(d,"roof_temp",roofTemp);finiteValue(d,"watts",watts);d["rpm"]=rpm;d["duty"]=state.duty;d["water"]=waterAvailable?"available":"low";d["help"]=state.help;d["quality"]=sensorFault?"invalid":"valid";d["fan_fault"]=state.fanFault;{FanAdvice a=fanAdvice(sensorFault?NAN:temp);d["fan_advice"]=a==FAN_OK?"ok":a==FAN_CAUTION?"caution":a==FAN_AVOID?"avoid":"unknown";}d["clock_aligned"]=false;d["reference_valid"]=false;d["ref_roof"]=nullptr;d["ref_air_speed"]=nullptr;d["air_speed"]=nullptr;serializeJson(d,Serial);Serial.println();
#if SAAYA_WIFI
 {UplinkFrame f;if(measureJson(d)<sizeof(f.json)){serializeJson(d,f.json,sizeof(f.json));xQueueOverwrite(uplinkQueue,&f);}} // latest frame only; never blocks
#endif

 if(displayOK){display.clearDisplay();display.setTextSize(1);display.setTextColor(SSD1306_WHITE);display.setCursor(0,0);display.println("SAAYA NODE / MEASURED"); /* 21 chars = one 128 px line */display.printf("T: %.1f RH: %.0f\n",temp,rh);display.printf("Fan %d%% %.0f RPM\n",state.duty,rpm);display.println(waterAvailable?"Water available":"WATER LOW / CHECK");FanAdvice advice=fanAdvice(sensorFault?NAN:temp);display.println(state.help?"HELP REQUEST LATCHED":sensorFault?"SENSOR FAULT":state.fanFault?"FAN FEEDBACK FAULT":advice==FAN_AVOID?"HOT: FAN MAY ADD HEAT":advice==FAN_CAUTION?"FAN: LIMITED BENEFIT":"Not a safety rating");display.display();}
}
