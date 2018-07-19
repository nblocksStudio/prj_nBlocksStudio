#include "ticker.h"

// TICKER
nBlock_Ticker::nBlock_Ticker(uint32_t period_ms) {
    (this->_ticker).attach(callback(this, &nBlock_Ticker::_tick), 0.001*period_ms);
}
void nBlock_Ticker::_tick(void) {
    output[0] = 1;
    available[0] = 1;
}
