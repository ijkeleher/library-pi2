from imutils.video import VideoStream
import imutils
import time
import cv2

class Facedetect:

    def getidentity(self):

        detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        print("[INFO] starting video stream...")
        vs = VideoStream(src=0).start()

        time.sleep(2.0)
        total = 0

        # loop over the frames from the video stream
        while True:

            frame = vs.read()
            orig = frame.copy()
            frame = imutils.resize(frame, width=400)

            # detect faces in the grayscale frame
            faces = detector.detectMultiScale(
                cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), scaleFactor=1.1,
                minNeighbors=5, minSize=(30, 30))

            # loop over the face detections and draw them on the frame
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            face_file_name = "dataset/chrisOLD/img.png"
            roi_color = frame[y:y + h, x:x + w]
            cv2.imwrite(face_file_name, roi_color)

            src = cv2.imread("dataset/chrisOLD/img.png", cv2.IMREAD_COLOR)
            hist1 = cv2.calcHist([src], [0], None, [256], [0, 256])
            src0 = cv2.imread("dataset/chrisOLD/00000.png", cv2.IMREAD_COLOR)
            hist2 = cv2.calcHist([src0], [0], None, [256], [0, 256])

            sc0 = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)

            if sc0 < 0.2:
                cv2.putText(frame, "Chris", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
                print("Chris detected")
                return "Chris"

            print(sc0)

            cv2.imshow("Frame", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        vs.release()
        cv2.destroyAllWindows()
