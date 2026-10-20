#!/bin/sh
# Compile the firmware control rules to WebAssembly for site/simulator.html (needs clang + wasm-ld).
set -e
cd "$(dirname "$0")/.."
clang --target=wasm32 -O2 -ffreestanding -fno-exceptions -fno-rtti -nostdlib -std=c++11 \
  -I firmware/sim/shim -Wl,--no-entry -Wl,--strip-all -o site/sim/controller.wasm firmware/sim/controller_wasm.cpp
echo "site/sim/controller.wasm $(wc -c < site/sim/controller.wasm) bytes"
