#ifndef __NB_GPI
#define __NB_GPI

#include "mbed.h"
#include "nworkbench.h"

class nBlock_GPI: public nBlockSimpleNode<3> {
public:
    nBlock_GPI(PinName pinIn);
    void endFrame(void);
private:
    DigitalIn _in;
    uint32_t old_in;
};


#endif
