try:
    import PySpin
except ImportError as e:
    print(e)
import sys


def init_camera_test(cam):
    try:
        cam.Init()
        if cam.AcquisitionMode.GetAccessMode() != PySpin.RW:
            raise Exception("Unable to set acquisition mode to continuous. Aborting...")

        cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        cam.BeginAcquisition()

    except PySpin.SpinnakerException as ex:
        raise Exception("Error: %s" % ex)


def init_camera(cam):
    try:
        nodemap_tldevice = cam.GetTLDeviceNodeMap()
        cam.Init()
        nodemap = cam.GetNodeMap()

        sNodemap = cam.GetTLStreamNodeMap()

        # Change bufferhandling mode to NewestOnly
        node_bufferhandling_mode = PySpin.CEnumerationPtr(
            sNodemap.GetNode("StreamBufferHandlingMode")
        )
        if not PySpin.IsAvailable(node_bufferhandling_mode) or not PySpin.IsWritable(
            node_bufferhandling_mode
        ):
            raise Exception("Unable to set stream buffer handling mode.. Aborting...")

        # Retrieve entry node from enumeration node
        node_newestonly = node_bufferhandling_mode.GetEntryByName("NewestOnly")
        if not PySpin.IsAvailable(node_newestonly) or not PySpin.IsReadable(
            node_newestonly
        ):
            raise Exception("Unable to set stream buffer handling mode.. Aborting...")

        # Retrieve integer value from entry node
        node_newestonly_mode = node_newestonly.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_bufferhandling_mode.SetIntValue(node_newestonly_mode)

        node_acquisition_mode = PySpin.CEnumerationPtr(
            nodemap.GetNode("AcquisitionMode")
        )
        if not PySpin.IsAvailable(node_acquisition_mode) or not PySpin.IsWritable(
            node_acquisition_mode
        ):
            raise Exception(
                "Unable to set acquisition mode to continuous (enum retrieval). Aborting..."
            )

        # Retrieve entry node from enumeration node
        node_acquisition_mode_continuous = node_acquisition_mode.GetEntryByName(
            "Continuous"
        )
        if not PySpin.IsAvailable(
            node_acquisition_mode_continuous
        ) or not PySpin.IsReadable(node_acquisition_mode_continuous):
            raise Exception(
                "Unable to set acquisition mode to continuous (entry retrieval). Aborting..."
            )

        # Retrieve integer value from entry node
        acquisition_mode_continuous = node_acquisition_mode_continuous.GetValue()

        # Set integer value from entry node as new value of enumeration node
        node_acquisition_mode.SetIntValue(acquisition_mode_continuous)

        cam.BeginAcquisition()

    except PySpin.SpinnakerException as ex:
        raise Exception("Error: %s" % ex)


def configure_exposure(cam, exposure_time_to_set=500000.0):
    try:
        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            raise Exception("Unable to disable automatic exposure. Aborting...")
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        print("Automatic exposure disabled...")

        if cam.ExposureTime.GetAccessMode() != PySpin.RW:
            raise Exception("Unable to set exposure time. Aborting...")

        exposure_time_to_set = min(cam.ExposureTime.GetMax(), exposure_time_to_set)
        cam.ExposureTime.SetValue(exposure_time_to_set)
        print("Shutter time set to %s us...\n" % exposure_time_to_set)

    except PySpin.SpinnakerException as ex:
        raise Exception("Error: %s" % ex)


def configure_gain(cam, gain=23.3):
    try:
        if cam.GainAuto.GetAccessMode() != PySpin.RW:
            raise Exception("Unable to disable automatic Gain. Aborting...")
        cam.GainAuto.SetValue(PySpin.GainAuto_Off)
        print("Automatic Gain disabled...")

        if cam.Gain.GetAccessMode() != PySpin.RW:
            raise Exception("Unable to set Gain time. Aborting...")

        Gain_to_set = min(cam.Gain.GetMax(), gain)
        cam.Gain.SetValue(Gain_to_set)
        print("Gain set to %s...\n" % Gain_to_set)

    except PySpin.SpinnakerException as ex:
        raise Exception("Error: %s" % ex)


def reset_exposure(cam):
    try:
        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            raise Exception(
                "Unable to enable automatic exposure (node retrieval). Non-fatal error..."
            )
            return False

        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
        print("Automatic exposure enabled...")

    except PySpin.SpinnakerException as ex:
        raise Exception("Error: %s" % ex)
