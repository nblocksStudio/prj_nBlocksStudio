#ifndef __DELAYBUFFER
#define __DELAYBUFFER

#include "mbed.h"
#include "nworkbench.h"

class nBlock_DelayBuffer: public nBlockSimpleNode<1> {
public:
    nBlock_DelayBuffer();
    void triggerInput(uint32_t inputNumber, uint32_t value);
};

#endif


