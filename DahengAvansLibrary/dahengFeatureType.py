#!/usr/bin/python
# doel: Klasse voor het beheren van verschillende featuretypes van een Daheng-camera
# auteur: Gerard Harkema
# datum: 2024-06-17
# versie: 1.00 initiële versie
#
from enum import Enum

# ============================================================
# Enumeratie: featureType
# Doel: definieert de mogelijke typen features die de camera kan hebben
# ============================================================
class featureType(Enum):
    Integer = 1   # Geheel getal
    Float = 2     # Kommagetal
    String = 3    # Tekststring
    Bool = 4      # Boolean (True/False)
    Enum = 5      # Enumeratie (lijst van vooraf bepaalde waarden)
    Command = 6   # Commando (uitvoerbare actie)
    Buffer = 7    # Buffer