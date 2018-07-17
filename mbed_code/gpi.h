#ifndef __NB_GPI
#define __NB_GPI

#include "mbed.h"
#include "nworkbench.h"

class nBlock_GPI: public nBlockNode {
public:
    nBlock_GPI(PinName pinIn);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void step(void);
private:
    DigitalIn _in;
    uint32_t _output;
    uint32_t _available;
    uint32_t _rise_available;
    uint32_t _fall_available;
};





#endif
