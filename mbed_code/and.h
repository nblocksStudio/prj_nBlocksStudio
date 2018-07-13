#ifndef __NB_AND
#define __NB_AND

//#include "mbed.h"
#include "nworkbench.h"



class nBlock_AND: public nBlockNode {
public:
    nBlock_AND(void);
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
