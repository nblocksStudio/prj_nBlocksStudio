#ifndef __NB_ADC
#define __NB_ADC

#include "mbed.h"
#include "nworkbench.h"

class nBlock_ADC: public nBlockNode {
public:
    nBlock_ADC(void);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void step(void);
private:
    uint32_t input_offset;
};





#endif
