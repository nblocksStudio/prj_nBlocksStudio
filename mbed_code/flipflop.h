#ifndef __NB_FLIPFLOP
#define __NB_FLIPFLOP

#include "mbed.h"
#include "nworkbench.h"

class nBlock_FlipFlop: public nBlockNode {
public:
    nBlock_FlipFlop(void);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    fifo internal_fifo;
    uint32_t last_state;
};


#endif
