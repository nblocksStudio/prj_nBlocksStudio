#ifndef _NWORKBENCH
#define _NWORKBENCH

#include "mbed.h"
#include "fifo.h"

extern Serial pc;
extern fifo inputs[8];
extern fifo adcs[4];

void SetupWorkbench(void);
void setOutput(uint32_t outputNumber, uint32_t value);
void setPwm(uint32_t outputNumber, uint32_t value);


// This is base class for all nodes in n-Workbench
class nBlockNode {
public:
    nBlockNode(void);
    void setNext(nBlockNode * next);
    uint32_t getNext(void);
    virtual uint32_t outputAvailable(uint32_t outputNumber);
    virtual uint32_t readOutput(uint32_t outputNumber);
    virtual void triggerInput(uint32_t inputNumber, uint32_t value);
    virtual void step(void);
private:
    nBlockNode * _next;
};

// Base class for simplified work nodes
// implementation must be here because of the template
template <size_t simpleNode_OutputSize>
class nBlockSimpleNode: public nBlockNode {
public:
    nBlockSimpleNode(void) {
        unsigned int i;
        for (i=0; i<simpleNode_OutputSize; i++) {
            _exposed_output[i] = 0;
            _exposed_available[i] = 0;
            output[i] = 0;
            available[i] = 0;
        }
    }
    uint32_t outputAvailable(uint32_t outputNumber) { return _exposed_available[outputNumber]; }
    uint32_t readOutput(uint32_t outputNumber) { return _exposed_output[outputNumber]; }
    virtual void endFrame(void) { return; }
    void step(void) {
        unsigned int i;
        endFrame();
        for (i=0; i<simpleNode_OutputSize; i++) {
            _exposed_output[i] = output[i];
            _exposed_available[i] = available[i];
            available[i] = 0;
        }
        return;
    }

    uint32_t output[simpleNode_OutputSize];
    uint32_t available[simpleNode_OutputSize];
private:
    //const uint32_t _numOutputs = simpleNode_OutputSize;
    uint32_t _exposed_output[simpleNode_OutputSize];
    uint32_t _exposed_available[simpleNode_OutputSize];
};


class nBlockConnection {
public:
    nBlockConnection(nBlockNode * srcBlock, uint32_t outputNumber, nBlockNode * dstBlock, uint32_t inputNumber);
    void propagate(void);
    void setNext(nBlockConnection * next);
    uint32_t getNext(void);
private:
    nBlockNode * _srcBlock;
    uint32_t _outputNumber;
    nBlockNode * _dstBlock;
    uint32_t _inputNumber;
    nBlockConnection * _next;
};



class nBlock_Dummy: public nBlockNode {
public:
    nBlock_Dummy(void);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
};


uint32_t check_fifo(void);
uint32_t get_fifo(void);




#endif
