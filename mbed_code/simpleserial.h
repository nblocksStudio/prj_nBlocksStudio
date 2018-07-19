#ifndef __NB_SIMPLESERIAL
#define __NB_SIMPLESERIAL

#include "mbed.h"
#include "nworkbench.h"

class nBlock_SimpleSerial: public nBlockSimpleNode<1> {
public:
    nBlock_SimpleSerial(PinName pinTX, PinName pinRX);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void endFrame(void);
private:
    Serial _ser;
};

#endif
