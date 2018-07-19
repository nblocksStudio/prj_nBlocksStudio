#ifndef __NB_ADC
#define __NB_ADC

#include "mbed.h"
#include "nworkbench.h"

class nBlock_ADC: public nBlockSimpleNode<1> {
public:
    nBlock_ADC(PinName pinAdc);
    void triggerInput(uint32_t inputNumber, uint32_t value);
private:
    AnalogIn _adc;
};





#endif
