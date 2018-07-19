#ifndef __NB_TICKER
#define __NB_TICKER

#include "mbed.h"
#include "nworkbench.h"

class nBlock_Ticker: public nBlockSimpleNode<1> {
public:
    nBlock_Ticker(uint32_t period_ms);
private:
    Ticker _ticker;
    void _tick(void);
};

#endif
