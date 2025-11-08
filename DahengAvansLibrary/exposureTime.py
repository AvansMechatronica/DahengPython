#!/usr/bin/python

class exposureTime:
    def __init__(self, remote_device_feature):
        self.remote_device_feature = remote_device_feature
        try:
            self.exposure_time_feature = self.remote_device_feature.get_float_feature("ExposureTime")
        except:
            print("<DahengCamera: Failed to get ExposureTime from remote device>")

        pass
    def get_range(self):
        return self.exposure_time_feature.get_range()
    def get(self):
        return self.exposure_time_feature.get()
    def set(self, exposure_time):
        if self.remote_device_feature.is_writable("ExposureTime"):
            self.exposure_time_feature.set(float(exposure_time))


if 0:
    try:
        exposure_mode_feature = self.remote_device_feature.get_enum_feature("ExposureMode")
        print(exposure_mode_feature.get_range())
        exposure_current_mode = exposure_mode_feature.get()
        print("ExposureMode: " + str(exposure_current_mode))
        if 0:
            if self.remote_device_feature.is_writable("ExposureTime"):
                exposure_time_feature.set(current_exposure_time * 100)
                current_exposure_time = exposure_time_feature.get()
                print("ExposureTime 2: " + str(current_exposure_time))
    except:
        print("<DahengCamera: Failed to get ExposureTime from remote device>")


            # exit when the camera is a mono camera
