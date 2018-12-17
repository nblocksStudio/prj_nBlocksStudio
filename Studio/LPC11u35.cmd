cd ..\..\mbed_code
mbed compile -t GCC_ARM -m lpc11u35_401
cd BUILD\lpc11u35_401\GCC_ARM
copy mbed_code.bin ..\..\..\mbed_code_lpc11u35_401.bin
cd ..\..\..


