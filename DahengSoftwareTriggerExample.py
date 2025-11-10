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
- Druk op 'q' terwijl het OpenCV-venster actief is om het programma te stoppen.

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
from DahengAvansLibrary.dahengLibrary import dahengCamera  # Daheng wrapper voor camera
import cv2       # OpenCV voor beeldweergave
import time      # Voor vertragingen
import threading # Voor multithreading

# ------------------------------------------------------------
# Globale variabelen
# ------------------------------------------------------------
camera = 0                  # Wordt later geïnitialiseerd in main()
stop_event = threading.Event()  # Event om threads netjes te stoppen

# ------------------------------------------------------------
# Functie: software trigger thread
# ------------------------------------------------------------
def trigger_thread():
    """
    Verstuur periodiek software triggers naar de camera.
    Deze thread blijft lopen totdat 'stop_event' wordt gezet.
    """
    while not stop_event.is_set():
        # Verstuur softwaretrigger om een nieuw beeld vast te leggen
        print("Generating trigger...")
        camera.TriggerSoftware.send_command()

        # Korte pauze tussen triggers om CPU te ontlasten
        time.sleep(3)  # 3 seconden interval tussen triggers

# ------------------------------------------------------------
# Functie: camera thread
# ------------------------------------------------------------
def camera_thread():
    """
    Haal continu beelden op van de camera en toon deze via OpenCV.
    Controleer op stopconditie via stop_event of toetsenbord ('q').
    """
    try:
        while not stop_event.is_set():
            timeout = 5000  # Wacht maximaal 5000 ms op een frame

            # Haal frame op van camera (blokkerend tot timeout)
            image = camera.grab_frame(timeout)

            if image is not None:
                # Toon beeld in OpenCV-venster
                cv2.imshow("Acquired Image (Software Trigger)", image)

                # Stopconditie: toets 'q' indrukken
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    print("⏹️  Programma gestopt door gebruiker.")
                    stop_event.set()  # Signaleer andere threads om te stoppen
                    break
            else:
                # Geen beeld ontvangen -> waarschuwing en stop
                print("⚠️  Geen beeld ontvangen – camera wordt gesloten.")
                stop_event.set()
                break

            # Korte vertraging voor stabiliteit (niet strikt nodig)
            time.sleep(0.5)

    except KeyboardInterrupt:
        # Ctrl+C afvangen en threads netjes stoppen
        print("⏹️  Onderbroken door gebruiker (Ctrl+C).")
        stop_event.set()

# ------------------------------------------------------------
# Hoofdfunctie
# ------------------------------------------------------------
def main():
    """
    Initialiseer camera, activeer software-trigger modus en start threads
    voor het versturen van triggers en ophalen van beelden.
    """
    global camera  # Zorg dat globale camera variabele wordt gebruikt
    camera = dahengCamera(1, True)  # Initialiseer camera (debug=True voor statusinfo)

    # Controleer of camera succesvol is geopend
    if not camera.isOpen():
        print("❌ Geen camera gevonden of kan camera niet openen.")
        return

    # --------------------------------------------------------
    # Binning instellen
    # --------------------------------------------------------
    # Horizontale binning: combineert 4 pixels horizontaal
    camera.BinningHorizontal.set(4)
    # Verticale binning: combineert 4 pixels verticaal
    camera.BinningVertical.set(4)
    # Binning verhoogt lichtgevoeligheid en vermindert ruis, maar verlaagt resolutie

    # Verhoog de huidige belichtingstijd 10x
    # camera.ExposureTime.get() haalt de huidige waarde op in microseconden of milliseconden
    # camera.ExposureTime.set(...) stelt vervolgens de nieuwe waarde in
    camera.ExposureTime.set(camera.ExposureTime.get() * 10)

    # Stel de gain van de camera in op 24
    # Gain verhoogt de gevoeligheid van de sensor, maar kan ruis versterken
    #camera.Gain.set(24)
    camera.GainAuto.set('Continuous')

    # --------------------------------------------------------
    # Software trigger modus instellen
    # --------------------------------------------------------
    camera.TriggerMode.set("On")         # Activeer trigger-modus
    camera.TriggerSource.set("Software") # Stel triggerbron in op software
    print("✅ Camera ingesteld op Software Trigger Mode")
    print("Druk op [q] in het OpenCV-venster om het programma te stoppen.")

    # --------------------------------------------------------
    # Start de camerastream
    # --------------------------------------------------------
    camera.startStream()

    # --------------------------------------------------------
    # Threads starten
    # --------------------------------------------------------
    # Thread 1: ophalen en tonen van beelden
    t_camera = threading.Thread(target=camera_thread)
    # Thread 2: versturen van software triggers
    t_trigger = threading.Thread(target=trigger_thread)
    t_camera.start()
    t_trigger.start()

    # Wacht tot beide threads zijn gestopt
    t_camera.join()
    t_trigger.join()

    # --------------------------------------------------------
    # Camera en vensters netjes afsluiten
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
