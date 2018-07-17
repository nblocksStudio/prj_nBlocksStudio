#include "stringpack.h"

char _stringpack_strbuf[256] = "";

nBlock_StringPack::nBlock_StringPack(const char * formatString) {
    _format = formatString; // Let's keep a pointer to this constant string
    _available = 0;
}
uint32_t nBlock_StringPack::outputAvailable(uint32_t outputNumber) { // outputNumber is ignored
    return _available;
}
uint32_t nBlock_StringPack::readOutput(uint32_t outputNumber) { // outputNumber is ignored
    uint32_t tmp;
    internal_fifo.read(&tmp);
    return tmp;
}
void nBlock_StringPack::triggerInput(uint32_t inputNumber, uint32_t value) { // inputNumber is ignored
    int i, f;

    // Insert the value into the format string, and save it into the stringpack buffer
    sprintf(_stringpack_strbuf, _format, value);

    // Fill free slots in fifo with data from this string (discard the remaining)
    f = internal_fifo.free();
    for (i=0; i<f; i++) {
        if (_stringpack_strbuf[i] == 0)
            break;
        else
            internal_fifo.put( _stringpack_strbuf[i] );
    }
}
void nBlock_StringPack::step(void) {
    uint32_t tmp;
    if (_available) internal_fifo.get(&tmp);
    _available = internal_fifo.available();
    return;
}

