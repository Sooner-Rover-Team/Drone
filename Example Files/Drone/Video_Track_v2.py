
# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera

from gpiozero import LED
from time import sleep

import time
import cv2
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()  #this creates a stream called camera 
camera.resolution = (720, 480)
camera.framerate = 30
rawCapture = PiRGBArray(camera, size=(720, 480))
 
# allow the camera to warmup
time.sleep(0.2)

#GPIO initiliazation
left = LED(2)
right = LED(3)
forward = LED(4)
backward = LED(14)

status = "No Targets"
first_detection = False #this shows the landing platform has not yet been detected, it becomes 1 on first detection

#the variables below show are for the postion of the landing platform
platformXcurrent = 0 
platformYcurrent = 0
platformXprevious = 0
platformYprevious = 0

#the two variables below show how much the platform has moved
movementX = 0
movementY = 0

# this loop keeps getting the frames from the camera stream 
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True): 
        # grab the raw NumPy array representing the image, then initialize the timestamp
	# and occupied/unoccupied text
	image = frame.array #captured image 
 
	# initialize key
	key = cv2.waitKey(1) & 0xFF 
 
	# convert the frame to grayscale, blur it, and detect edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #converts image from color to greyscale
        blurred = cv2.GaussianBlur(gray, (7, 7), 0) #use GaussianBlur to filter out noise
        edged = cv2.Canny(blurred, 50, 150) #Canny edge detection

        # find contours in the edge map
        cnts, _ = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours found and try to find the square platform
        for c in cnts:
            
                # approximate the contour
                peri = cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, 0.01 * peri, True) #tries to approximate the shape to become a square at 1%

                # ensure that the approximated contour is "roughly" rectangular
                if len(approx) >= 4 and len(approx) <= 6:
                        # compute the bounding box of the approximated contour and
                        # use the bounding box to compute the aspect ratio
                        (x, y, w, h) = cv2.boundingRect(approx)
                        aspectRatio = w / float(h)

                        # compute the solidity of the original contour
                        area = cv2.contourArea(c)
                        hull = cv2.convexHull(c) # ensures shape becomes a square
                        hullArea = cv2.contourArea(hull)
                        solidity = area / float(hullArea)

                        # compute whether or not the width and height, solidity, and
                        # aspect ratio of the contour falls within appropriate bounds
                        keepDims = w > 25 and h > 25
                        keepSolidity = solidity > 0.9
                        keepAspectRatio = aspectRatio >= 0.8 and aspectRatio <= 1.2

                        # ensure that the contour passes all our tests - everything below this indicates the square has been detected or landing platform has been detected
                        if keepDims and keepSolidity and keepAspectRatio:
                            
                                # draw an outline around the target and update the status text
                                cv2.drawContours(image, [approx], -1, (0, 0, 255), 4)
                                status = "Target(s) Acquired"
                            
                                # compute the center of the contour region and draw the crosshairs
                                M = cv2.moments(approx)
                                (platformX, platformY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])) #computes the center of the square contour

                                cv2.circle(image,(int(platformX),int(platformY)), 5, (0,0,255), -1) #draw a circle at the center of the frame captured

                                #THE CODES BELOW ARE AN UPDATE FROM drone_v1.py

                                #find which quadrant the target is input
                                #below checks for Q1 boundaries -fixed from v1
                                inQ1X = platformX > 0 and platformX <= 360
                                inQ1Y = platformY > 0 and platformY <= 240

                                #below checks for Q2 boundaries
                                inQ2X = platformX > 360 and platformX < 720
                                inQ2Y = platformY > 0 and platformY <= 240

                                #below checks for Q3 boundaries
                                inQ3X = platformX > 360 and platformX < 720
                                inQ3Y = platformY > 240 and platformY < 480

                                #below checks for Q4 boundaries
                                inQ4X = platformX > 0 and platformX <= 360
                                inQ4Y = platformY > 240 and platformY < 480

                                #below checks if the quadcopter is centered with the platform
                                inCX  = platformX >= 320 and platformX <= 400
                                inCY  = platformY >= 200 and platformY <= 280

                                #decision uopn first platform detection
                                if first_detection == False:

                                        #current position of the platform in the pictured
                                        platformXcurrent = platformX - 360
                                        platformYcurrent = -1*(platformY - 240)

                                        #previous platform postion initialize
                                        platformXprevious = platformXcurrent
                                        platformYprevious = platformYcurrent

                                        first_detection = True
                                        print('First Detection Confirmed')


                                else: #this shows that the platform had been detected once and now is being tracked

                                        #current position of the platform in the pictured
                                        platformXcurrent = platformX - 360
                                        platformYcurrent = -1*(platformY - 240)

                                        #find out how much the platform has moved
                                        movementX = platformXcurrent - platformXprevious
                                        movementY = platformYcurrent - platformYprevious
                                    
                                        #movement logics, how the quadcopter is moving with reference to landing platform
                                        moveRightForward     = platformXcurrent > platformXprevious and platformYcurrent > platformYprevious
                                        moveRightBackward    = platformXcurrent > platformXprevious and platformYcurrent < platformYprevious
                                        moveLeftForward      = platformXcurrent < platformXprevious and platformYcurrent > platformYprevious
                                        moveLeftBackward     = platformXcurrent < platformXprevious and platformYcurrent < platformYprevious

                                        #turn off all the led's
                                        left.off()
                                        right.off()
                                        forward.off()
                                        backward.off()
                                
                                        #check which quadrant the landing platform is located in the image 

                                        if inCX and inCY: #checks if the platform and quadcopter is properly aligned

                                                #insert here the code to detect the distance to the platform
                                                print('Center')
                                                print('Current X,Y: ', platformXcurrent, platformYcurrent)
                                                print('PreviousX,Y: ', platformXprevious, platformYprevious )

                                                if moveRightForward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and forward')
                                                        left.on()

                                                elif moveRightBackward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and backwards')
                                                        right.on()
                                                        
                                                elif moveLeftForward:

                                                        #the drone has moved left and forward
                                                        print('Drone moved left and forward')
                                                        forward.on()

                                                elif moveLeftBackward:

                                                        #the drone has moved left and backward
                                                        print('Drone moved left and backward')
                                                        backward.on()

                                                else:
                                                        
                                                        #the drone has not moved yet 
                                                        print('Drone not moved')
                                                        
                                                        #turn on all the led's
                                                        left.on()
                                                        right.on()
                                                        forward.on()
                                                        backward.on()

                                        elif inQ1X and inQ1Y: #check if the platform is in Q1

                                                #prints the position of the landing platform
                                                print('Quadrant 1')
                                                print('Current X,Y: ', platformXcurrent, platformYcurrent)
                                                print('PreviousX,Y: ', platformXprevious, platformYprevious )

                                                if moveRightForward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and forward')
                                                        left.on()

                                                elif moveRightBackward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and backwards')
                                                        right.on()
                                                        
                                                elif moveLeftForward:

                                                        #the drone has moved left and forward
                                                        print('Drone moved left and forward')
                                                        forward.on()
                                                        

                                                elif moveLeftBackward:

                                                        #the drone has moved left and backward
                                                        print('Drone moved left and backward')
                                                        backward.on()

                                                else:
                                                                
                                                        #the drone has not moved 
                                                        print('Drone not moved')
                                                        
                                                        #turn on all the led's
                                                        left.on()
                                                        right.on()
                                                        forward.on()
                                                        backward.on()

                                        elif inQ2X and inQ2Y: #check if the platform is in Q2

                                                #prints the position of the landing platform
                                                print('Quadrant 2')
                                                print('Current X,Y: ', platformXcurrent, platformYcurrent)
                                                print('PreviousX,Y: ', platformXprevious, platformYprevious )

                                                if moveRightForward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and forward')
                                                        left.on()
                                                        
                                                elif moveRightBackward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and backwards')
                                                        right.on()

                                                elif moveLeftForward:

                                                        #the drone has moved left and forward
                                                        print('Drone moved left and forward')
                                                        forward.on()

                                                elif moveLeftBackward:

                                                        #the drone has moved left and backward
                                                        print('Drone moved left and backward')
                                                        backward.on()

                                                else:
                                                                
                                                        #drone has not moved
                                                        print('Drone not moved')
                                                        
                                                        #turn on all the led's
                                                        left.on()
                                                        right.on()
                                                        forward.on()
                                                        backward.on()

                                        elif inQ3X and inQ3Y: #check if the platform is in Q3

                                                #prints the position of the landing platform
                                                print('Quadrant 3')
                                                print('Current X,Y: ', platformXcurrent, platformYcurrent)
                                                print('PreviousX,Y: ', platformXprevious, platformYprevious )

                                                if moveRightForward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and forward')
                                                        left.on()

                                                elif moveRightBackward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and backwards')
                                                        right.on()

                                                elif moveLeftForward:

                                                        #the drone has moved left and forward
                                                        print('Drone moved left and forward')
                                                        forward.on()

                                                elif moveLeftBackward:

                                                        #the drone has moved left and backward
                                                        print('Drone moved left and backward')
                                                        backward.on()

                                                else:
                                                        
                                                        #the drone has not moved 
                                                        print('Drone not moved')
                
                                                        #turn on all the led's
                                                        left.on()
                                                        right.on()
                                                        forward.on()
                                                        backward.on()

                                        else:

                                                #prints the position of the landing platform
                                                print('Quadrant 4')
                                                print('Current X,Y: ', platformXcurrent, platformYcurrent)
                                                print('PreviousX,Y: ', platformXprevious, platformYprevious )

                                                if moveRightForward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and forward')
                                                        left.on()

                                                elif moveRightBackward:

                                                        #the drone has moved right and forward with respect to platform
                                                        print('Drone moved right and backwards')
                                                        right.on()

                                                elif moveLeftForward:

                                                        #the drone has moved left and forward
                                                        print('Drone moved left and forward')
                                                        forward.on()

                                                elif moveLeftBackward:

                                                        #the drone has moved left and backward
                                                        print('Drone moved left and backward')
                                                        backward.on()
                                                              
                                                else:
                                                                
                                                        #drone has not moved 
                                                        print('Drone not moved')
                                                        
                                                        #trun on all the led's
                                                        left.on()
                                                        right.on()
                                                        forward.on()
                                                        backward.on()
                
                                        #update the current position as the previous position
                                        platformXprevious = platformXcurrent
                                        platformYprevious = platformYcurrent

        #displays the image captured along with any edits           
        cv2.imshow("Frame", image)     
	
        # clear the stream in preparation for the next frame
	rawCapture.truncate(0)
	
	# if the `q` key was pressed, break from the for loop
	if key == ord("q"):
		break
