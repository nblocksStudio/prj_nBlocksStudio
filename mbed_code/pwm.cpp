#include "pwm.h"

/// GPO
nBlock_PWM::nBlock_PWM(void) {
    output_offset = 0;
    return;
}
void nBlock_PWM::triggerInput(uint32_t inputNumber, uint32_t value) {
    setPwm(output_offset*8 + inputNumber, value);
}
void nBlock_PWM::step(void) { return; }
