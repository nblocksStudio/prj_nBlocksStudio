#include "not.h"


// NOT GATE
nBlock_NOT::nBlock_NOT(void) {
    return;
}
uint32_t nBlock_NOT::outputAvailable(uint32_t outputNumber) { // outputNumber is ignored
    return internal_fifo.available();
}
uint32_t nBlock_NOT::readOutput(uint32_t outputNumber) { // outputNumber is ignored
    uint32_t tmp;
    internal_fifo.read(&tmp);
    return tmp;
}
void nBlock_NOT::triggerInput(uint32_t inputNumber, uint32_t value) { // inputNumber is ignored
    if (value == 0) internal_fifo.put(1);
    else internal_fifo.put(0);
}
void nBlock_NOT::step(void) {
    uint32_t tmp;
    internal_fifo.get(&tmp);
    return;
}

