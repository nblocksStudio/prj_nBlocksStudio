#ifndef _NWORKBENCH
#define _NWORKBENCH

#include "mbed.h"
#include "fifo.h"

#define pin_A3    P2_0
#define pin_A4    P2_1
#define pin_A5    P0_10
#define pin_A6    P0_11
#define pin_A7    P0_17
#define pin_A8    P0_18
#define pin_A9    P0_15
#define pin_A10   P0_16

#define pin_B1    P0_3
#define pin_B2    P0_2
#define pin_B3    P1_0
#define pin_B4    P1_1
#define pin_B5    P1_4
#define pin_B6    P1_8
#define pin_B7    P1_9
#define pin_B8    P1_10
#define pin_B9    P1_14
#define pin_B10   P1_15
#define pin_B11   P1_16
#define pin_B12   P1_17

#define pin_C4    P3_26
#define pin_C5    P3_25
#define pin_C6    P0_28
#define pin_C7    P0_27
#define pin_C8    P2_11
#define pin_C9    P0_6
#define pin_C10   P2_6
#define pin_C11   P2_2
#define pin_C12   P2_3

#define pin_D1    P0_23
#define pin_D2    P0_24
#define pin_D3    P0_25
#define pin_D4    P0_26
#define pin_D5    P1_30
#define pin_D6    P1_31
#define pin_D9    P0_1
#define pin_D10   P0_0
#define pin_D11   P0_4
#define pin_D12   P0_5

#define pin_E1    P1_19
#define pin_E2    P1_22
#define pin_E3    P1_25
#define pin_E4    P1_26
#define pin_E5    P1_27
#define pin_E6    P2_13
#define pin_E7    P2_12
#define pin_E8    P0_21
#define pin_E9    P0_22
#define pin_E10   P2_8
#define pin_E11   P2_5
#define pin_E12   P2_4

#define pin_F3    P4_29
#define pin_F4    P4_28
#define pin_F5    P0_19
#define pin_F6    P0_20
#define pin_F7    P0_8
#define pin_F8    P0_9
#define pin_F9    P0_7
#define pin_F10   P1_29





void SetupWorkbench(void);


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


#endif
