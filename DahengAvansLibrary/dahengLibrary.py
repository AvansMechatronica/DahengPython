#!/usr/bin/python
# doel: Bibliotheek voor Daheng-camera’s
# auteur: Gerard Harkema
# datum: 2024-06-17
# versie: 1.00 initiële versie
#

import os
import warnings

# ------------------------------------------------------------
# Instellen van de omgeving voor de Daheng Galaxy SDK
# ------------------------------------------------------------
# De SDK heeft specifieke omgevingsvariabelen nodig om de juiste
# GenICam- en GenTL-componenten te kunnen vinden.
os.environ["GALAXY_GENICAM_ROOT"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenICam"
os.environ["GENICAM_GENTL64_PATH"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

# Voeg de benodigde paden toe aan de systeemvariabele PATH
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenICam\bin\Win64_x64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\APIDll\Win64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

# ------------------------------------------------------------
# Importeren van externe modules en Daheng-hulpprogramma’s
# ------------------------------------------------------------
import gxipy as gx
from ctypes import *
from gxipy.gxidef import *
import numpy
from gxipy.ImageFormatConvert import *
import cv2
from DahengAvansLibrary.dahengFeature import *


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


# ============================================================
# Klasse: dahengCamera
# Doel: Wrapper rond de Daheng Galaxy SDK voor eenvoudige toegang
# ============================================================
class dahengCamera:
    """
    Wrapperklasse voor Daheng-camera’s met de Galaxy SDK.

    Functionaliteiten:
    - Initialiseren en openen van een Daheng-camera
    - Configureren van belichting, trigger en beeldverwerking
    - Starten/stoppen van beeldstreaming
    - Opnemen en converteren van frames naar OpenCV-compatibele BGR-beelden
    - Veilig sluiten en vrijgeven van de camera
    """

    def __init__(self, device_index, debug=False):
        """Initialiseer de camera-interface en open de opgegeven camera-index."""
        self.debug = debug
        if self.debug:
            print("<DahengCamera: init camera>")

        # Maak een DeviceManager-object aan om beschikbare camera’s te beheren
        self.device_manager = gx.DeviceManager()

        # Hulpmiddelen voor conversie en beeldverwerking
        self.image_convert = self.device_manager.create_image_format_convert()
        self.image_process = self.device_manager.create_image_process()

        self.frame_counter = 0  # Teller voor het aantal opgenomen frames

        # Open de camera op basis van het opgegeven indexnummer
        self.open(device_index)

    def open(self, device_index):
        """Open een Daheng-camera via zijn index en configureer de standaardinstellingen."""
        dev_num, self.dev_info_list = self.device_manager.update_all_device_list()
        if dev_num == 0:
            if self.debug:
                print("<DahengCamera: Geen camera gevonden>")
            self.open = False
            return

        # Open de opgegeven camera (meestal index 1 bij één camera)
        self.cam = self.device_manager.open_device_by_index(device_index)
        self.remote_device_feature = self.cam.get_remote_device_feature_control()

        # Configuratie van beeldverwerking: schakel kleurcorrectie uit
        image_process_config = self.cam.create_image_process_config()
        image_process_config.enable_color_correction(False)

        # Definieer diverse camera-features (instellingen)
        for name, ftype in features:
            if(self.remote_device_feature.is_implemented(name)):
                setattr(self, name, dahengFeature(self.remote_device_feature, ftype, name))
            else:
                warnings.warn(f"Feature bestaat niet: {name}")

        # Laad de standaard gebruikersinstellingen van de camera
        self.UserSetSelector.set("Default")
        self.UserSetLoad.send_command()

        # Toon camera-informatie bij debugmodus
        if self.debug:
            print("<DahengCamera: ***********************************************>")
            print(f"<Vendor Name:   {self.dev_info_list[0]['vendor_name']}>")
            print(f"<Model Name:    {self.dev_info_list[0]['model_name']}>")
            print(f"<Serial Number: {self.dev_info_list[0]['sn']}>")
            print("<DahengCamera: ***********************************************>")

        self.open = True

    def isOpen(self):
        """Controleer of de camera open is."""
        return self.open

    def startStream(self):
        """Start continue beeldstreaming vanaf de camera."""
        self.cam.stream_on()

    def stopStream(self):
        """Stop de continue beeldstreaming."""
        self.cam.stream_off()

    def get_best_valid_bits(self, pixel_format):
        """Bepaal de optimale geldige bitrange voor het opgegeven pixelformaat."""
        valid_bits = DxValidBit.BIT0_7

        # Verschillende formaten hebben hun eigen geldige bitrange
        if pixel_format in (GxPixelFormatEntry.MONO8,
                            GxPixelFormatEntry.BAYER_GR8, GxPixelFormatEntry.BAYER_RG8,
                            GxPixelFormatEntry.BAYER_GB8, GxPixelFormatEntry.BAYER_BG8,
                            GxPixelFormatEntry.RGB8, GxPixelFormatEntry.BGR8,
                            GxPixelFormatEntry.R8, GxPixelFormatEntry.B8, GxPixelFormatEntry.G8):
            valid_bits = DxValidBit.BIT0_7
        elif pixel_format in (GxPixelFormatEntry.MONO10, GxPixelFormatEntry.MONO10_PACKED, GxPixelFormatEntry.MONO10_P,
                              GxPixelFormatEntry.BAYER_GR10, GxPixelFormatEntry.BAYER_RG10,
                              GxPixelFormatEntry.BAYER_GB10, GxPixelFormatEntry.BAYER_BG10,
                              GxPixelFormatEntry.BAYER_GR10_P, GxPixelFormatEntry.BAYER_RG10_P,
                              GxPixelFormatEntry.BAYER_GB10_P, GxPixelFormatEntry.BAYER_BG10_P,
                              GxPixelFormatEntry.BAYER_GR10_PACKED, GxPixelFormatEntry.BAYER_RG10_PACKED,
                              GxPixelFormatEntry.BAYER_GB10_PACKED, GxPixelFormatEntry.BAYER_BG10_PACKED):
            valid_bits = DxValidBit.BIT2_9
        elif pixel_format in (GxPixelFormatEntry.MONO12, GxPixelFormatEntry.MONO12_PACKED, GxPixelFormatEntry.MONO12_P,
                              GxPixelFormatEntry.BAYER_GR12, GxPixelFormatEntry.BAYER_RG12,
                              GxPixelFormatEntry.BAYER_GB12, GxPixelFormatEntry.BAYER_BG12,
                              GxPixelFormatEntry.BAYER_GR12_P, GxPixelFormatEntry.BAYER_RG12_P,
                              GxPixelFormatEntry.BAYER_GB12_P, GxPixelFormatEntry.BAYER_BG12_P,
                              GxPixelFormatEntry.BAYER_GR12_PACKED, GxPixelFormatEntry.BAYER_RG12_PACKED,
                              GxPixelFormatEntry.BAYER_GB12_PACKED, GxPixelFormatEntry.BAYER_BG12_PACKED):
            valid_bits = DxValidBit.BIT4_11
        elif pixel_format in (GxPixelFormatEntry.MONO14, GxPixelFormatEntry.MONO14_P,
                              GxPixelFormatEntry.BAYER_GR14, GxPixelFormatEntry.BAYER_RG14,
                              GxPixelFormatEntry.BAYER_GB14, GxPixelFormatEntry.BAYER_BG14,
                              GxPixelFormatEntry.BAYER_GR14_P, GxPixelFormatEntry.BAYER_RG14_P,
                              GxPixelFormatEntry.BAYER_GB14_P, GxPixelFormatEntry.BAYER_BG14_P):
            valid_bits = DxValidBit.BIT6_13
        elif pixel_format in (GxPixelFormatEntry.MONO16,
                              GxPixelFormatEntry.BAYER_GR16, GxPixelFormatEntry.BAYER_RG16,
                              GxPixelFormatEntry.BAYER_GB16, GxPixelFormatEntry.BAYER_BG16):
            valid_bits = DxValidBit.BIT8_15
        return valid_bits

    def convert_to_RGB(self, raw_image):
        """Converteer een ruwe camerabeeldbuffer naar RGB-formaat."""
        self.image_convert.set_dest_format(GxPixelFormatEntry.RGB8)
        valid_bits = self.get_best_valid_bits(raw_image.get_pixel_format())
        self.image_convert.set_valid_bits(valid_bits)

        # Bepaal de grootte van de outputbuffer
        buffer_out_size = self.image_convert.get_buffer_size_for_conversion(raw_image)
        output_image_array = (c_ubyte * buffer_out_size)()
        output_image = addressof(output_image_array)

        # Voer de conversie uit naar RGB
        self.image_convert.convert(raw_image, output_image, buffer_out_size, False)
        if output_image is None:
            if self.debug:
                print("<DahengCamera: Conversie van RawImage naar RGBImage mislukt>")
            return

        return output_image_array, buffer_out_size

    def grab_frame(self, timeout=1000):
        """Neem één frame op, converteer naar BGR (OpenCV-formaat) en retourneer als NumPy-array."""
        self.frame_counter += 1
        if self.debug:
            print(f"<DahengCamera: grab_frame {self.frame_counter}>")

        if not self.open:
            if self.debug:
                print("<DahengCamera: camera niet open>")
            return None

        try:
            # Vraag een beeld op van de camerastream
            raw_image = self.cam.data_stream[0].get_image(timeout)
            if raw_image is None:
                if self.debug:
                    print("<DahengCamera: Beeld ophalen mislukt>")
                return None

            # Indien het beeld niet RGB is, converteer het eerst
            if raw_image.get_pixel_format() != GxPixelFormatEntry.RGB8:
                rgb_image_array, rgb_image_buffer_length = self.convert_to_RGB(raw_image)
                if rgb_image_array is None:
                    return None
                numpy_image = numpy.frombuffer(rgb_image_array, dtype=numpy.ubyte,
                                               count=rgb_image_buffer_length).reshape(
                    raw_image.frame_data.height,
                    raw_image.frame_data.width,
                    3
                )
            else:
                # Indien al RGB, direct als NumPy-array ophalen
                numpy_image = raw_image.get_numpy_array()

                # Verbeter eventueel de beeldkwaliteit
                rgb_image = GxImageInfo()
                rgb_image.image_width = raw_image.frame_data.width
                rgb_image.image_height = raw_image.frame_data.height
                rgb_image.image_buf = raw_image.frame_data.image_buf
                rgb_image.image_pixel_format = GxPixelFormatEntry.RGB8
                self.image_process.image_improvement(rgb_image, rgb_image.image_buf, self.image_process_config)

                if numpy_image is None:
                    return None

            # Converteer van RGB naar BGR (vereist door OpenCV)
            bgr_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)

            return bgr_image

        except Exception as ex:
            if self.debug:
                print(f"Fout bij grab_frame: {str(ex)}")
            return None

    def close(self):
        """Sluit de camera en geef alle resources vrij."""
        if self.debug:
            print("<DahengCamera: Close camera>")
        self.cam.close_device()
        self.open = False

    def __del__(self):
        """Zorg ervoor dat de camera netjes wordt afgesloten bij vernietiging van het object."""
        self.close()
