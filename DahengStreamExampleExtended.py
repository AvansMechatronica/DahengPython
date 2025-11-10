#!/usr/bin/python
"""
Voorbeeld: Gebruik van Daheng-camera in streammodus met ExposureTime-regeling
-----------------------------------------------------------------------------

Dit script demonstreert hoe je:
- Een Daheng-camera initialiseert en opent via de DahengAvansLibrary-wrapper.
- De camerastream start.
- Frames vastlegt en toont met OpenCV.
- De belichtingstijd (ExposureTime) dynamisch aanpast met een schuifbalk (trackbar).
- De stream correct stopt en de camera afsluit.

Bediening:
- Gebruik de schuifbalk 'ExposureTime' om de belichtingstijd aan te passen.
- Druk op 'q' (en daarna Enter) om het programma te stoppen.

Vereisten:
- Daheng Galaxy SDK geïnstalleerd
- gxipy Python-pakket
- OpenCV (cv2)

Auteur:  Gerard Harkema
Datum:   2025-09-19
Versie:  1.00 (initiële versie)
"""

# ------------------------------------------------------------
# Imports
# ------------------------------------------------------------
from DahengAvansLibrary.dahengLibrary import dahengCamera  # Wrapper voor Daheng-camera’s
import cv2                                                  # OpenCV voor beeldverwerking


# ------------------------------------------------------------
# Callbackfunctie voor de OpenCV-trackbar
# ------------------------------------------------------------
def rangeCb(value):
    pass  # Geen verdere actie nodig – de waarde wordt in de hoofdloop opgehaald


# ------------------------------------------------------------
# Hoofdfunctie
# ------------------------------------------------------------
def main():
    """Initialiseer de camera, start streaming en stel exposure-regeling in."""

    # --------------------------------------------------------
    # Initialiseer camera
    # --------------------------------------------------------
    # camera = dahengCamera(1, True)  # Debugmodus inschakelen indien gewenst
    camera = dahengCamera(1)

    if not camera.isOpen():
        print("❌ Geen camera gevonden of kan camera niet openen.")
        return

    print("✅ Camera geopend.")
    print("Druk op [q] en dan [Enter] om het programma te stoppen.")

    # Stel de horizontale binningfactor in op 4
    # Binning combineert meerdere pixels tot één grotere 'superpixel'.
    # Dit verhoogt de lichtgevoeligheid, maar verlaagt de resolutie.
    camera.BinningHorizontal.set(4)

    # Stel de verticale binningfactor in op 4
    # Hierdoor worden telkens 4 pixels verticaal gecombineerd.
    # Dit resulteert in een kleinere afbeelding, maar met minder ruis en hogere lichtopbrengst.
    camera.BinningVertical.set(4)

    # --------------------------------------------------------
    # Start de beeldstream
    # --------------------------------------------------------
    camera.startStream()

    # --------------------------------------------------------
    # Maak OpenCV-venster en trackbar voor ExposureTime
    # --------------------------------------------------------
    window_name = "Acquired Image"
    cv2.namedWindow(window_name)

    # Haal het bereik van de belichtingstijd op (min/max)
    exp_range = camera.ExposureTime.get_range()
    print(f"ExposureTime bereik: {exp_range}")

    gain_range = camera.Gain.get_range()
    print(f"Bain bereik: {exp_range}")


    # Maak een schuifbalk in het venster voor dynamische aanpassing
    cv2.createTrackbar(
        "ExposureTime",
        window_name,
        int(exp_range["min"] + 1),  # startwaarde
        int(exp_range["max"]),      # maximumwaarde
        rangeCb                     # callbackfunctie
    )

    cv2.createTrackbar(
        "Gain",
        window_name,
        int(gain_range["min"] + 1),  # startwaarde
        int(gain_range["max"]),      # maximumwaarde
        rangeCb                     # callbackfunctie
    )

    # Lees huidige belichtingstijd uit en stel schuifbalk daarop in
    et = camera.ExposureTime.get()
    print(f"Huidige ExposureTime: {et}")
    cv2.setTrackbarPos("ExposureTime", window_name, int(et))

    gain = camera.Gain.get()
    print(f"Huidige Gain: {gain}")
    cv2.setTrackbarPos("Gain", window_name, int(gain))

    # --------------------------------------------------------
    # Hoofd-lus: beelden ophalen en tonen
    # --------------------------------------------------------
    while True:
        # Lees de actuele waarde van de schuifbalk
        new_et = cv2.getTrackbarPos("ExposureTime", window_name)
        new_gain = cv2.getTrackbarPos("Gain", window_name)

        # Pas de belichtingstijd van de camera aan
        camera.ExposureTime.set(new_et)
        camera.Gain.set(new_gain)

        # Haal een nieuw frame op van de camera
        image = camera.grab_frame()

        # Controleer of een geldig beeld is ontvangen
        if image is not None:

            # Toon het beeld
            cv2.imshow(window_name, image)

            # Stopconditie: druk op 'q'
            if cv2.waitKey(1) & 0xFF == ord("q"):
                print("⏹️  Stoppen met streamen...")
                camera.stopStream()
                cv2.destroyAllWindows()
                return
        else:
            # Als geen beeld wordt ontvangen, camera netjes sluiten
            print("⚠️ Geen beeld ontvangen. Camera wordt gesloten.")
            camera.stopStream()
            camera.close()
            cv2.destroyAllWindows()
            return


# ------------------------------------------------------------
# Startpunt van het script
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
