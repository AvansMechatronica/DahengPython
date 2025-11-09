#!/usr/bin/python
# doel: Klasse voor het beheren van verschillende featuretypes van een Daheng-camera
# auteur: Gerard Harkema
# datum: 2024-06-17
# versie: 1.00 initiële versie
#

from enum import Enum
import warnings
from sympy.strategies.core import switch  # (wordt hier niet gebruikt — mogelijk overbodig import)

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

# ============================================================
# Klasse: dahengFeature
# Doel: algemene interface voor het lezen, schrijven en aansturen
#       van features op de Daheng-camera
# ============================================================
class dahengFeature:
    def __init__(self, remote_device_feature, feature_type: featureType, feature_name):
        """
        Constructor voor een Daheng feature.

        Parameters:
        - remote_device_feature: object dat toegang geeft tot de features van het apparaat
        - feature_type: type van de feature (zie featureType)
        - feature_name: naam van de feature in de SDK
        """
        self.remote_device_feature = remote_device_feature
        self.feature_name = feature_name
        self.feature_type = feature_type

        # Poging om de juiste feature op te halen op basis van het type
        try:
            match feature_type:
                case featureType.Integer:
                    self.feature = self.remote_device_feature.get_int_feature(self.feature_name)
                case featureType.Float:
                    self.feature = self.remote_device_feature.get_float_feature(self.feature_name)
                case featureType.String:
                    self.feature = self.remote_device_feature.get_string_feature(self.feature_name)
                case featureType.Bool:
                    self.feature = self.remote_device_feature.get_bool_feature(self.feature_name)
                case featureType.Enum:
                    self.feature = self.remote_device_feature.get_enum_feature(self.feature_name)
                case featureType.Command:
                    self.feature = self.remote_device_feature.get_command_feature(self.feature_name)
                case _:
                    warnings.warn("Ongeldig feature-type opgegeven")
        except:
            warnings.warn(f"Kon feature niet ophalen: {self.feature_name}")
            return None

    # ------------------------------------------------------------
    # Controlefuncties
    # ------------------------------------------------------------
    def is_readable(self):
        """Controleer of de feature uitleesbaar is."""
        return self.remote_device_feature.is_readable(self.feature_name)

    def is_writable(self):
        """Controleer of de feature schrijfbaar is."""
        return self.remote_device_feature.is_writable(self.feature_name)

    # ------------------------------------------------------------
    # Waardefuncties
    # ------------------------------------------------------------
    def get_range(self):
        """Lees het bereik (min, max, stapgrootte) van de feature uit."""
        if(self.feature_type.value != featureType.Integer):
            try:
                return self.feature.get_range()
            except:
                warnings.warn(f"Kon bereik niet ophalen: {self.feature_name}")
                return None

    def get(self):
        """Lees de huidige waarde van de feature uit (indien toegestaan)."""
        try:
            if self.is_readable():
                return self.feature.get()
            else:
                return None
        except:
            warnings.warn(f"Kon waarde niet lezen: {self.feature_name}")
            return 0.0

    def set(self, value):
        """
        Stel de waarde van de feature in, afhankelijk van het type.
        Controleert eerst of de feature schrijfbaar is.
        """
        try:
            # Zorg dat de waarde wordt omgezet naar het juiste Python-type
            match self.feature_type:
                case featureType.Integer:
                    write_value = int(value)
                case featureType.Float:
                    write_value = float(value)
                case featureType.String:
                    write_value = str(value)
                case featureType.Bool:
                    write_value = bool(value)
                case featureType.Enum:
                    write_value = value
                case _:
                    warnings.warn("Ongeldig feature-type voor set-operatie")

            # Alleen schrijven als de feature schrijfbaar is
            if self.is_writable():
                self.feature.set(write_value)

        except:
            warnings.warn(f"Kon waarde niet instellen voor: {self.feature_name}")
            return

    # ------------------------------------------------------------
    # Commandofunctie
    # ------------------------------------------------------------
    def send_command(self):
        """Voer een commando-type feature uit (zoals 'trigger' of 'reset')."""
        try:
            if self.feature_type == featureType.Command:
                self.feature.send_command()
            else:
                warnings.warn("Ongeldig feature-type voor send-command")
        except:
            warnings.warn(f"Kon commando niet uitvoeren: {self.feature_name}")

    # Functie om de maximale lengte van een string-feature op te vragen
    def get_string_max_length(self):
        if self.feature_type.value == featureType.String:
            try:
                return self.feature.get_string_max_length()
            except:
                # Waarschuwing tonen als de actie mislukt
                warnings.warn(f"Kon waarde niet uitvoeren: {self.feature_name}")
                return 0
        else:
            # Waarschuwing als het featuretype niet overeenkomt
            warnings.warn(f"Feature '{self.feature_name}' is geen stringtype.")
            return 0

    # Functie om de bufferlengte op te vragen
    def get_buffer_length(self):
        if self.feature_type.value == featureType.Buffer:
            try:
                return self.feature.get_buffer_length()
            except:
                warnings.warn(f"Kon waarde niet uitvoeren: {self.feature_name}")
                return 0
        else:
            warnings.warn(f"Feature '{self.feature_name}' is geen buffertype.")
            return 0

    # Functie om de buffer op te halen
    def get_buffer(self):
        if self.feature_type.value == featureType.Buffer:
            try:
                return self.feature.get_buffer()
            except:
                warnings.warn(f"Kon waarde niet uitvoeren: {self.feature_name}")
                return None
        else:
            warnings.warn(f"Feature '{self.feature_name}' is geen buffertype.")
            return None

    # Functie om de buffer te zetten
    def set_buffer(self, buffer):
        if self.feature_type.value == featureType.Buffer:
            try:
                self.feature.set_buffer(buffer)
            except:
                warnings.warn(f"Kon waarde niet uitvoeren: {self.feature_name}")
                return
        else:
            warnings.warn(f"Feature '{self.feature_name}' is geen buffertype.")
            return