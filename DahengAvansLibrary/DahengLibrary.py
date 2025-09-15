import os
if 0:
    import gxipy as gx
    from gxipy.gxidef import *
    import cv2
    import numpy as np

    os.environ["GALAXY_GENICAM_ROOT"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenICam"
    os.environ["GENICAM_GENTL64_PATH"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

    # voeg de bin folder toe aan PATH
    os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenICam\bin\Win64_x64"
    os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\APIDll\Win64"
    os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\"Win64"

    import gxipy as gxi

class dahengCamera:
    def __init__(self):
        print("init daheng camera")
        pass

    def open(self):
        print("open daheng camera")
        pass

    def close(self):
        print("close daheng camera")
        pass