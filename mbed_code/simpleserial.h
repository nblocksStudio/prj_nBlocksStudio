#ifndef __NB_SIMPLESERIAL
#define __NB_SIMPLESERIAL

#include "mbed.h"
#include "nworkbench.h"

class nBlock_SimpleSerial: public nBlockNode {
public:
    nBlock_SimpleSerial(PinName pinTX, PinName pinRX);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    int _out;
    Serial _ser;
};




#endif
