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

# convert the frame to grayscale, blur it, and detect edges
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #converts image from color to greyscale
blurred = cv2.GaussianBlur(gray, (7, 7), 0) #use GaussianBlur to filter out noise
edged = cv2.Canny(blurred, 50, 150) #Canny edge detection

# find contours in the edge map
(_, cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# loop over the contours
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

	# ensure that the contour passes all our tests
	if keepDims and keepSolidity and keepAspectRatio:
            # draw an outline around the target and update the status text
	    #cv2.drawContours(frame, [approx], -1, (0, 0, 255), 4)
	    status = "Target(s) Acquired"
 
	    # compute the center of the contour region and draw the crosshairs
	    M = cv2.moments(approx)
	    (cX, cY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
	    (startX, endX) = (int(cX - (w * 0.15)), int(cX + (w * 0.15)))
	    (startY, endY) = (int(cY - (h * 0.15)), int(cY + (h * 0.15)))
	    #cv2.line(frame, (startX, cY), (endX, cY), (0, 0, 255), 3)
	    #cv2.line(frame, (cX, startY), (cX, endY), (0, 0, 255), 3)

	    #print('cX: ', cX)
	    #print('cY: ', cY)
            #print('startX: ', startX)
            #print('endX: ', endX)
            #print('startY ', startY)
	    #print('endY :', endY)
	    #print('hull: ', hull)

	    #create a bounding rectangle over the hull
	    rect = cv2.minAreaRect(hull)#returns the center coordinate of the rec and its dimensions and angle of rotation
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            
            cv2.drawContours(frame,[box],0,(0,0,255),2) #draws a frame over the box
            (circle_x, circle_y) = rect[0] #gives the center co-ordinates
            cv2.circle(frame,(int(circle_x),int(circle_y)), 5, (255,0,0), -1) #draw a circle at the center of the circle

            #find the dimensions of the image
            frame_height, frame_width, frame_channels = frame.shape #height = y and width = x
            cv2.circle(frame,(int(frame_width/2),int(frame_height/2)), 5, (255,0,0), -1) #draw a circle at the center of the circle
            
# draw the status text on the frame
cv2.putText(frame, status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

# show the frame and record if a key is pressed
cv2.imshow("Frame", frame)
key = cv2.waitKey(0)

