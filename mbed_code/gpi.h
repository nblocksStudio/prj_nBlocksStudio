#ifndef __NB_GPI
#define __NB_GPI

#include "mbed.h"
#include "nworkbench.h"

class nBlock_GPI: public nBlockNode {
public:
    nBlock_GPI(void);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void step(void);
private:
    uint32_t input_offset;
};





#endif
