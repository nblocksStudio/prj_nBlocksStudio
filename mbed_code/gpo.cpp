#include "gpo.h"

/// GPO
nBlock_GPO::nBlock_GPO(PinName pinOut): _out(pinOut) {
    return;
}
void nBlock_GPO::triggerInput(uint32_t inputNumber, uint32_t value) {
    _out = (value)? 1 : 0;
}

