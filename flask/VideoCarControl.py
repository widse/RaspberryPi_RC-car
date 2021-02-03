# Remote Car Control with Video Streaming by Flask web service    

#Import GPIO, time library
from flask import Flask, render_template, request, Response
import RPi.GPIO as GPIO                 
import time      
import io
import threading
import picamera

class Camera:
    thread = None  # background thread that reads frames from camera
    frame = None  # current frame is stored here by background thread
    start_time = 0  # time of last client access to the camera

    def getStreaming(self):
        Camera.start_time = time.time()
        #self.initialize()
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self.streaming)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frame is None:
                time.sleep(0)
        return self.frame

    @classmethod
    def streaming(c):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (320, 240)
            camera.hflip = True
            camera.vflip = True

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            stream = io.BytesIO()
            for f in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                c.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - c.start_time > 10:
                    break
        c.thread = None
        
app = Flask(__name__)

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

DIGIT_L = 23 #sensor pin number
DIGIT_R = 24

R_FW = 26  #mortor pin number
R_BW = 19
R_PWM = 13
L_FW = 21
L_BW = 20
L_PWM = 16

GPIO.setup(DIGIT_L,GPIO.IN)
GPIO.setup(DIGIT_R,GPIO.IN)

GPIO.setup(R_FW, GPIO.OUT)
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

def RMotor(forward, backward, pwm):
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
#     time.sleep(2)
# def Rmove(power):     
#     RMotor(1,0,power)
#     LMotor(0,0,power)
#     time.sleep(1)
# def Lmove(power):     
#     RMotor(0,0,power)
#     LMotor(1,0,power)
#     time.sleep(1)
# def Smove():     
#     RMotor(0,0,0)
#     LMotor(0,0,0)
    
@app.route("/")
def hello():
    return "Hello Pyrhon IoT Projects!"

@app.route("/<command>")
def action(command):
    power = 70
    if command == "F":
        RMotor(1,0,power)
        LMotor(1,0,power)
        time.sleep(1)
        message = "Moving Foward"
    elif command == "L":
        RMotor(0,0,power)
        LMotor(1,0,power)
        time.sleep(1)
        message = "Turn Left"
    elif command == "R":
        RMotor(1,0,power)
        LMotor(0,0,power)
        time.sleep(1)   
        message = "Turn Right"  
    else:
        RMotor(0,0,0)
        LMotor(0,0,0)
        message = "Unknown Command [" + command + "] " 

    return render_template('video.html', message = message)


def show(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.getStreaming()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/show')
def showVideo():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(show(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    try:
        app.run(host='0.0.0.0', port=8300, debug=True, threaded=True)
    except KeyboardInterrupt:
        print ("Terminate program by Keyboard Interrupt")
        GPIO.cleanup()
