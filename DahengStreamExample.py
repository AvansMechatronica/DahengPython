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
from DahengAvansLibrary.dahengFeature import featureType



# ------------------------------------------------------------
# Importeren van benodigde bibliotheken
# ------------------------------------------------------------
from DahengAvansLibrary.dahengCameraLibrary import dahengCamera  # Eigen wrapper rond de Daheng SDK
import cv2  # OpenCV voor beeldverwerking en weergave


def main():
    """Hoofdfunctie: initialiseert camera, start streaming en toont beelden."""

    # --------------------------------------------------------
    # Initialiseer de camera
    # --------------------------------------------------------
    # Argumenten:
    # - device_index: index van de camera (meestal 1 bij één aangesloten camera)
    # - debug (optioneel): zet op True voor extra debug uitvoer
    # camera = dahengCamera(1, True)
    camera = dahengCamera(1,True)

    # Controleer of de camera succesvol is geopend
    if not camera.isOpen():
        print("Geen camera gevonden of kan camera niet openen.")
        return

    print("Druk op [q] en dan [Enter] om het programma te stoppen.")

    # --------------------------------------------------------
    # Start de videostream van de camera
    # --------------------------------------------------------
    print(f"Binning Horizontal Range: {camera.BinningHorizontal.get_range()}")
    print(f"Binning Vertical Range: {camera.BinningVertical.get_range()}")

    # Stel de horizontale binningfactor in op 4
    # Binning combineert meerdere pixels tot één grotere 'superpixel'.
    # Dit verhoogt de lichtgevoeligheid, maar verlaagt de resolutie.
    camera.BinningHorizontal.set(4)

    # Stel de verticale binningfactor in op 4
    # Hierdoor worden telkens 4 pixels verticaal gecombineerd.
    # Dit resulteert in een kleinere afbeelding, maar met minder ruis en hogere lichtopbrengst.
    camera.BinningVertical.set(4)

    # Verhoog de huidige belichtingstijd 10x
    # camera.ExposureTime.get() haalt de huidige waarde op in microseconden of milliseconden
    # camera.ExposureTime.set(...) stelt vervolgens de nieuwe waarde in
    camera.ExposureTime.set(camera.ExposureTime.get() * 10)

    # Stel de gain van de camera in op 24
    # Gain verhoogt de gevoeligheid van de sensor, maar kan ruis versterken
    #camera.Gain.set(24)
    camera.GainAuto.set('Continuous')

    camera.startStream()

    # --------------------------------------------------------
    # Hoofd-lus: continue beelden ophalen en tonen
    # --------------------------------------------------------
    while True:
        # Vraag een enkel frame op van de camera
        image = camera.grab_frame()

        # Controleer of een geldig beeld is ontvangen
        if image is not None:

            # Toon het verkleinde beeld in een OpenCV-venster
            cv2.imshow("Acquired Image", image)

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
