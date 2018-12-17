cd ..\..\mbed_code_os5
mbed compile -t GCC_ARM -m NRF52_DK
cd BUILD\NRF52_DK\GCC_ARM
copy mbed_code.bin ..\..\..\mbed_code_nRF52.bin
cd ..\..\..


