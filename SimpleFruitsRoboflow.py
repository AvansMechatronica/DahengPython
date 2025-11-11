"""
Auteur:  Gerard Harkema
Datum:   2025-09-19
Versie:  1.00 (eerste versie)

Beschrijving:
Dit script voert objectdetectie uit met behulp van de Roboflow Python SDK in "offline"-modus.
In plaats van de cloud REST API te gebruiken, wordt het model lokaal geladen en
wordt inferentie (objectherkenning) direct uitgevoerd op beelden van een Daheng-camera.
"""

# --------------------------------------------------------
# 🔹 IMPORTS
# --------------------------------------------------------
# Importeer benodigde libraries
# (de import van imagemath_equal wordt niet gebruikt en kan veilig worden verwijderd)
from PIL.ImageMath import imagemath_equal  # (onbenutte import)
from DahengAvansLibrary.dahengCameraLibrary import dahengCamera
from roboflow import Roboflow
import cv2
import time
import numpy as np


# --------------------------------------------------------
# 🔹 KLASSE: RoboflowDetector
# --------------------------------------------------------
class RoboflowDetector:
    """
    Deze klasse verzorgt:
    - Het laden van een getraind Roboflow-model via de SDK
    - Het lokaal uitvoeren van voorspellingen
    - Het tekenen van detectiekaders (bounding boxes) en labels
    """

    def __init__(self):
        # Verbind met Roboflow via API-sleutel
        self.rf = Roboflow(api_key="K3sks4IiHf1jC7nMw6YN")

        # Laad het project 'simplefruits' binnen de werkruimte
        self.project = self.rf.workspace().project("simplefruits")

        # Gebruik versie 1 van het model
        self.model = self.project.version(1).model

    def plot_boxes(self, image):
        """
        Voert detectie uit op het ingevoerde beeld en tekent de
        gevonden objecten met labels en kaders.
        """
        # Voer de voorspelling uit (retourneert JSON-structuur)
        predictions = self.model.predict(image, confidence=40, overlap=30).json()

        # Loop door alle detecties heen
        for prediction in predictions['predictions']:
            print(prediction['class'])

            # Roboflow gebruikt middelpunt-coördinaten; hier worden die omgezet naar hoekpunten
            x0 = prediction['x'] - prediction['width'] / 2
            x1 = prediction['x'] + prediction['width'] / 2
            y0 = prediction['y'] - prediction['height'] / 2
            y1 = prediction['y'] + prediction['height'] / 2

            # Definieer start- en eindpunten van de rechthoek
            start_point = (int(x0), int(y0))
            end_point = (int(x1), int(y1))

            # Teken het kader (blauw)
            cv2.rectangle(image, start_point, end_point, color=(255, 0, 0), thickness=1)

            # Teken labeltekst boven het kader
            cv2.putText(
                image,
                prediction["class"],            # Objectnaam
                (int(x0), int(y0) - 10),        # Positie net boven het kader
                fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                fontScale=0.6,
                color=(0, 255, 0),              # Groen label
                thickness=2
            )
        return image


# --------------------------------------------------------
# 🔹 HOOFDPROGRAMMA
# --------------------------------------------------------
def main():
    """
    Hoofdlus:
    - Start de Daheng-camera
    - Voert Roboflow objectdetectie uit op elke frame
    - Toont de resultaten met FPS-teller
    - Sluit netjes af bij indrukken van 'q'
    """

    # Maak een camera-object aan (index 1, debugging aan)
    camera = dahengCamera(1, True)

    # Maak een objectdetector aan
    object_detector = RoboflowDetector()

    # Controleer of de camera geopend is
    if not camera.isOpen():
        return

    # --------------------------------------------------------
    # 🔸 Camera-instellingen
    # --------------------------------------------------------

    # Stel horizontale binning in op 4
    # ➜ Combineert 4 pixels horizontaal tot één superpixel (meer licht, minder resolutie)
    camera.BinningHorizontal.set(4)

    # Stel verticale binning in op 4
    # ➜ Combineert 4 pixels verticaal tot één superpixel (minder ruis, lagere resolutie)
    camera.BinningVertical.set(4)

    # Verhoog de belichtingstijd 10x
    # ➜ Zorgt voor helderdere beelden, maar kan bewegingsonscherpte veroorzaken
    camera.ExposureTime.set(camera.ExposureTime.get() * 10)

    # Stel de gain in
    # ➜ Verhoogt signaalversterking, maar ook ruis — hier op automatisch ('Continuous')
    camera.GainAuto.set('Continuous')

    # --------------------------------------------------------
    # 🔸 Software-trigger instellen
    # --------------------------------------------------------
    # De camera zal nu alleen een frame vastleggen na een software-trigger.
    # Dit helpt om latency te controleren i.v.m. Roboflow-verwerking.
    camera.TriggerMode.set("On")         # Activeer trigger-modus
    camera.TriggerSource.set("Software") # Gebruik software als triggerbron

    print("✅ Camera ingesteld op Software Trigger Mode")
    print("Druk op [q] in het OpenCV-venster om het programma te stoppen.")

    # --------------------------------------------------------
    # 🔸 Start de stream
    # --------------------------------------------------------
    print("Press [q] and then [Enter] to Exit the Program")
    camera.startStream()

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # 🔹 Verwerkingslus
    # --------------------------------------------------------
    while True:
        # Verstuur softwaretrigger (laat camera een frame opnemen)
        camera.TriggerSoftware.send_command()

        # Lees frame uit de camera
        image = camera.grab_frame(1000)

        if image is not None:
            # Voer objectdetectie uit op het frame
            image = object_detector.plot_boxes(image)

            # Bereken FPS (frames per seconde)
            end_time = time.perf_counter()
            fps = 1 / np.round(end_time - start_time, 3)

            # Teken FPS op het beeld
            cv2.putText(image, f'FPS: {int(fps)}',
                        (20, 70), cv2.FONT_HERSHEY_SIMPLEX,
                        1.5, (0, 255, 0), 2)

            # Toon het beeld met detecties
            cv2.imshow("Detected objects Image", image)

            # Stop bij 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.stopStream()
                cv2.destroyAllWindows()
                return

            # Reset tijd voor volgende FPS-berekening
            start_time = end_time
        else:
            # Als geen frame wordt ontvangen, sluit alles netjes af
            camera.stopStream()
            camera.close()
            cv2.destroyAllWindows()
            return


# --------------------------------------------------------
# 🔹 Startpunt van het script
# --------------------------------------------------------
if __name__ == "__main__":
    main()
