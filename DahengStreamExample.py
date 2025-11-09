#!/usr/bin/python
"""
Voorbeeld: Gebruik van een Daheng-camera in streammodus
-------------------------------------------------------

Dit script demonstreert hoe je:
- Een Daheng-camera initialiseert en opent via de DahengAvansLibrary-wrapper.
- De camerastream start.
- Beelden (frames) vastlegt en toont met OpenCV.
- De stream correct stopt en de camera afsluit bij beëindiging.

Bediening:
- Druk op 'q' (en vervolgens Enter) terwijl het OpenCV-venster actief is om te stoppen.

Vereisten:
- Daheng Galaxy SDK geïnstalleerd
- gxipy Python-pakket
- OpenCV (cv2)

Auteur:  Gerard Harkema
Datum:   2025-09-19
Versie:  1.00 (initiële versie)
"""

# Schaalfactor voor het weergegeven beeld (verkleint om prestaties te verbeteren)
image_scale_factor = 0.3

# ------------------------------------------------------------
# Importeren van benodigde bibliotheken
# ------------------------------------------------------------
from DahengAvansLibrary.dahengLibrary import dahengCamera  # Eigen wrapper rond de Daheng SDK
import cv2  # OpenCV voor beeldverwerking en weergave


def main():
    """Hoofdfunctie: initialiseert camera, start streaming en toont beelden."""

    # --------------------------------------------------------
    # Initialiseer de camera
    # --------------------------------------------------------
    # Argumenten:
    # - device_index: index van de camera (meestal 1 bij één aangesloten camera)
    # - debug (optioneel): zet op True voor extra debuguitvoer
    # camera = dahengCamera(1, True)
    camera = dahengCamera(1)

    # Controleer of de camera succesvol is geopend
    if not camera.isOpen():
        print("Geen camera gevonden of kan camera niet openen.")
        return

    print("Druk op [q] en dan [Enter] om het programma te stoppen.")

    # --------------------------------------------------------
    # Start de videostream van de camera
    # --------------------------------------------------------
    camera.startStream()

    # --------------------------------------------------------
    # Hoofd-lus: continue beelden ophalen en tonen
    # --------------------------------------------------------
    while True:
        # Vraag een enkel frame op van de camera
        image = camera.grab_frame()

        # Controleer of een geldig beeld is ontvangen
        if image is not None:
            # Verklein het beeld voor weergave (optioneel)
            resized = cv2.resize(
                image,
                None,
                fx=image_scale_factor,
                fy=image_scale_factor,
                interpolation=cv2.INTER_AREA
            )

            # Toon het verkleinde beeld in een OpenCV-venster
            cv2.imshow("Acquired Image", resized)

            # Controleer of gebruiker op 'q' drukt om te stoppen
            if cv2.waitKey(1) & 0xFF == ord('q'):
                # Stop de stream en sluit het venster
                camera.stopStream()
                cv2.destroyAllWindows()
                return

        else:
            # Als geen beeld ontvangen wordt, sluit de camera netjes af
            print("Geen beeld ontvangen - stream wordt gestopt.")
            camera.stopStream()
            camera.close()
            cv2.destroyAllWindows()
            return


# ------------------------------------------------------------
# Startpunt van het programma
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
