import sys
import os

os.environ["GALAXY_GENICAM_ROOT"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenICam"
os.environ["GENICAM_GENTL64_PATH"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

# voeg de bin folder toe aan PATH
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenICam\bin\Win64_x64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\APIDll\Win64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

# Voeg hier het pad toe naar gxipy als nodig
#sys.path.append(r"C:\Program Files\Daheng Imaging\GalaxySDK\Development\Samples\Python")
import gxipy as gx

device_manager = gx.DeviceManager()
dev_num, dev_info_list = device_manager.update_device_list()

if dev_num == 0:
    print("Geen Daheng camera gevonden.")
else:
    cam = device_manager.open_device_by_index(1)
    print(f"Type van camera-object: {type(cam)}")
    print("\nBeschikbare attributen en methodes:")
    for attr in dir(cam):
        if not attr.startswith("__"):
            print(attr)

# Controleer of PixelFormat bestaat
print("Heeft cam een attribuut 'PixelFormat'? ", hasattr(cam, "PixelFormat"))

# Als het bestaat, toon de beschikbare methodes
if hasattr(cam, "PixelFormat"):
    print("Beschikbare methodes binnen cam.PixelFormat:")
    for attr in dir(cam.PixelFormat):
        if not attr.startswith("__"):
            print(attr)


# werkt niet
# print(cam.PixelFormat.get_enum_list())