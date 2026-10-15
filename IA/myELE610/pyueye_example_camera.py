#!/usr/bin/env python3


from time import sleep
from turtle import width

import cv2
import numpy as np
from pyueye import ueye

from pyueye_example_utils import (
    ImageBuffer,
    ImageData,
    Rect,
    check,
    get_bits_per_pixel,
    uEyeException,
)


class Camera:
    def __init__(self, device_id=0):
        self.h_cam = ueye.HIDS(device_id)
        ret = ueye.is_InitCamera(self.h_cam, None)
        self.img_buffers = []

        ueye.is_SetColorMode(self.h_cam, ueye.IS_CM_BGR8_PACKED)
        exposure = ueye.DOUBLE(100.0)
        ueye.is_Exposure(
            self.h_cam,
            ueye.IS_EXPOSURE_CMD_SET_EXPOSURE,
            exposure,
            ueye.sizeof(exposure),
        )
        ueye.is_SetHardwareGain(
            self.h_cam,
            100,
            ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER,
            ueye.IS_IGNORE_PARAMETER,
        )
        self.mem_ptr = ueye.c_mem_p()
        self.mem_id = ueye.int()

        self.width = 1280
        self.height = 720
        self.bits_per_pixel = 24

        ret = ueye.is_AllocImageMem(
            self.h_cam,
            self.width,
            self.height,
            self.bits_per_pixel,
            self.mem_ptr,
            self.mem_id,
        )

        ret = ueye.is_SetImageMem(self.h_cam, self.mem_ptr, self.mem_id)

    def handle(self):
        return self.h_cam

    def printInfo(self):
        """Print some information on camera"""

        print("printInfo(): print state and settings.")
        # just set a camera option (parameter) even if it is not used here
        d = ueye.double()
        ui1 = ueye.uint()

        STATUS = ueye.is_SetFrameRate(self.handle(), 2.0, d)
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Frame rate set to:':<45}  {float(d):8.3f} fps")
        STATUS = ueye.is_Exposure(
            self.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_DEFAULT, d, 8
        )
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Default exposure time:':<45}  {float(d):8.3f} ms")

        STATUS = ueye.is_Exposure(
            self.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MIN, d, 8
        )
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Minimum exposure time:':<45}  {float(d):8.3f} ms")

        STATUS = ueye.is_Exposure(
            self.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MAX, d, 8
        )
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Maximum exposure time':<45}  {float(d):8.3f} ms")
        STATUS = ueye.is_Focus(self.handle(), ueye.FDT_CMD_GET_CAPABILITIES, ui1, 4)
        if (STATUS == ueye.IS_SUCCESS) and (ui1 & ueye.FOC_CAP_AUTOFOCUS_SUPPORTED):
            print("Autofocus: SUPPORTED")

        if STATUS == ueye.IS_SUCCESS:
            print(f"{'is_Focus()':<45}  {int(ui1):8d}")

        fZR = ueye.IS_RECT()  # may be used to set focus ??
        STATUS = ueye.is_Focus(self.handle(), ueye.FOC_CMD_SET_ENABLE_AUTOFOCUS, ui1, 0)
        if STATUS == ueye.IS_SUCCESS:
            print(f"is_Focus(ENABLE) is success")
        STATUS = ueye.is_Focus(self.handle(), ueye.FOC_CMD_GET_AUTOFOCUS_STATUS, ui1, 4)
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'is_Focus(status)':<45}  {int(ui1):8d}")
        # There may be some trouble setting exposure time
        STATUS = ueye.is_Exposure(
            self.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8
        )
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Currently set exposure time':<45}  {float(d):8.3f} ms")
        d = ueye.double(5.0)
        STATUS = ueye.is_Exposure(
            self.handle(), ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, d, 8
        )
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Tried to change exposure time':<45}  {float(d):8.3f} ms")
        STATUS = ueye.is_Exposure(
            self.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8
        )
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Currently set exposure time':<45}  {float(d):8.3f} ms")
        # Sharpness
        STATUS = ueye.is_Sharpness(self.handle(), ueye.SHARPNESS_CMD_GET_VALUE, ui1, 4)
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Current Sharpness setting':<45}  {int(ui1):8d}")
        # color
        STATUS = ueye.is_SetColorMode(self.handle(), ueye.IS_CM_BGR8_PACKED)
        colormode = ueye.is_SetColorMode(self.handle(), ueye.IS_GET_COLOR_MODE)
        if STATUS == ueye.IS_SUCCESS:
            print(f"{'Current color mode':<45}  {int(colormode):8d}")

    def getcv2image(self):
        pitch = ueye.INT()
        ueye.is_GetImageMemPitch(self.h_cam, pitch)
        array = ueye.get_data(
            self.mem_ptr,
            self.width,
            self.height,
            self.bits_per_pixel,
            pitch.value,
            copy=True,
        )

        img = np.reshape(array, (int(self.height), int(self.width), 3))
        return img

    def takePicture(self):
        print(f"getOneImage() try to capture one image")

        ueye.is_StopLiveVideo(self.h_cam, ueye.IS_FORCE_VIDEO_STOP)
        retVal = ueye.is_FreezeVideo(self.h_cam, ueye.IS_WAIT)
        if retVal == ueye.IS_SUCCESS:
            print(retVal)

        return self.getcv2image()


if __name__ == "__main__":
    print("no run")
