#include "gpi.h"

/// GPI
nBlock_GPI::nBlock_GPI(void) {
    input_offset = 0;
    return;
}

uint32_t nBlock_GPI::outputAvailable(uint32_t outputNumber) {
    return inputs[input_offset*8 + outputNumber].available();
}

uint32_t nBlock_GPI::readOutput(uint32_t outputNumber) {
    uint32_t tmp;
    inputs[input_offset*8 + outputNumber].read(&tmp);
    return tmp;
}
void nBlock_GPI::step(void) {
    uint32_t tmp;
    for (int i = 0; i < 8; i++) {
        inputs[input_offset*8 + i].get(&tmp);
    }
    return;
}
