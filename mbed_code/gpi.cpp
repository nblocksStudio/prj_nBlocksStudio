#include "gpi.h"

/// GPI
nBlock_GPI::nBlock_GPI(PinName pinIn): _in(pinIn) {
    output[0] = _in;
    available[0] = 1; // We start by firing the initial state
    return;
}

void nBlock_GPI::endFrame(void) {
    // Rising edge
    if ((old_in == 0) && (_in != 0)) {
        available[0] = 1;
        available[1] = 1;
        available[2] = 0;
        output[0] = _in;
        output[1] = _in;
    }
    // Falling edge
    else if ((old_in == 1) && (_in == 0)) {
        available[0] = 1;
        available[1] = 0;
        available[2] = 1;
        output[0] = _in;
        output[2] = _in;
    }
    // No edge, no new data
    else {
        available[0] = 0;
        available[1] = 0;
        available[2] = 0;
    }
    old_in = _in;
    return;
}
