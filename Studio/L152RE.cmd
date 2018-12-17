cd ..\..\mbed_code
mbed compile -t GCC_ARM -m NUCLEO_L152RE
cd BUILD\NUCLEO_L152RE\GCC_ARM
copy mbed_code.bin ..\..\..\mbed_code_L152RE.bin
cd ..\..\..


