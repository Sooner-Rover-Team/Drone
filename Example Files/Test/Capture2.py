#This code is to take a snap shot and do image processing and it will
#be timed to see how long it takes to process a single image

#Important Notes
#It took the program to process the image in 0.0587639808655 seconds
#or it took 58.764 milliseconds for the code to process a single image
#however it took, 0.601491928101 seconds just to capture and convert image
#to Numpy array format (601.491 milliseconds)
#if you capture the image at a lower resolution
#it takes a shorter time but quality is very poor and square detection poor

#When the picture quality is lowered from (720 x 480) to (320 x 240)
#the Pi takes a picture under 0.47976398468 seconds
#or 479.764 milliseconds
#it requires more light to detect the image
#it has beenb found that the warm up time plays a role
#in capturing an image, so with a warmup time of 0.2 seconds delays
#the capturing process longer

#import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import time
 
# initialize the camera and grab a reference to the raw camera capture
# camera resolution is set low for efficiency
camera = PiCamera()
camera.resolution = (320, 240)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(320, 240))

# allow the camera to warmup
time.sleep(0.1) #this setting brightens up the image

start_time = time.time() #starts timer
 
# grab an image from the camera
camera.capture(rawCapture, format="bgr") #the image captured is in the color format
frame = rawCapture.array #represents the image in an NUmpy array

print("-- %s seconds --" % (time.time() - start_time))

#start_time = time.time() #starts timer

status = "No Targets" #string which inidcates no target has been detected

# convert the frame to grayscale, blur it, and detect edges
gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #converts image from color to greyscale
blurred = cv2.GaussianBlur(gray, (7, 7), 0) #use GaussianBlur to filter out noise
edged = cv2.Canny(blurred, 50, 150) #Canny edge detection

# find contours in the edge map
(cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

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

            #Update status text
	    status = "Target(s) Acquired"

	    #create a bounding rectangle over the hull
	    rect = cv2.minAreaRect(hull)#returns the center coordinate of the rec and its dimensions and angle of rotation
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            #(center_x, center_y) = rect[0] gives the center co-ordintes of the rectangle

            cv2.drawContours(frame,[box],0,(0,0,255),2) #draws a frame over the box

# draw the status text on the frame
cv2.putText(frame, status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

#prints the amount of time that has elapsed when processing a single frame
#print("-- %s seconds --" % (time.time() - start_time))  

# show the frame and record if a key is pressed
cv2.imshow("Frame", frame)
key = cv2.waitKey(0)
	    





