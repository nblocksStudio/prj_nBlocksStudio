cd ..\..\mbed_code
mbed compile -t GCC_ARM -m LPC1768
cd BUILD\LPC1768\GCC_ARM
copy mbed_code.bin ..\..\..\mbed_code_LPC1768.bin
cd ..\..\..


