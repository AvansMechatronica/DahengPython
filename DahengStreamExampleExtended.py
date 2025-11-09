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

# Schaalfactor om beelden kleiner weer te geven (voor snelheid)
image_scale_factor = 0.3


# ------------------------------------------------------------
# Callbackfunctie voor de OpenCV-trackbar
# ------------------------------------------------------------
def rangeCb(value):
    """Callback die wordt aangeroepen wanneer de schuifbalk wordt aangepast."""
    print(f"Nieuwe ExposureTime waarde (callback): {value}")
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

    # --------------------------------------------------------
    # Start de beeldstream
    # --------------------------------------------------------
    camera.startStream()

    # --------------------------------------------------------
    # Maak OpenCV-venster en trackbar voor ExposureTime
    # --------------------------------------------------------
    cv2.namedWindow("Acquired Image")

    # Haal het bereik van de belichtingstijd op (min/max)
    exp_range = camera.exposureTime.get_range()
    print(f"ExposureTime bereik: {exp_range}")

    # Maak een schuifbalk in het venster voor dynamische aanpassing
    cv2.createTrackbar(
        "ExposureTime",
        "Acquired Image",
        int(exp_range["min"] + 1),  # startwaarde
        int(exp_range["max"]),      # maximumwaarde
        rangeCb                     # callbackfunctie
    )

    # Lees huidige belichtingstijd uit en stel schuifbalk daarop in
    et = camera.exposureTime.get()
    print(f"Huidige ExposureTime: {et}")
    cv2.setTrackbarPos("ExposureTime", "Acquired Image", int(et))

    # --------------------------------------------------------
    # Hoofd-lus: beelden ophalen en tonen
    # --------------------------------------------------------
    while True:
        # Lees de actuele waarde van de schuifbalk
        new_et = cv2.getTrackbarPos("ExposureTime", "Acquired Image")

        # Pas de belichtingstijd van de camera aan
        camera.exposureTime.set(new_et)

        # Haal een nieuw frame op van de camera
        image = camera.grab_frame()

        # Controleer of een geldig beeld is ontvangen
        if image is not None:
            # Verklein het beeld (optioneel)
            resized = cv2.resize(
                image,
                None,
                fx=image_scale_factor,
                fy=image_scale_factor,
                interpolation=cv2.INTER_AREA
            )

            # Toon het beeld
            cv2.imshow("Acquired Image", resized)

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
