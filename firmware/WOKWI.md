# Wokwi simulation (online)

`diagram.json` + `wokwi.toml` wire the real firmware pins to Wokwi parts: OLED (I2C 0x3C), DS18B20 roof probe (IO4 + 4.7 kΩ), MODE/HELP/ACK buttons (IO32/33/27), status LED (IO26 + 330 Ω), buzzer (IO14), float switch (IO35 + 10 kΩ) and the tach pull-up (IO34).

Wokwi has no SHT3x or INA219 part and no PWM fan, so the simulation deliberately shows the **fault paths**: air sensors read *unavailable* → `SENSOR FAULT` on the OLED, automatic fan inhibited, power `null`; commanding the fan in MANUAL gives `FAN FEEDBACK FAULT` after 3 s because no tach pulses arrive. HELP latches, survives a simulated reset and clears only with ACK. (Custom-chip SHT31/INA219 models are possible with Wokwi's chips API but are not included.)

Run: `pio run -e esp32dev` in `firmware/`, then open the folder with the Wokwi VS Code extension. Status: prepared from Wokwi's documented part names; not executed during this review.
