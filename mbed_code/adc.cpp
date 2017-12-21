#include "adc.h"

/// GPI
nBlock_ADC::nBlock_ADC(void) {
    input_offset = 0;
    return;
}

uint32_t nBlock_ADC::outputAvailable(uint32_t outputNumber) {
    return adcs[input_offset*4 + outputNumber].available();
}

uint32_t nBlock_ADC::readOutput(uint32_t outputNumber) {
    uint32_t tmp;
    adcs[input_offset*4 + outputNumber].read(&tmp);
    return tmp;
}
void nBlock_ADC::step(void) {
    uint32_t tmp;
    for (int i = 0; i < 4; i++) {
        adcs[input_offset*4 + i].get(&tmp);
    }
    return;
}
