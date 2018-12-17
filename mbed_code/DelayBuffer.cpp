#include "DelayBuffer.h"

nBlock_DelayBuffer::nBlock_DelayBuffer() {
    return;
}

void nBlock_DelayBuffer::triggerInput(uint32_t inputNumber, uint32_t value) {
    if (inputNumber == 0) {
        output[0] = value; // transfers the input value to the output
        available[0] = 1;  // set the flag: we have data available in this output pipe
    }
}