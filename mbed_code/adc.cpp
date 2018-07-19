#include "adc.h"

/// GPI
nBlock_ADC::nBlock_ADC(PinName pinAdc): _adc(pinAdc) {
    return;
}

void nBlock_ADC::triggerInput(uint32_t inputNumber, uint32_t value) {
    // Input 0 triggers a read regardless of value
    if (inputNumber == 0) {
        output[0] = _adc.read_u16();
        available[0] = 1;
    }
}

