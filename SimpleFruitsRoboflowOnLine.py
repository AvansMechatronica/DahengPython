"""
Author: Gerard Harkema
Date:   2025-09-19
Version: 1.00 (initial version)

This script uses the Roboflow cloud API for real-time object detection.
It captures images from a Daheng camera, sends them to Roboflow for inference,
and displays the annotated results with bounding boxes and FPS.
"""

# Roboflow SDK example usage (commented out).
# This section shows how to initialize a Roboflow project locally,
# but the script below instead uses the REST API directly.
from roboflow import Roboflow
# rf = Roboflow(api_key="K3sks4IiHf1jC7nMw6YN")
# project = rf.workspace().project("simplefruits")
# model = project.version(1).model
# print(model.predict("your_image.jpg", confidence=40, overlap=30).json())

# ========== Dependencies ==========
import cv2
import base64
import numpy as np
import requests
from DahengAvansLibrary.DahengLibrary import dahengCamera
import time

# ========== Roboflow Configuration ==========
ROBOFLOW_API_KEY = "K3sks4IiHf1jC7nMw6YN"   # Your Roboflow API key
ROBOFLOW_MODEL = "simplefruits/1"           # Project name + version
ROBOFLOW_SIZE = 416                         # Target image size for model input


class RoboflowDetectorOnline:
    """
    A detector class that:
    - Prepares images for Roboflow API
    - Sends them for inference
    - Returns annotated images with bounding boxes drawn by Roboflow
    """

    def __init__(self):
        # Construct the upload URL for Roboflow inference API
        self.upload_url = "".join([
            "https://detect.roboflow.com/",
            ROBOFLOW_MODEL,
            "?access_token=",
            ROBOFLOW_API_KEY,
            "&format=image",   # Response format = annotated image
            "&stroke=5"        # Thickness of bounding box lines
        ])

    def plot_boxes(self, image):
        """
        Sends a frame to the Roboflow cloud API for detection
        and returns the annotated image.
        """
        # Get image dimensions
        height, width, channels = image.shape

        # Rescale image so the larger dimension = ROBOFLOW_SIZE
        scale = ROBOFLOW_SIZE / max(height, width)
        img = cv2.resize(image, (round(scale * width), round(scale * height)))

        # Encode image to JPEG -> then to base64 string for API
        retval, buffer = cv2.imencode('.jpg', image)
        img_str = base64.b64encode(buffer)

        # Clean up URL (remove accidental leading spaces)
        upload_url = self.upload_url.lstrip(" ")

        # Send POST request to Roboflow Infer API
        resp = requests.post(
            upload_url,
            data=img_str,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            stream=True  # Stream response since it's an image
        ).raw

        # Convert response (bytes) back into an OpenCV image
        image = np.asarray(bytearray(resp.read()), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)

        return image


def main():
    """
    Main function to:
    - Open Daheng camera stream
    - Run Roboflow detection on each frame
    - Display results with bounding boxes and FPS
    - Exit on 'q' key press
    """
    # Initialize camera (camera ID=1, color=True)
    camera = dahengCamera(1, True)
    # Initialize Roboflow detector
    object_detector = RoboflowDetectorOnline()

    # Exit if camera cannot be opened
    if not camera.isOpen():
        return

    print("Press [q] and then [Enter] to Exit the Program")
    camera.startStraem()

    # Initialize FPS timer
    start_time = time.perf_counter()

    while True:
        image = camera.grab_frame()  # Capture a frame
        if image is not None:
            # Get annotated image from Roboflow
            image = object_detector.plot_boxes(image)

            # Calculate FPS
            end_time = time.perf_counter()
            fps = 1 / np.round(end_time - start_time, 3)

            # Overlay FPS on top-left corner
            cv2.putText(image, f'FPS: {int(fps)}',
                        (20, 70), cv2.FONT_HERSHEY_SIMPLEX,
                        1.5, (0, 255, 0), 2)

            # Show results
            cv2.imshow("Detected objects Image", image)

            # Quit on 'q' key
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.stopStraem()
                cv2.destroyAllWindows()
                return

            start_time = end_time  # Reset FPS timer
        else:
            # Stop if no frame is captured
            camera.stopStraem()
            camera.close()
            cv2.destroyAllWindows()
            return


if __name__ == "__main__":
    main()
