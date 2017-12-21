#ifndef __NB_NOT
#define __NB_NOT

#include "mbed.h"
#include "nworkbench.h"


class nBlock_NOT: public nBlockNode {
public:
    nBlock_NOT(void);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    fifo internal_fifo;
};




#endif
