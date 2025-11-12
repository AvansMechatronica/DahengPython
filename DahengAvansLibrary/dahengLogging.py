#!/usr/bin/python
# doel: Bibliotheek voor logging Daheng-camera’s
# auteur: Gerard Harkema
# datum: 2024-06-17
# versie: 1.00 initiële versie
#
import logging

# --------------------------------------------------------
# ANSI kleurcodes voor terminalkleurweergave
# --------------------------------------------------------
# \033[32m  → groen
# \033[33m  → geel
# \033[31m  → rood
# \033[0m   → reset naar standaardkleur
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"


# --------------------------------------------------------
# Custom Formatter voor gekleurde logging
# --------------------------------------------------------
class ColorFormatter(logging.Formatter):
    """
    Formatter die de kleur van het logbericht aanpast op basis
    van het logniveau.

    DEBUG / INFO    → groen
    WARNING         → geel
    ERROR / CRITICAL→ rood
    """
    COLORS = {
        'DEBUG': GREEN,
        'INFO': GREEN,
        'WARNING': YELLOW,
        'ERROR': RED,
        'CRITICAL': RED
    }

    def format(self, record):
        """
        Override van de standaard 'format' methode van logging.
        Voegt ANSI-kleuren toe aan het logbericht.
        """
        # Haal de kleur op basis van het logniveau
        color = self.COLORS.get(record.levelname, RESET)
        # Formatteer het bericht zoals normaal
        message = super().format(record)
        # Voeg kleurcodes toe rondom het bericht
        return f"{color}{message}{RESET}"


# --------------------------------------------------------
# Filter om INFO-berichten te verbergen
# --------------------------------------------------------
class HideInfoFilter(logging.Filter):
    """
    Logging filter die alleen INFO-berichten onderdrukt.
    Alle andere niveaus (DEBUG, WARNING, ERROR, CRITICAL)
    worden wel weergegeven.
    """

    def filter(self, record):
        return record.levelno != logging.INFO  # retourneer True als het niveau niet INFO is


# --------------------------------------------------------
# Logger configureren
# --------------------------------------------------------
logger = logging.getLogger("color_logger")  # Maak een named logger aan
logger.setLevel(logging.DEBUG)  # Logger accepteert alle niveaus (DEBUG en hoger)

# StreamHandler instellen (output naar console)
ch = logging.StreamHandler()

# Gebruik de custom ColorFormatter voor console-uitvoer
formatter = ColorFormatter(
    "%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s - %(message)s"
)
ch.setFormatter(formatter)

# Voeg de handler toe aan de logger
logger.addHandler(ch)




