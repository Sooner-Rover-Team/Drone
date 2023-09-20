from gpiozero import LED
from time import sleep

import cv2

left = LED(2)
right = LED(3)
forward = LED(4)
backward = LED(14)

while True:

    left.off()
    right.off()
    forward.off()
    backward.off()

    sleep(1) #delay in seconds

    left.on()
    right.on()
    forward.on()
    backward.on()

    sleep(1) #delay in seconds

    

    
