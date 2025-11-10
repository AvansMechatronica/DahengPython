# Python-bibliotheekfuncties voor een Daheng-camera

## Importeren van de bibliotheek
In je software dien je de volgende bibliotheek op te nemen om controle te krijgen over een Daheng-camera.
```python
from DahengAvansLibrary.dahengCameraLibrary import dahengCamera
```

## Maak verbinding met een camera
Daheng-camera’s worden automatisch genummerd zodra je ze aansluit. De eerste camera heeft index **1**.  
In onderstaand voorbeeld wordt een camera-object aangemaakt dat verwijst naar de eerst aangesloten camera.
```python
camera = dahengCamera(1)

# Controleer of de camera succesvol is geopend
if not camera.isOpen():
    print("Geen camera gevonden of kan camera niet openen.")
    return
```

## Start een camera-stream
Nadat het camera-object is aangemaakt, dien je de camerastream te starten met onderstaande code.

*Let op: Doe dit niet in een (while-)loop.*
```python
camera.startStream()
```

## Opvragen van een image (foto) uit de camera
Met onderstaande functie kun je een image van de camera verkrijgen.  
Dit is een **NumPy-array**, die geschikt is voor gebruik met **OpenCV**.
```python
image = camera.grab_frame()
```

## Stoppen van de stream
Als je tijdelijk het streamen van de camera wilt stoppen, kan dat met de volgende functie:
```python
camera.stopStream()
```

## Afsluiten van de camera
Aan het einde van je programma dien je de camera netjes af te sluiten met de volgende functie:
```python
camera.close()
```

## Programmeren van camera-features
*(Sectie nog uit te werken)*
