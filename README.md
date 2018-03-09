Workbench for n-Blocks

How to set up:

1- Install python and panda3d

2- Put python in the system path

3- Install mbed CLI

4- Download the studio from this repository (folder Studio)

5- Download the mbed source code from this repository (folder mbed_code)

6- Go to command line, navigate to the mbed_code folder and type:

C:\....\mbed_code>   mbed new . --mbedlib

C:\....\mbed_code>   mbed deploy


7- Use the studio. When exporting, save into the file main.cpp inside mbed_code, and build with:

C:\....\mbed_code>  mbed compile -t GCC_ARM -m LPC1768

