# USAGE
# python picamera_fps_demo.py
# python picamera_fps_demo.py --display 1

#Important Notes
#in ths code the non-threadng code has been removed
#this code is doing video processing using a video thread
#The threads at times will not shut down properly hence giving errors
#this code is calling out to thread PiVideoStream installed in imutils
#thread outputs frames at 32 FPS and a resoluton of 320x240 pixels

#when using the threaded method the porgram is capable of reading:
#200 FPS - without image processing
#60  FPS - with image processing (greyscale,blur,edge)
#55  FPS - with image processing (greyscale,blur,edge,find contours)
#this code executes at 50 FPS now

# import the necessary packages
from __future__ import print_function
from imutils.video.pivideostream import PiVideoStream
from imutils.video import FPS
from picamera.array import PiRGBArray
from picamera import PiCamera
import argparse
import imutils
import time
import cv2
import numpy as np

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-n", "--num-frames", type=int, default=100,
	help="# of frames to loop over for FPS test")
ap.add_argument("-d", "--display", type=int, default=-1,
	help="Whether or not frames should be displayed")
args = vars(ap.parse_args())

# created a *threaded *video stream, allow the camera sensor to warmup,
# and start the FPS counter
print("[INFO] sampling THREADED frames from `picamera` module...")
vs = PiVideoStream().start()
time.sleep(2.0)
fps = FPS().start()

# loop over some frames...this time using the threaded stream
while fps._numFrames < args["num_frames"] :
	# grab the frame from the threaded video stream and resize it
	# to have a maximum width of 400 pixels
	frame = vs.read()
	#the read frame is actually already in numpy format format
	#frame = imutils.resize(frame, width=400)

        status = "No Targets" #string which inidcates no target has been detected

	#Image processing
	# convert the frame to grayscale, blur it, and detect edges
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #converts image from color to greyscale
        blurred = cv2.GaussianBlur(gray, (7, 7), 0) #use GaussianBlur to filter out noise
        edged = cv2.Canny(blurred, 50, 150) #Canny edge detection

        # find contours in the edge map
        (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours detected
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

	# check to see if the frame should be displayed to our screen
	if args["display"] > 0:
		cv2.imshow("Frame", frame)
		key = cv2.waitKey(1) & 0xFF
		
	# update the FPS counter
	fps.update()

        # if the `q` key was pressed, break from the loop
	if key == ord("q"):
		break
	
        
# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
