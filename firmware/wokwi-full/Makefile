# Build the Wokwi custom chips (needs clang with the wasm32-wasi sysroot).
CFLAGS = --target=wasm32-unknown-wasi -nostartfiles -Wl,--import-memory -Wl,--export-table -Wl,--no-entry -Werror -O2 -I vendor
all: dist/sht30.chip.wasm dist/saaya-fan.chip.wasm
dist/%.chip.wasm: %.chip.c %.chip.json vendor/wokwi-api.h
	mkdir -p dist && clang $(CFLAGS) -o $@ $< && cp $*.chip.json dist/
clean:
	rm -rf dist
