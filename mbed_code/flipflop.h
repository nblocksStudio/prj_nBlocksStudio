#ifndef __NB_FLIPFLOP
#define __NB_FLIPFLOP

#include "mbed.h"
#include "nworkbench.h"

/*
=============================================================================
THIS NODE IS A REFERENCE EXAMPLE OF HOW TO IMPLEMENT USING THE RAW NODE CLASS

                     Derive your node from nBlockNode
=============================================================================
*/

class nBlock_FlipFlop: public nBlockNode {
public:
    // This flip flop has configurable edge. Not specifying it means positive edge
    // positive edge means it will be triggered by values > 0
    // Both means triggered by any value update
    enum {triggerMode_Positive, triggerMode_Zero, triggerMode_Both};

    nBlock_FlipFlop(uint32_t triggerMode = triggerMode_Positive);
    uint32_t outputAvailable(uint32_t outputNumber);
    uint32_t readOutput(uint32_t outputNumber);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    // Below are variables used internally by this node
    uint32_t _triggerMode;

    // ================================================================
    // Below are variables to store output data
    // The size of these arrays is the number of outputs
    // So if you have 1 output, you should have uint32_t _exposed_output[1]
    // If you have 6 outputs, you have uint32_t _exposed_output[6]

    // In one frame the node must constantly provide data produced in the
    // previous frame, not the current one. The outputs should never change
    // during a frame as consequence of inputs in the same frame, as this
    // leads to harmful inconsistencies.
    // Therefore you always need the following two variables.
    // You can't change them during the frame, only in the step method
    // (unless you know what you are doing)
    uint32_t _exposed_output[1];
    uint32_t _exposed_available[1];

    // If you don't have any FIFO or buffers of any kind, then you also
    // need an extra pair to hold values being changed during the frame,
    // like working registers, since you can't touch the exposed variables.
    // Transfer the values from these to the exposed ones in the step method
    uint32_t _output[1];
    uint32_t _available[1];
};


#endif
