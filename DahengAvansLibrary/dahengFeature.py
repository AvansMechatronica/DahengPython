#!/usr/bin/python
# doel: Klasse voor het beheren van verschillende featuretypes van een Daheng-camera
# auteur: Gerard Harkema
# datum: 2024-06-17
# versie: 1.00 initiële versie
#


import warnings
from .dahengLogging import *


from DahengAvansLibrary.dahengFeatureList import *
from sympy.strategies.core import switch  # (wordt hier niet gebruikt — mogelijk overbodig import)

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
                    logger.error("Ongeldig feature-type opgegeven")
        except:
            logger.error(f"Kon feature niet ophalen: {self.feature_name}")
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
                logger.error(f"Kon bereik niet ophalen: {self.feature_name}")
                return None

    def get(self):
        """Lees de huidige waarde van de feature uit (indien toegestaan)."""
        try:
            if self.is_readable():
                return self.feature.get()
            else:
                return None
        except:
            logger.error(f"Kon waarde niet lezen: {self.feature_name}")
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
                    logger.error("Ongeldig feature-type voor set-operatie")

            # Alleen schrijven als de feature schrijfbaar is
            if self.is_writable():
                self.feature.set(write_value)

        except:
            logger.error(f"Kon waarde niet instellen voor: {self.feature_name}")
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
                logger.error("Ongeldig feature-type voor send-command")
        except:
            logger.error(f"Kon commando niet uitvoeren: {self.feature_name}")

    # Functie om de maximale lengte van een string-feature op te vragen
    def get_string_max_length(self):
        if self.feature_type.value == featureType.String:
            try:
                return self.feature.get_string_max_length()
            except:
                # Waarschuwing tonen als de actie mislukt
                logger.error(f"Kon waarde niet uitvoeren: {self.feature_name}")
                return 0
        else:
            # Waarschuwing als het featuretype niet overeenkomt
            logger.error(f"Feature '{self.feature_name}' is geen stringtype.")
            return 0

    # Functie om de bufferlengte op te vragen
    def get_buffer_length(self):
        if self.feature_type.value == featureType.Buffer:
            try:
                return self.feature.get_buffer_length()
            except:
                logger.error(f"Kon waarde niet uitvoeren: {self.feature_name}")
                return 0
        else:
            logger.error(f"Feature '{self.feature_name}' is geen buffertype.")
            return 0

    # Functie om de buffer op te halen
    def get_buffer(self):
        if self.feature_type.value == featureType.Buffer:
            try:
                return self.feature.get_buffer()
            except:
                logger.error(f"Kon waarde niet uitvoeren: {self.feature_name}")
                return None
        else:
            logger.error(f"Feature '{self.feature_name}' is geen buffertype.")
            return None

    # Functie om de buffer te zetten
    def set_buffer(self, buffer):
        if self.feature_type.value == featureType.Buffer:
            try:
                self.feature.set_buffer(buffer)
            except:
                logger.error(f"Kon waarde niet uitvoeren: {self.feature_name}")
                return
        else:
            logger.error(f"Feature '{self.feature_name}' is geen buffertype.")
            return

# ============================================================
# Klasse: dahengDummyFeature
# Doel: algemene interface voor het lezen, schrijven en aansturen
#       van features op de Daheng-camera
# ============================================================
class dahengDummyFeature:
    def __init__(self, remote_device_feature, feature_type: featureType, feature_name):
        """
        Constructor voor een Daheng dummy feature.

        Parameters:
        - remote_device_feature: object dat toegang geeft tot de features van het apparaat
        - feature_type: type van de feature (zie featureType)
        - feature_name: naam van de feature in de SDK
        """
        self.remote_device_feature = remote_device_feature
        self.feature_name = feature_name
        self.feature_type = feature_type
        logger.error(f"Feature bestaat niet: {self.feature_name}")

    # ------------------------------------------------------------
    # Controlefuncties
    # ------------------------------------------------------------
    def is_readable(self):
        """Controleer of de feature uitleesbaar is."""
        logger.error(f"Feature bestaat niet: {self.feature_name}.is_readable()")
        return False

    def is_writable(self):
        """Controleer of de feature schrijfbaar is."""
        logger.error(f"Feature bestaat niet: {self.feature_name}.is_writable()")
        return False

    # ------------------------------------------------------------
    # Waardefuncties
    # ------------------------------------------------------------
    def get_range(self):
        """Lees het bereik (min, max, stapgrootte) van de feature uit."""
        logger.error(f"Feature bestaat niet: {self.feature_name}.get_range()")
        return None

    def get(self):
        """Lees de huidige waarde van de feature uit (indien toegestaan)."""
        logger.error(f"Feature bestaat niet: {self.feature_name}.get()")
        return None

    def set(self, value):
        """
        Stel de waarde van de feature in, afhankelijk van het type.
        Controleert eerst of de feature schrijfbaar is.
        """
        logger.error(f"Feature bestaat niet: {self.feature_name}.set()")

    # ------------------------------------------------------------
    # Commandofunctie
    # ------------------------------------------------------------
    def send_command(self):
        """Voer een commando-type feature uit (zoals 'trigger' of 'reset')."""
        logger.error(f"Feature bestaat niet: {self.feature_name}.send_command()")


    # Functie om de maximale lengte van een string-feature op te vragen
    def get_string_max_length(self):
        logger.error(f"Feature bestaat niet: {self.feature_name}.get_string_max_length()")
        return 0

    # Functie om de bufferlengte op te vragen
    def get_buffer_length(self):
        logger.error(f"Feature bestaat niet: {self.feature_name}.get_buffer_length()")
        return 0

    # Functie om de buffer op te halen
    def get_buffer(self):
        logger.error(f"Feature bestaat niet: {self.feature_name}.get_buffer()")
        return None

    # Functie om de buffer te zetten
    def set_buffer(self, buffer):
        logger.error(f"Feature bestaat niet: {self.feature_name}.set_buffer()")



