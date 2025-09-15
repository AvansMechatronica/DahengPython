# version:1.1.2312.9221
import sys
import os

os.environ["GALAXY_GENICAM_ROOT"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenICam"
os.environ["GENICAM_GENTL64_PATH"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

# voeg de bin folder toe aan PATH
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenICam\bin\Win64_x64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\APIDll\Win64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

import gxipy as gx
from ctypes import *
from gxipy.gxidef import *
import numpy
from gxipy.ImageFormatConvert import *
import cv2


def get_best_valid_bits(pixel_format):
    valid_bits = DxValidBit.BIT0_7
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
                          GxPixelFormatEntry.BAYER_GB14_P, GxPixelFormatEntry.BAYER_BG14_P,
                          ):
        valid_bits = DxValidBit.BIT6_13
    elif pixel_format in (GxPixelFormatEntry.MONO16,
                          GxPixelFormatEntry.BAYER_GR16, GxPixelFormatEntry.BAYER_RG16,
                          GxPixelFormatEntry.BAYER_GB16, GxPixelFormatEntry.BAYER_BG16):
        valid_bits = DxValidBit.BIT8_15
    return valid_bits


def convert_to_RGB(raw_image):
    image_convert.set_dest_format(GxPixelFormatEntry.RGB8)
    valid_bits = get_best_valid_bits(raw_image.get_pixel_format())
    image_convert.set_valid_bits(valid_bits)

    # create out put image buffer
    buffer_out_size = image_convert.get_buffer_size_for_conversion(raw_image)
    output_image_array = (c_ubyte * buffer_out_size)()
    output_image = addressof(output_image_array)

    # convert to rgb
    image_convert.convert(raw_image, output_image, buffer_out_size, False)
    if output_image is None:
        print('Failed to convert RawImage to RGBImage')
        return

    return output_image_array, buffer_out_size


def main():
    print("")
    print("-------------------------------------------------------------")
    print("Sample to show how to acquire color image continuously and show acquired image (OpenCV).")
    print("-------------------------------------------------------------")
    print("")

    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_all_device_list()
    if dev_num == 0:
        print("Number of enumerated devices is 0")
        return

    # open the first device
    cam = device_manager.open_device_by_index(1)
    remote_device_feature = cam.get_remote_device_feature_control()

    # get image convert obj
    global image_convert
    image_convert = device_manager.create_image_format_convert()

    # get image improvement obj
    global image_process, image_process_config
    image_process = device_manager.create_image_process()
    image_process_config = cam.create_image_process_config()
    image_process_config.enable_color_correction(False)

    # exit when the camera is a mono camera
    pixel_format_value, pixel_format_str = remote_device_feature.get_enum_feature("PixelFormat").get()
    if Utility.is_gray(pixel_format_value):
        print("This sample does not support mono camera.")
        cam.close_device()
        return

    # set continuous acquisition
    trigger_mode_feature = remote_device_feature.get_enum_feature("TriggerMode")
    trigger_mode_feature.set("Off")

    # get param of improving image quality
    if remote_device_feature.is_readable("GammaParam"):
        gamma_value = remote_device_feature.get_float_feature("GammaParam").get()
        image_process_config.set_gamma_param(gamma_value)
    else:
        image_process_config.set_gamma_param(1)
    if remote_device_feature.is_readable("ContrastParam"):
        contrast_value = remote_device_feature.get_int_feature("ContrastParam").get()
        image_process_config.set_contrast_param(contrast_value)
    else:
        image_process_config.set_contrast_param(0)

    # start data acquisition
    cam.stream_on()

    num = 1000  # aantal beelden om te tonen
    for i in range(num):
        raw_image = cam.data_stream[0].get_image()
        if raw_image is None:
            print("Getting image failed.")
            continue

        # get RGB image from raw image
        image_buf = None
        if raw_image.get_pixel_format() != GxPixelFormatEntry.RGB8:
            rgb_image_array, rgb_image_buffer_length = convert_to_RGB(raw_image)
            if rgb_image_array is None:
                return
            numpy_image = numpy.frombuffer(rgb_image_array, dtype=numpy.ubyte,
                                           count=rgb_image_buffer_length).reshape(
                raw_image.frame_data.height,
                raw_image.frame_data.width,
                3
            )
            image_buf = addressof(rgb_image_array)
        else:
            numpy_image = raw_image.get_numpy_array()
            image_buf = raw_image.frame_data.image_buf

        rgb_image = GxImageInfo()
        rgb_image.image_width = raw_image.frame_data.width
        rgb_image.image_height = raw_image.frame_data.height
        rgb_image.image_buf = image_buf
        rgb_image.image_pixel_format = GxPixelFormatEntry.RGB8

        # improve image quality
        image_process.image_improvement(rgb_image, image_buf, image_process_config)

        if numpy_image is None:
            continue

        # --- OpenCV: tonen van het beeld ---
        bgr_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
        cv2.imshow("Acquired Image", bgr_image)
        cv2.waitKey(1)

        print("Frame ID: %d   Height: %d   Width: %d"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

    # stop data acquisition
    cam.stream_off()
    cam.close_device()

    print("Press any key to close...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
