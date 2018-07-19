#include "nworkbench.h"

#ifdef TARGET_LPC1768
  //Serial pc(USBTX, USBRX);
  //Serial pc(p26, p25);

  // INPUTS
  //DigitalIn input0(p28);
  //DigitalIn input1(p27);

  // ADC
  AnalogIn adc0(p15);

  // OUTPUTS
  DigitalOut output0(p12);
  DigitalOut output1(p11);

  // PWM
  PwmOut pwm0(p21);
#endif

#ifdef TARGET_LPC11U35_501
  //Serial pc(P0_19, P0_18);

  // INPUTS
  DigitalIn input0(P0_5);
  DigitalIn input1(P0_4);

  // OUTPUTS
  DigitalOut output0(P0_8);
  DigitalOut output1(P0_7);

  // PWM P0_12
#endif

fifo adcs[4];

// INTERNALS
uint32_t adc0_old;

Ticker InputTicker;

Ticker PropagateTicker;

nBlockNode * __firstNode = 0;
nBlockNode * __last_node = 0;
nBlockConnection * __first_connection = 0;
nBlockConnection * __last_connection = 0;
uint32_t __propagating = 0;

// NBLOCK NODE BASIC CLASS
nBlockNode::nBlockNode(void) {
    // placeholder
    if (__firstNode == 0) __firstNode = this;
    if (__last_node != 0) __last_node->setNext(this);
    __last_node = this;
}
void nBlockNode::setNext(nBlockNode * next) { this->_next = next; }
uint32_t nBlockNode::getNext(void) { return (uint32_t)(this->_next); }
uint32_t nBlockNode::outputAvailable(uint32_t outputNumber) { return 0; }
uint32_t nBlockNode::readOutput(uint32_t outputNumber) { return 0; }
void nBlockNode::triggerInput(uint32_t inputNumber, uint32_t value) { return; }
void nBlockNode::step(void) { return; }




// NBLOCKCONNECTION
nBlockConnection::nBlockConnection(nBlockNode * srcBlock, uint32_t outputNumber, nBlockNode * dstBlock, uint32_t inputNumber) {
    this->_srcBlock = srcBlock;
    this->_outputNumber = outputNumber;
    this->_dstBlock = dstBlock;
    this->_inputNumber = inputNumber;
    this->_next = 0;

    if (__first_connection == 0) __first_connection = this;
    if (__last_connection != 0) __last_connection->setNext(this);
    __last_connection = this;
}
void nBlockConnection::propagate(void) {
    //pc.printf("[%d] -- propagating...\n", this);
    if (this->_srcBlock->outputAvailable(this->_outputNumber) > 0) {
        uint32_t tmp = this->_srcBlock->readOutput(this->_outputNumber);
        this->_dstBlock->triggerInput(this->_inputNumber, tmp);
    }
}
void nBlockConnection::setNext(nBlockConnection * next) {
    this->_next = next;
}
uint32_t nBlockConnection::getNext(void) {
    return (uint32_t)(this->_next);
}



// DUMMY
nBlock_Dummy::nBlock_Dummy(void) {
  return;
}
uint32_t nBlock_Dummy::outputAvailable(uint32_t outputNumber){return 0;}
uint32_t nBlock_Dummy::readOutput(uint32_t outputNumber){return 0;}
void nBlock_Dummy::triggerInput(uint32_t inputNumber, uint32_t value){return;}
void nBlock_Dummy::step(void) { return; }



///////////////////
void propagateTick(void) {
    nBlockConnection * econn;
    nBlockNode * enode;
    if ((__propagating == 0) && (__first_connection != 0)) {
        __propagating = 1;
        // propagate connections
        econn = __first_connection;
        while (econn != 0) {
            econn->propagate();
            econn = (nBlockConnection *)(econn->getNext());
        }
        // step blocks' state machines and fifos
        enode = __firstNode;
        while (enode != 0) {
            enode->step();
            enode = (nBlockNode *)(enode->getNext());
        }
        __propagating = 0;
    }
}
void inputTick(void) {
    // --- INPUT 0 ---
    //if ((input0_old == 0) && (input0 != 0)) { inputs[0].put(1);  input0_old = input0; } // rising edge
    //if ((input0_old != 0) && (input0 == 0)) { inputs[0].put(0);  input0_old = input0; } // falling edge
    // --- INPUT 1 ---
    //if ((input1_old == 0) && (input1 != 0)) { inputs[1].put(1);  input1_old = input1; } // rising edge
    //if ((input1_old != 0) && (input1 == 0)) { inputs[1].put(0);  input1_old = input1; } // falling edge

    // --- ADC 0 ---
    uint32_t tmp;
    tmp = adc0.read_u16();
    tmp = (tmp << 16) & 0xFFFF0000;
    if (adc0_old != tmp) { adcs[0].put(tmp);  adc0_old = tmp; } // rising edge

}

void setOutput(uint32_t outputNumber, uint32_t value) {
    if (outputNumber == 0) { if (value == 0) output0 = 0; else output0 = 1; }
    if (outputNumber == 1) { if (value == 0) output1 = 0; else output1 = 1; }
}
void setPwm(uint32_t outputNumber, uint32_t value) {
    float tmp;
    tmp = value;
    tmp = tmp / 0xFFFFFFFF;
    if (outputNumber == 0) pwm0.write(tmp);
}


void SetupWorkbench(void) {
    //if (input0 == 0) input0_old = 1; else input0_old = 0; // make sure we start firing the initial state
    //if (input1 == 0) input1_old = 1; else input1_old = 0;
    adc0_old = 1; // impossible value, since the mask for this is 0xFFFF0000, so we fire the first value

    pwm0.period(0.001);

    InputTicker.attach(&inputTick, 0.001);
    PropagateTicker.attach(&propagateTick, 0.001);
}


