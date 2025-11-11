"""
Auteur:  Gerard Harkema
Datum:   2025-09-19
Versie:  1.00 (eerste versie)

Beschrijving:
Dit script voert objectdetectie uit met behulp van een YOLOv5-model (You Only Look Once, versie 5).
Het model wordt lokaal geladen en gebruikt om objecten te detecteren in beelden
die via een Daheng-camera worden binnengehaald.
"""

# --------------------------------------------------------
# 🔹 IMPORTS
# --------------------------------------------------------
import torch               # PyTorch – gebruikt voor het laden en uitvoeren van het YOLOv5-model
import numpy as np         # Numpy – voor numerieke berekeningen (zoals FPS)
import cv2                 # OpenCV – voor beeldbewerking en het tekenen van kaders/tekst
import time                # Tijdmetingen (voor FPS-berekening)
from DahengAvansLibrary.dahengCameraLibrary import dahengCamera  # Daheng-camera library


# --------------------------------------------------------
# 🔹 KLASSE: YoloV5Detector
# --------------------------------------------------------
class YoloV5Detector:
    """
    Een klasse die zorgt voor:
    - Het laden van het YOLOv5-model
    - Het uitvoeren van inferentie (detectie)
    - Het tekenen van kaders en labels op de gevonden objecten
    """

    def __init__(self):
        # Laad het YOLOv5-model
        self.model = self.load_model()
        # Sla de klasselabels van het model op (namen van te herkennen objecten)
        self.classes = self.model.names
        # Gebruik GPU (indien beschikbaar), anders CPU
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print("\n\nApparaat in gebruik:", self.device)

    def load_model(self):
        """
        Laadt het YOLOv5-model met aangepaste gewichten.
        - Gebruikt torch.hub om het model uit de ultralytics/yolov5-repository te laden
        - Laadt de getrainde gewichten uit het lokale pad 'support/SimpleFruitsv1iyolov5pytorch.pt'
        - Stelt detectieparameters in (confidence en IoU-drempel)
        """
        model = torch.hub.load(
            'ultralytics/yolov5',  # Repository van het model
            'custom',              # Aangepast model laden
            path='support/SimpleFruitsv1iyolov5pytorch.pt',  # Pad naar de gewichten
            force_reload=False     # Niet opnieuw laden als het al in cache staat
        )

        # Stel detectiedrempels in
        model.conf = 0.50  # Minimale zekerheid voor een detectie
        model.iou = 0.65   # IoU-drempel (hoeveel overlap tussen kaders toegestaan is)
        return model

    def score_frame(self, frame):
        """
        Voert inferentie (objectdetectie) uit op één beeld.
        Retourneert:
        - labels: de gedetecteerde objectklassen
        - cord: coördinaten van de bounding boxes (genormaliseerd)
        """
        # Zet model op het juiste apparaat (CPU of GPU)
        self.model.to(self.device)

        # YOLOv5 verwacht een lijst van beelden als invoer
        frame = [frame]
        results = self.model(frame)

        # Toon ruwe resultaten in de console (optioneel, voor debug)
        results.print()
        print(results.xyxy[0])             # Absolute coördinaten van de bounding boxes
        print(results.pandas().xyxy[0])    # Resultaten in Pandas DataFrame

        # Extract labels en genormaliseerde coördinaten (0–1)
        labels, cord = results.xyxyn[0][:, -1], results.xyxyn[0][:, :-1]
        return labels, cord

    def class_to_label(self, x):
        """
        Zet een numeriek klasse-ID om naar de bijbehorende klassenaam.
        """
        return self.classes[int(x)]

    def plot_boxes(self, results, frame):
        """
        Tekent kaders (bounding boxes) en labels op het beeld.
        Alleen kaders met een zekerheid >= 0.2 worden getekend.
        """
        labels, cord = results
        n = len(labels)
        x_shape, y_shape = frame.shape[1], frame.shape[0]  # Beeldafmetingen

        for i in range(n):
            row = cord[i]
            if row[4] >= 0.2:  # Drempelwaarde voor detectiezekerheid
                # Zet genormaliseerde coördinaten om naar pixels
                x1, y1, x2, y2 = (
                    int(row[0] * x_shape),
                    int(row[1] * y_shape),
                    int(row[2] * x_shape),
                    int(row[3] * y_shape),
                )

                bgr = (0, 255, 0)  # Groen kader
                # Teken de rechthoek rond het gedetecteerde object
                cv2.rectangle(frame, (x1, y1), (x2, y2), bgr, 2)
                # Teken het label boven het object
                cv2.putText(frame, self.class_to_label(labels[i]),
                            (x1, y1), cv2.FONT_HERSHEY_SIMPLEX,
                            0.9, bgr, 2)

        return frame


# --------------------------------------------------------
# 🔹 HOOFDPROGRAMMA
# --------------------------------------------------------
def main():
    """
    Hoofdlus:
    - Initialiseert de camera
    - Voert YOLOv5-detectie uit op live videobeelden
    - Toont de resultaten met kaders en FPS-teller
    - Stopt netjes wanneer de gebruiker 'q' indrukt
    """

    # Initialiseer Daheng-camera (camera-index 1, debug aan)
    camera = dahengCamera(1, True)

    # Maak YOLOv5-detector aan
    object_detector = YoloV5Detector()

    # Controleer of de camera correct is geopend
    if not camera.isOpen():
        return

    print("Druk op [q] en vervolgens [Enter] om het programma te stoppen.")

    # --------------------------------------------------------
    # 🔸 Camera-instellingen
    # --------------------------------------------------------
    # Horizontale binning op 4 (meer licht, lagere resolutie)
    camera.BinningHorizontal.set(4)

    # Verticale binning op 4 (minder ruis, lagere resolutie)
    camera.BinningVertical.set(4)

    # Verhoog belichtingstijd (10x de huidige waarde)
    camera.ExposureTime.set(camera.ExposureTime.get() * 10)

    # Automatische gain activeren
    camera.GainAuto.set('Continuous')

    # --------------------------------------------------------
    # 🔸 Start stream en meet FPS
    # --------------------------------------------------------
    camera.startStream()
    start_time = time.perf_counter()

    while True:
        # Neem één frame op van de camera
        image = camera.grab_frame()

        if image is not None:
            # Voer detectie uit
            results = object_detector.score_frame(image)
            image = object_detector.plot_boxes(results, image)

            # Bereken FPS (frames per seconde)
            end_time = time.perf_counter()
            fps = 1 / np.round(end_time - start_time, 3)

            # Toon FPS in beeld
            cv2.putText(image, f'FPS: {int(fps)}',
                        (20, 70), cv2.FONT_HERSHEY_SIMPLEX,
                        1.5, (0, 255, 0), 2)

            # Toon het beeld met detecties
            cv2.imshow("Detected Objects", image)

            # Stoppen bij indrukken van 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                camera.stopStream()
                cv2.destroyAllWindows()
                return

            start_time = end_time  # Herstart FPS-timer
        else:
            # Geen frame ontvangen → stop en sluit af
            camera.stopStream()
            camera.close()
            cv2.destroyAllWindows()
            return


# --------------------------------------------------------
# 🔹 Startpunt van het script
# --------------------------------------------------------
if __name__ == "__main__":
    main()
