#include "simpleserial.h"

nBlock_SimpleSerial::nBlock_SimpleSerial(PinName pinTX, PinName pinRX): _ser(pinTX, pinRX) {
    return;
}
uint32_t nBlock_SimpleSerial::outputAvailable(uint32_t outputNumber) { // outputNumber is ignored
    return _ser.readable();
}
uint32_t nBlock_SimpleSerial::readOutput(uint32_t outputNumber) { // outputNumber is ignored
    return _ser.getc();
}
void nBlock_SimpleSerial::triggerInput(uint32_t inputNumber, uint32_t value) { // inputNumber is ignored
    _ser.putc(value);
}
void nBlock_SimpleSerial::step(void) {
    return;
}

