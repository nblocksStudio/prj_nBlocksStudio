#ifndef __NB_OR
#define __NB_OR

//#include "mbed.h"
#include "nworkbench.h"



class nBlock_OR: public nBlockNode {
public:
    nBlock_OR(void);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    fifo internal_fifo;
    uint32_t input_0;
    uint32_t input_1;
};





#endif
