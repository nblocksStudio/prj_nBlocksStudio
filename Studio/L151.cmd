cd ..\..\mbed_code
mbed compile -t GCC_ARM -m xdot_l151cc
cd BUILD\xdot_l151cc\GCC_ARM
copy mbed_code.bin ..\..\..\mbed_code_L151.bin
cd ..\..\..


