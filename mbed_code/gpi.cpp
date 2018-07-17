#include "gpi.h"

/// GPI
nBlock_GPI::nBlock_GPI(PinName pinIn): _in(pinIn) {
    _output = _in;
    _available = 1; // We start by firing the initial state
    _rise_available = 0;
    _fall_available = 0;
    return;
}

uint32_t nBlock_GPI::outputAvailable(uint32_t outputNumber) {
    switch (outputNumber) {
        case 0: // OUTPUT: CHANGE
            return _available;
        case 1: // OUTPUT: RISE
            return _rise_available;
        case 2: // OUTPUT: RISE
            return _fall_available;
        default:
            return 0;
    }
}

uint32_t nBlock_GPI::readOutput(uint32_t outputNumber) {
    // same data for all outputs
    return _output;
}

void nBlock_GPI::step(void) {
    // Rising edge
    if ((_output == 0) && (_in != 0)) {
        _available = 1;
        _rise_available = 1;
        _fall_available = 0;
        _output = _in;
    }
    // Falling edge
    else if ((_output == 1) && (_in == 0)) {
        _available = 1;
        _rise_available = 0;
        _fall_available = 1;
        _output = _in;
    }
    // No edge, no new data
    else {
        _available = 0;
        _rise_available = 0;
        _fall_available = 0;
    }
    return;
}
