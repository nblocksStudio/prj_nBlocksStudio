#ifndef __NB_PWM
#define __NB_PWM

#include "mbed.h"
#include "nworkbench.h"

class nBlock_PWM: public nBlockNode {
public:
    nBlock_PWM(PinName pinPwm);
    void triggerInput(uint32_t inputNumber, uint32_t value);
    void step(void);
private:
    PwmOut _pwm;
    uint32_t duty_int;
};



#endif
