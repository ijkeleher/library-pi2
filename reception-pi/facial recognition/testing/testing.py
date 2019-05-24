

# import numpy as np
# import cv2
#
# cap = cv2.VideoCapture(0)
#
# while(True):
#     # Capture frame-by-frame
#     ret, frame = cap.read()
#
#     # Our operations on the frame come here
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#     # Display the resulting frame
#     cv2.imshow('frame',gray)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break
#
# # When everything done, release the capture
# cap.release()
# cv2.destroyAllWindows()


# import the necessary packages
from imutils.video import VideoStream
import argparse
import imutils
import time
import cv2
import os




# load OpenCV's Haar cascade for face detection from disk
detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# initialize the video stream, allow the camera sensor to warm up,

print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()

time.sleep(2.0)
total = 0

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream, clone it, (just
	# in case we want to write it to disk), and then resize the frame
	# so we can apply face detection faster
	frame = vs.read()
	orig = frame.copy()
	frame = imutils.resize(frame, width=400)

	# detect faces in the grayscale frame
	rects = detector.detectMultiScale(
		cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1, 
		minNeighbors=5, minSize=(30, 30))

	# loop over the face detections and draw them on the frame
	for (x, y, w, h) in rects:
		cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

	# show the output frame
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF
 
	# if the `k` key was pressed, write the *original* frame to disk
	# so we can later process it and use it for face recognition
	if key == ord("k"):
		p = os.path.sep.join(['dataset/chrisOLD', "{}.png".format(
			str(total).zfill(5))])
		cv2.imwrite(p, orig)
		total += 1

	# if the `q` key was pressed, break from the loop
	elif key == ord("q"):
		break

# do a bit of cleanup
print("[INFO] {} face images stored".format(total))
print("[INFO] cleaning up...")
cv2.destroyAllWindows()
vs.stop()