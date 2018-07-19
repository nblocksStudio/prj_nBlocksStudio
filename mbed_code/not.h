#ifndef __NB_NOT
#define __NB_NOT

#include "mbed.h"
#include "nworkbench.h"

class nBlock_NOT: public nBlockSimpleNode<1> {
public:
    void triggerInput(uint32_t inputNumber, uint32_t value);
};

#endif
