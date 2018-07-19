#include "simpleserial.h"

nBlock_SimpleSerial::nBlock_SimpleSerial(PinName pinTX, PinName pinRX): _ser(pinTX, pinRX) {
    return;
}
void nBlock_SimpleSerial::triggerInput(uint32_t inputNumber, uint32_t value) { // inputNumber is ignored
    _ser.putc(value);
}
void nBlock_SimpleSerial::endFrame(void) {
    if (_ser.readable()) {
        output[0] = _ser.getc();
        available[0] = 1;
    }
    return;
}

