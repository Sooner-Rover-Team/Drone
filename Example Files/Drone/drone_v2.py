#This code takes a snapshot and detects the square
#Has issues with lighting
#Changed the sleep time from 0.1 to 0.2 to detect the white square without additional external lighting help
#can only detect one square target
#in a new review, this code can detect two square targets
#targets have to white or shinny white with a well outlined edge probably in black


 # import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
rawCapture = PiRGBArray(camera)
 
# allow the camera to warmup
time.sleep(0.2) #this setting brightens up the image
 
# grab an image from the camera
camera.capture(rawCapture, format="bgr") #the image captured is in the color format
frame = rawCapture.array

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

# convert the frame to grayscale, blur it, and detect edges
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #converts image from color to greyscale
blurred = cv2.GaussianBlur(gray, (7, 7), 0) #use GaussianBlur to filter out noise
edged = cv2.Canny(blurred, 50, 150) #Canny edge detection

# find contours in the edge map
(_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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
	    cv2.drawContours(frame, [approx], -1, (0, 0, 255), 4)
	    status = "Target(s) Acquired"
	    
	    # compute the center of the contour region and draw the crosshairs
	    M = cv2.moments(approx)
	    (platformX, platformY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"])) #computes the center of the square contour

            cv2.circle(frame,(int(platformX),int(platformY)), 5, (0,0,255), -1) #draw a circle at the center of the frame captured

            #THE CODES BELOW ARE AN UPDATE FROM drone_v1.py

            #find which quadrant the target is in
            #below checks for Q1 boundaries
            inQ1X = platformX > 0 and platformX <= 360
            inQ1Y = platformY > 0 and platformY <= 240

            #below checks for Q2 boundaries
            inQ2X = platformX > 360 and platformX < 720
            inQ2Y = platformY > 0 and platformY < 240

            #below checks for Q3 boundaries
            inQ3X = platformX >= 360 and platformX < 720
            inQ3Y = platformY > 0 and platformY <= 240

            #below checks for Q4 boundaries
            inQ4X = platformX > 0 and platformX < 360
            inQ4Y = platformY > 240 and platformY < 480

            #decision uopn first platform detection
            if first_detection == False:

                #current platform position initialize
                platformXcurrent = platformX - 360
                platformYcurrent = -1*(platformY - 240)
                    
                #previous platform postion initialize
                platformXprevious = platformXcurrent
                platformYprevious = platformYcurrent

            else:  #this shows that the platform had been detected once and now is being tracked

                #update current position in Q1
                platformXcurrent = platformX - 360
                platformYcurrent = -1*(platformY - 240)

                #find out how much the platform has moved
                movementX = platformXcurrent - platformXprevious
                movementY = platformYcurrent - platformYprevious

                #movement logics
                moveRightQ14     = platformXprevious < platformXcurrent
                moveLeftQ14      = platformXprevious > platformXcurrent

                moveRightQ23     = platformXprevious > platformXcurrent
                moveLeftQ23      = platformXprevious < platformXcurrent
                
                moveForawrdQ12   = platformYprevious < platformYcurrent
                moveBackwardQ12  = platformYprevious > platformYcurrent

                moveForwardQ34   = platformYprevious > platformYcurrent
                moveBackwardQ34  = platformYprevious < platformYcurrent

                #check which quadrant the platform is in
                if inQ1X and inQ1Y: #check if the platform is in Q1

                    if moveRightQ14 and moveForwardQ12: #platform has moved right and forward
                        
                        print('The platform has moved ', abs(movementX), 'right and ', abs(movementY), 'forward')

                    elif moveRightQ14 and moveBackwardQ12: #platform has moved right and backward

                        print('The platform has moved ', abs(movementX), 'right and ', abs(movementY), 'backward')

                    elif moveLeftQ14 and moveForwardQ12: #platform has moved left and forward

                        print('The platform has moved ', abs(movementX), 'left and ', abs(movementY), 'forward')

                    else: #platform has moved left and backward

                        print('The platform has moved ', abs(movementX), 'left and ', abs(movementY), 'backward')

                elif inQ2X and inQ2Y: #check if the platform is in Q2

                    if moveRightQ23 and moveForwardQ12: #platform has moved right and forward
                        
                        print('The platform has moved ', abs(movementX), 'right and ', abs(movementY), 'forward')

                    elif moveRightQ23 and moveBackwardQ12: #platform has moved right and backward

                        print('The platform has moved ', abs(movementX), 'right and ', abs(movementY), 'backward')

                    elif moveLeftQ23 and moveForwardQ12: #platform has moved left and forward

                        print('The platform has moved ', abs(movementX), 'left and ', abs(movementY), 'forward')

                    else: #platform has moved left and backward

                        print('The platform has moved ', abs(movementX), 'left and ', abs(movementY), 'backward')

                elif inQ3X and inQ3Y: #check if the platform is in Q3

                    if moveRightQ23 and moveForwardQ34: #platform has moved right and forward
                        
                        print('The platform has moved ', abs(movementX), 'right and ', abs(movementY), 'forward')

                    elif moveRightQ23 and moveBackwardQ34: #platform has moved right and backward

                        print('The platform has moved ', abs(movementX), 'right and ', abs(movementY), 'backward')

                    elif moveLeftQ23 and moveForwardQ34: #platform has moved left and forward

                        print('The platform has moved ', abs(movementX), 'left and ', abs(movementY), 'forward')

                    else: #platform has moved left and backward

                        print('The platform has moved ', abs(movementX), 'left and ', abs(movementY), 'backward')

                else: #platform is in Q4

                    if moveRightQ14 and moveForwardQ34: #platform has moved right and forward
                        
                        print('The platform has moved ', abs(movementX), 'right and ', abs(movementY), 'forward')

                    elif moveRightQ14 and moveBackwardQ34: #platform has moved right and backward

                        print('The platform has moved ', abs(movementX), 'right and ', abs(movementY), 'backward')

                    elif moveLeftQ14 and moveForwardQ34: #platform has moved left and forward

                        print('The platform has moved ', abs(movementX), 'left and ', abs(movementY), 'forward')

                    else: #platform has moved left and backward

                        print('The platform has moved ', abs(movementX), 'left and ', abs(movementY), 'backward')
                    
                #update the current position as the previous position
                platformXprevious = platformXcurrent
                platformYprevious = platformYcurrent
                            
# draw the status text on the frame
cv2.putText(frame, status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# show the frame and record if a key is pressed
cv2.imshow("Frame", frame)
key = cv2.waitKey(0) #press any key to exit

