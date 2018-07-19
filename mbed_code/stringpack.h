#ifndef __NB_STRINGPACK
#define __NB_STRINGPACK

#include "mbed.h"
#include "nworkbench.h"

// temporary buffer used by sprintf
extern char _stringpack_strbuf[256];

class nBlock_StringPack: public nBlockSimpleNode<1> {
public:
    nBlock_StringPack(const char * formatString);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void endFrame(void);
private:
    fifo internal_fifo;
    const char * _format;
};

#endif
