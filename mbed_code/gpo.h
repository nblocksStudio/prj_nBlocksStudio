#ifndef __NB_GPO
#define __NB_GPO

#include "mbed.h"
#include "nworkbench.h"



class nBlock_GPO: public nBlockNode {
public:
    nBlock_GPO(void);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    uint32_t output_offset;
};




#endif
