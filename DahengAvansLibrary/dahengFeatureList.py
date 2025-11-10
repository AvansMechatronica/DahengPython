#!/usr/bin/python
# doel: Klasse voor het beheren van verschillende featuretypes van een Daheng-camera
# auteur: Gerard Harkema
# datum: 2024-06-17
# versie: 1.00 initiële versie



from DahengAvansLibrary.dahengFeatureType import *

# Vul hier features toe die je wilt gebruiken
# zie 3.4. Feature Parameter
# Python Interface Development User Manual
# Na toevoeging zijn ze als object beschikbaar in je software
features = [
    # zie 3.4.1. Device feature parameter
    # DeviceInformation Section
    # ImageFormat Section
    ("BinningHorizontal", featureType.Integer),
    ("BinningVertical", featureType.Integer),
    # TransportLayer Section
    # DigitalIO Section
    # AnalogControls Section
    ("Gain", featureType.Float),
    ("GainAuto", featureType.Enum),
    # CustomFeature Section
    # UserSetControl Section
    ("UserSetSelector", featureType.Enum),
    ("UserSetLoad", featureType.Command),
    # Event Section
    # LUT Section
    # Color Transformation Control
    # ChunkData Section
    # Device Feature
    # AcquisitionTrigger Section
    ("ExposureTime", featureType.Float),
    ("TriggerSoftware", featureType.Command),
    ("TriggerMode", featureType.Enum),
    ("TriggerSource", featureType.Enum),
    # CounterAndTimerControl Section
    # RemoveParameterLimitControl Section
    # Feature parameter
]
