#include "ticker.h"

// TICKER
nBlock_Ticker::nBlock_Ticker(void) {
    this->_output = 0;
    (this->_ticker).attach(callback(this, &nBlock_Ticker::_tick), 1.0);
}
uint32_t nBlock_Ticker::outputAvailable(uint32_t outputNumber) { // outputNumber is ignored
    return _output;
}
uint32_t nBlock_Ticker::readOutput(uint32_t outputNumber) { // outputNumber is ignored
    return _output;
}
void nBlock_Ticker::triggerInput(uint32_t inputNumber, uint32_t value) { // inputNumber is ignored
    return;
}
void nBlock_Ticker::step(void) {
    if (_output) _output = 0;
    return;
}
void nBlock_Ticker::_tick(void) {
    if (_output == 0) _output = 1;
}
