#include "gpo.h"

/// GPO
nBlock_GPO::nBlock_GPO(void) {
    output_offset = 0;
    return;
}
void nBlock_GPO::triggerInput(uint32_t inputNumber, uint32_t value) {
    setOutput(output_offset*4 + inputNumber, value);
}
void nBlock_GPO::step(void) { return; }
