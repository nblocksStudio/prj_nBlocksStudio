#include "nworkbench.h"

#ifdef TARGET_LPC1768

#endif

#ifdef TARGET_LPC11U35_501

#endif



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

void SetupWorkbench(void) {

    PropagateTicker.attach(&propagateTick, 0.001);
}


