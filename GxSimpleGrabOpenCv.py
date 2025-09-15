# version:1.0.2406.9261

import sys
import os
import gxipy as gx
from gxipy.gxidef import *
import cv2
import numpy as np

os.environ["GALAXY_GENICAM_ROOT"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenICam"
os.environ["GENICAM_GENTL64_PATH"] = r"C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"

# voeg de bin folder toe aan PATH
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenICam\bin\Win64_x64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\APIDll\Win64"
os.environ["PATH"] += r";C:\Program Files\Daheng Imaging\GalaxySDK\GenTL\Win64"


def capture_thread(cam):
    cam.stream_on()
    print("<Acquisition started, press [q] in the window to stop>")
    while True:
        try:
            frame = cam.data_stream[0].dq_buf(1000)  # timeout 1000 ms
            if frame is None:
                print("<Failed to get frame>")
                continue

            if frame.frame_data.status == GxFrameStatusList.SUCCESS:
                # convert to numpy array (mono or color)
                numpy_image = frame.get_numpy_array()

                if numpy_image is not None:
                    # Als de camera kleurbeeld geeft → RGB omzetten naar BGR voor OpenCV
                    if len(numpy_image.shape) == 3 and numpy_image.shape[2] == 3:
                        bgr_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
                    else:
                        bgr_image = numpy_image  # Mono direct tonen

                    cv2.imshow("Daheng Camera", bgr_image)

                    # stop als gebruiker 'q' indrukt
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break

                print(f"<Frame OK: Width={frame.frame_data.width}, "
                      f"Height={frame.frame_data.height}, "
                      f"FrameID={frame.frame_data.frame_id}>")
            else:
                print("<Abnormal Acquisition>")

            cam.data_stream[0].q_buf(frame)

        except Exception as ex:
            print(f"Error: {str(ex)}")
            break

    cam.stream_off()
    cv2.destroyAllWindows()


def main():
    # create a device manager
    device_manager = gx.DeviceManager()
    dev_num, dev_info_list = device_manager.update_all_device_list()
    if dev_num == 0:
        print("No Daheng camera found")
        return

    # open the first device
    cam = device_manager.open_device_by_index(1)
    remote_device_feature = cam.get_remote_device_feature_control()

    # Restore default parameter group
    remote_device_feature.get_enum_feature("UserSetSelector").set("Default")
    remote_device_feature.get_command_feature("UserSetLoad").send_command()

    print("***********************************************")
    print(f"<Vendor Name:   {dev_info_list[0]['vendor_name']}>")
    print(f"<Model Name:    {dev_info_list[0]['model_name']}>")
    print("***********************************************")
    print("Press [a] and then [Enter] to start acquisition")
    print("Press [x] and then [Enter] to Exit the Program")

    while True:
        user_input = input()
        if user_input.lower() == 'a':
            capture_thread(cam)
            break
        elif user_input.lower() == 'x':
            print("<App exit!>")
            cam.close_device()
            return

    cam.close_device()


if __name__ == "__main__":
    main()
