#!/usr/bin/python
"""
Example: Using Daheng Camera in Stream Mode
-------------------------------------------

This script demonstrates how to:
- Initialize and open a Daheng camera using the DahengAvansLibrary wrapper.
- Start image streaming.
- Capture frames and display them using OpenCV.
- Gracefully stop the stream and close the camera.

Controls:
- Press 'q' (and then Enter) while the OpenCV window is active to stop streaming and exit.

Requirements:
- Daheng Galaxy SDK installed
- gxipy Python package
- OpenCV (cv2)

Author: Gerard Harkema
Date:   2025-09-19
Version: 1.00 (initial version)
"""

# import the Daheng library
from DahengAvansLibrary.DahengLibrary import dahengCamera
import cv2

def rangeCb(value):
    print(value)
    pass

def main():
    #camera = dahengCamera(1, True)


    camera = dahengCamera(1)
    if not camera.isOpen():
        return
    print("Press [q] and then [Enter] to Exit the Program")

    camera.startStraem()

    cv2.namedWindow('Acquired Image')
    range = camera.exposureTime.get_range()
    print(range)
    cv2.createTrackbar('ExposureTime', "Acquired Image", int(range['min'] + 1), int(range['max']), rangeCb)
    #cv2.createTrackbar('ExposureTime', 'Acquired Image', 0, 100, rangeCb)

    et = camera.exposureTime.get()
    print("Current exposure time 1: {}".format(et))
    cv2.setTrackbarPos('ExposureTime', "Acquired Image", int(et))
#    camera.gain.set()

    while True:
        new_et = cv2.getTrackbarPos('ExposureTime', "Acquired Image")
        camera.exposureTime.set(new_et)
        image = camera.grab_frame()
        if image is not None:
            resized = cv2.resize(image, None, fx=0.3, fy=0.3, interpolation=cv2.INTER_AREA)
            cv2.imshow("Acquired Image", resized)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.stopStraem()
                cv2.destroyAllWindows()
                return
        else:
            camera.stopStraem()
            camera.close()
            cv2.destroyAllWindows()
            return


if __name__ == "__main__":
    main()
