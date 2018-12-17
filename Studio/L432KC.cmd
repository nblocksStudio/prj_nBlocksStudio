cd ..\..\mbed_code
mbed compile -t GCC_ARM -m NUCLEO_L432KC
cd BUILD\NUCLEO_L432KC\GCC_ARM
copy mbed_code.bin ..\..\..\mbed_code_NUCLEO_L432KC.bin
cd ..\..\..


