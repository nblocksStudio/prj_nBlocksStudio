#include "not.h"

void nBlock_NOT::triggerInput(uint32_t inputNumber, uint32_t value) {
    output[0] = (value? 0 : 1);
    available[0] = 1;
}
