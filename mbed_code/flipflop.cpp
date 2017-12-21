#include "flipflop.h"

// FLIP FLOP
nBlock_FlipFlop::nBlock_FlipFlop(void) {
    last_state = 0;
    return;
}
uint32_t nBlock_FlipFlop::outputAvailable(uint32_t outputNumber) { // outputNumber is ignored
    return internal_fifo.available();
}
uint32_t nBlock_FlipFlop::readOutput(uint32_t outputNumber) { // outputNumber is ignored
    uint32_t tmp;
    internal_fifo.read(&tmp);
    return tmp;
}
void nBlock_FlipFlop::triggerInput(uint32_t inputNumber, uint32_t value) { // inputNumber is ignored
    if (value != 0) {
        if (last_state == 0) last_state = 1;
        else last_state = 0;
        internal_fifo.put(last_state);
    }
    // else nothing, rising edge flip flop
}
void nBlock_FlipFlop::step(void) {
    uint32_t tmp;
    internal_fifo.get(&tmp);
    return;
}
