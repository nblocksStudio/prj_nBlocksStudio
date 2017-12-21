#ifndef __NB_TICKER
#define __NB_TICKER

#include "mbed.h"
#include "nworkbench.h"


class nBlock_Ticker: public nBlockNode {
public:
    nBlock_Ticker(void);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    Ticker _ticker;
    uint32_t _output;
    void _tick(void);
};



#endif
