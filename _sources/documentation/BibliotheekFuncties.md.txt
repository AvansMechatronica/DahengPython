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

> **Let op:**: Doe dit niet in een (while-)loop.
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
Er zijn zogeheten functies waarmee je verschillende instellingen van de camera kunt opvragen en wijzigen.  
Deze instellingen worden *features* genoemd in de documentatie van Daheng.  
Voorbeelden van features zijn:

* **Gain**
* **ExposureTime**
* **TriggerMode**

Je kunt in het bestand *dahengFeatureList.py* in de map *DahengAvansLibrary* bekijken welke features zijn geïmplementeerd.  
De belangrijkste functies van iedere feature worden hieronder beschreven.

Elke feature heeft een aantal functies die je in Python kunt gebruiken. Hieronder staan de belangrijkste uitgelegd.

---

### Verkrijgen van het bereik
Met onderstaande functie verkrijg je het bereik van de feature als een Python-dictionary.

> **Let op:** De dictionary-items zijn afhankelijk van het featuretype.  
> Featuretypen zijn gedefinieerd in het bestand *dahengFeatureType.py* in de map *DahengAvansLibrary*.

```python
range = camera.<feature>.get_range()
range_minimaal = range["min"]
range_maximaal = range["max"]
```

---

### Verkrijgen van de huidige ingestelde waarde
Met onderstaande functie kun je de huidige waarde van een feature opvragen:
```python
current_value = camera.<feature>.get()
```

---

### Instellen van een nieuwe waarde
Met onderstaande functie kun je de waarde van een feature wijzigen.

> **Let op:** Het type (*int*, *float*, *bool*, …) van de nieuwe waarde (`new_value`) moet overeenkomen met het featuretype.

```python
camera.<feature>.set(new_value)
```

---

### Verzenden van een commando
Met onderstaande functie kun je een commando van de camera uitvoeren, bijvoorbeeld een *SoftwareTrigger*:
```python
camera.<feature>.send_command()
```

---

### Zelf features toevoegen
De lijst met features van de Daheng-camera is lang; daarom zijn niet alle features geïmplementeerd.  
Je kunt in het bestand *dahengFeatureList.py* in de map *DahengAvansLibrary* zelf extra features toevoegen.  
Uiteraard kun je alleen features toevoegen die worden ondersteund door de Daheng-driver van de camera.



Een volledige lijst met beschikbare features vind je in de  
**[Daheng Python Manual](PythonInterfaceDevelopmentUserManual.pdf)**, Appendix 3.4.  

> **Tip:** Gebruik de exacte namen en het juiste type zoals vermeld in de handleiding.

>**Let op:** Als je een feature toevoegt met een naam die niet in de originele Daheng-driver bestaat, zal een je code een foutmelding krijgen bij het uitvoeren van de betreffende functie.
Deze worden in de kleur rood weergegeven in je Terminal.