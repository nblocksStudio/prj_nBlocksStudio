#include "pwm.h"

/// GPO
nBlock_PWM::nBlock_PWM(PinName pinPwm): _pwm(pinPwm) {
    duty_int = 0;
    _pwm.period(0.001);
    _pwm.write(0);
    return;
}
void nBlock_PWM::triggerInput(uint32_t inputNumber, uint32_t value) {
    // Stores the duty cycle we would like to use
    // when updating in the end of this frame
    duty_int = value;
}
void nBlock_PWM::step(void) {
    float tmp;
    tmp = (duty_int & 0x0000FFFF);
    tmp = tmp / 0x0000FFFF;
    _pwm.write(tmp);
    return;
}
