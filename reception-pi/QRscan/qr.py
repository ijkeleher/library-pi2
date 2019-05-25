# USAGE
# python3 barcode_scanner_console.py

## Acknowledgement
## This code is adapted from:
## https://www.pyimagesearch.com/2018/05/21/an-opencv-barcode-and-qr-code-scanner-with-zbar/
## pip3 install pyzbar

# import the necessary packages
from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2

# initialize the video stream and allow the camera sensor to warm up
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
time.sleep(2.0)

found = set()

# loop over the frames from the video stream
while True:
    # grab the frame from the threaded video stream and resize it to
    # have a maximum width of 400 pixels
    frame = vs.read()
    frame = imutils.resize(frame, width=400)

    # find the barcodes in the frame and decode each of the barcodes
    barcodes = pyzbar.decode(frame)

    # loop over the detected barcodes
    for barcode in barcodes:
        # the barcode data is a bytes object so we convert it to a string
        barcodeData = barcode.data.decode("utf-8")
        barcodeType = barcode.type

        # if the barcode text has not been seen before print it and update the set
        if barcodeData not in found:
            print("[FOUND] Type: {}, Data: {}".format(barcodeType, barcodeData))
            found.add(barcodeData)

    # wait a little before scanning again
    time.sleep(1)

# close the output CSV file do a bit of cleanup
print("[INFO] cleaning up...")
vs.stop()