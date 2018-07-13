#include "or.h"


// OR GATE
nBlock_OR::nBlock_OR(void) {
    return;
}
uint32_t nBlock_OR::outputAvailable(uint32_t outputNumber) { // outputNumber is ignored
    return internal_fifo.available();
}
uint32_t nBlock_OR::readOutput(uint32_t outputNumber) { // outputNumber is ignored
    uint32_t tmp;
    internal_fifo.read(&tmp);
    return tmp;
}

void nBlock_OR::triggerInput(uint32_t inputNumber, uint32_t value) { 

	uint32_t result;

	if(value !=0 ){value = 1;}// anything non zero is 1
	
	switch (inputNumber){
		
		case 0:
			
			input_0 = value;
			break;
			
		case 1:
			
			input_1 = value;
			break;
			
		default:
			break;	
		
	}
	
	result = input_0 | input_1;
	
	internal_fifo.put(result);
	  
}

void nBlock_OR::step(void) {
    uint32_t tmp;
    internal_fifo.get(&tmp);
    return;
}
