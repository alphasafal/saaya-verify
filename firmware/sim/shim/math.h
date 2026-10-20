/* Freestanding shim so firmware/include/controller.h compiles to wasm32 without a libc. */
#pragma once
#define isfinite(x) __builtin_isfinite(x)
#define NAN __builtin_nanf("")
