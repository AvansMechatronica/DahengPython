#!/usr/bin/python
"""
Voorbeeld: Gebruik van Daheng Camera in software-trigger modus
--------------------------------------------------------------

Dit script demonstreert hoe je:
- Een Daheng-camera initialiseert en opent via de DahengAvansLibrary-wrapper.
- De camerastream start in "Software Trigger"-modus.
- Via software een triggercommando geeft om beelden vast te leggen.
- Beelden toont met OpenCV.
- De camera en stream netjes afsluit bij beëindiging.

Bediening:
- Druk op 'q' (en daarna Enter) terwijl het OpenCV-venster actief is om te stoppen.

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
from DahengAvansLibrary.dahengLibrary import dahengCamera
import cv2
import time

# Schaalfactor voor het tonen van beelden (verkleinen = sneller)
image_scale_factor = 0.3


# ------------------------------------------------------------
# Hoofdfunctie
# ------------------------------------------------------------
def main():
    """Initialiseer camera, activeer software-trigger en verwerk beelden."""

    # --------------------------------------------------------
    # Initialiseer camera (debug=True geeft extra statusinformatie)
    # --------------------------------------------------------
    camera = dahengCamera(1, True)

    # Controleer of camera succesvol is geopend
    if not camera.isOpen():
        print("❌ Geen camera gevonden of kan camera niet openen.")
        return

    # --------------------------------------------------------
    # Stel camera in op software-trigger modus
    # --------------------------------------------------------
    camera.TriggerMode.set("On")           # Activeer trigger-modus
    camera.TriggerSource.set("Software")   # Stel triggerbron in op software
    print("✅ Camera ingesteld op Software Trigger Mode")

    print("Druk op [q] en dan [Enter] om het programma te stoppen.")

    # --------------------------------------------------------
    # Start beeldstream
    # --------------------------------------------------------
    camera.startStream()

    # --------------------------------------------------------
    # Hoofdlus: stuur softwaretriggers en toon beelden
    # --------------------------------------------------------
    try:
        while True:
            # Verstuur softwaretrigger om een nieuw beeld vast te leggen
            camera.TriggerSoftware.send_command()

            # Wacht en haal het beeld op
            image = camera.grab_frame()

            if image is not None:
                # Schaal beeld (optioneel)
                resized = cv2.resize(
                    image,
                    None,
                    fx=image_scale_factor,
                    fy=image_scale_factor,
                    interpolation=cv2.INTER_AREA
                )

                # Toon beeld in OpenCV-venster
                cv2.imshow("Acquired Image (Software Trigger)", resized)

                # Stopconditie
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("⏹️  Programma gestopt door gebruiker.")
                    break
            else:
                print("⚠️  Geen beeld ontvangen – camera wordt gesloten.")
                break

            # Voeg een korte vertraging toe tussen triggers (500 ms)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("⏹️  Onderbroken door gebruiker (Ctrl+C).")

    # --------------------------------------------------------
    # Sluit camera en vensters netjes af
    # --------------------------------------------------------
    camera.stopStream()
    camera.close()
    cv2.destroyAllWindows()
    print("✅ Camera gesloten en programma beëindigd.")


# ------------------------------------------------------------
# Startpunt
# ------------------------------------------------------------
if __name__ == "__main__":
    main()
