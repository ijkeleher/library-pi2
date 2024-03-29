#!/usr/bin/env python3

import time
from imutils.video import VideoStream
import imutils
from pyzbar import pyzbar


class QRscan:
    """
    QR Code scanner
    """

    def scan(self):
        """
        scan qr code to get information

        Return:
            barcodeData: a bytes object
        """

        # initialize the video stream and allow the camera sensor to warm up
        print("[INFO] starting video stream...")
        video_stream_obj = VideoStream(src=0)
        video_stream = video_stream_obj.start()
        time.sleep(2.0)

        # found = set()

        # loop over the frames from the video stream
        while True:
            # grab the frame from the threaded video stream and resize it to
            # have a maximum width of 400 pixels
            frame = video_stream.read()
            frame = imutils.resize(frame, width=400)

            # find the barcodes in the frame and decode each of the barcodes
            barcodes = pyzbar.decode(frame)

            # loop over the detected barcodes
            for barcode in barcodes:
                # the barcode data is a bytes object so we convert it to a
                # string
                barcode_data = barcode.data.decode("utf-8")
                # barcodeType = barcode.type
                video_stream_obj.stop()	
                return barcode_data


if __name__ == "__main__":
    QRscan().scan()
