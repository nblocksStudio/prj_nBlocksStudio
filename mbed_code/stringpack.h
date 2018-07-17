#ifndef __NB_STRINGPACK
#define __NB_STRINGPACK

#include "mbed.h"
#include "nworkbench.h"

// temporary buffer used by sprintf
extern char _stringpack_strbuf[256];

class nBlock_StringPack: public nBlockNode {
public:
    nBlock_StringPack(const char * formatString);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    fifo internal_fifo;
    uint32_t _available;
    const char * _format;
};




#endif
