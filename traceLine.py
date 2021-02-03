import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

DIGIT_L = 23    # set pin number about sensor
DIGIT_R = 24

R_FW = 26       # set pin number about mortor
R_BW = 19
R_PWM = 13
L_FW = 21
L_BW = 20
L_PWM = 16

GPIO.setup(DIGIT_L,GPIO.IN)         # set raspberry pi pin as input mode
GPIO.setup(DIGIT_R,GPIO.IN)

GPIO.setup(R_FW, GPIO.OUT)          # set raspberry pi pin as output mode
GPIO.setup(R_BW, GPIO.OUT)
GPIO.setup(R_PWM, GPIO.OUT)
GPIO.output(R_PWM, 0)
R_MOTOR = GPIO.PWM(R_PWM, 100)
R_MOTOR.start(0)
R_MOTOR.ChangeDutyCycle(0)

GPIO.setup(L_FW, GPIO.OUT)
GPIO.setup(L_BW, GPIO.OUT)
GPIO.setup(L_PWM, GPIO.OUT)
GPIO.output(L_PWM, 0)
L_MOTOR = GPIO.PWM(L_PWM, 100)
L_MOTOR.start(0)
L_MOTOR.ChangeDutyCycle(0)

def RMotor(forward, backward, pwm):         # define function to drive motor through RBpi pin 
    GPIO.output(R_FW, forward)
    GPIO.output(R_BW, backward)
    R_MOTOR.ChangeDutyCycle(pwm)
    
def LMotor(forward, backward, pwm):
    GPIO.output(L_FW, forward)
    GPIO.output(L_BW, backward)
    L_MOTOR.ChangeDutyCycle(pwm)

# When use below function rc car doesn't work normally. Why? 
# def Fmove(power):
#     RMotor(1,0,power)
#     LMotor(1,0,power)
# def Rmove(power):     
#     RMotor(1,0,power)
#     LMotor(0,0,0)
# def Lmove(power):     
#     RMotor(0,0,0)
#     LMotor(1,0,power)    
# def Smove(power = 0):     
#     RMotor(0,0,power)
#     LMotor(0,0,power)
    
if __name__ == '__main__':
    power = 70
    try:
        while 1:
            digit_val_L = GPIO.input(DIGIT_L)   # accept sensor input to variables  
            digit_val_R = GPIO.input(DIGIT_R)
            
            # set condition to trace line depending on sensor input
            if (digit_val_L == 1 and digit_val_R == 1):
                RMotor(1,0,power)
                LMotor(1,0,power)
                
            elif (digit_val_L == 1 and digit_val_R == 0):
                RMotor(1,0,power)
                LMotor(0,0,power)
                
            elif (digit_val_L == 0 and digit_val_R == 1):
                RMotor(0,0,power)
                LMotor(1,0,power)
                
            elif (digit_val_L == 0 and digit_val_R == 0):
                RMotor(0,0,power)
                LMotor(0,0,power)
                
            time.sleep(0.005)
            
    except KeyboardInterrupt:       # reset RBpi before exit
        GPIO.cleanup()
    finally:
        print("clean up") 
        GPIO.cleanup()