''' Tests for generic HID controller. '''
import pytest
from itertools import islice
from device_data.test_data_generator import axes_test_data_generator
from device_data.br import axis
from device_data.gc import gc_axes


DEVICE_NAME = 'Flydigi APEX3'
HID_DESC = bytes([
    0x05, 0x01,        # Usage Page (Generic Desktop)
    0x09, 0x05,        # Usage (Gamepad)
    0xA1, 0x01,        # Collection (Application)
    0x85, 0x01,        #   Report ID (1)
    0xA1, 0x02,        #   Collection (Logical)
    0x09, 0x30,        #     Usage (X)
    0x09, 0x31,        #     Usage (Y)
    0x09, 0x32,        #     Usage (Z)
    0x09, 0x35,        #     Usage (Rz)
    0x15, 0x80,        #     Logical Minimum (-128)
    0x25, 0x7F,        #     Logical Maximum (127)
    0x35, 0x80,        #     Physical Minimum (-128)
    0x45, 0x7F,        #     Physical Maximum (127)
    0x75, 0x08,        #     Report Size (8)
    0x95, 0x04,        #     Report Count (4)
    0x81, 0x02,        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x09, 0x40,        #     Usage (Vx)
    0x09, 0x41,        #     Usage (Vy)
    0x09, 0x42,        #     Usage (Vz)
    0x09, 0x43,        #     Usage (Vbrx)
    0x15, 0x00,        #     Logical Minimum (0)
    0x26, 0xFF, 0x00,  #     Logical Maximum (255)
    0x75, 0x08,        #     Report Size (8)
    0x95, 0x04,        #     Report Count (4)
    0x81, 0x02,        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x75, 0x04,        #     Report Size (4)
    0x95, 0x01,        #     Report Count (1)
    0x15, 0x01,        #     Logical Minimum (1)
    0x25, 0x08,        #     Logical Maximum (8)
    0x46, 0x3B, 0x01,  #     Physical Maximum (315)
    0x65, 0x14,        #     Unit (System: English Rotation, Length: Centimeter)
    0x09, 0x39,        #     Usage (Hat Switch)
    0x81, 0x42,        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,Null State)
    0x65, 0x00,        #     Unit (None)
    0x05, 0x09,        #     Usage Page (Button)
    0x95, 0x0C,        #     Report Count (12)
    0x75, 0x01,        #     Report Size (1)
    0x25, 0x01,        #     Logical Maximum (1)
    0x15, 0x00,        #     Logical Minimum (0)
    0x09, 0x01,        #     Usage (0x01)
    0x09, 0x02,        #     Usage (0x02)
    0x09, 0x04,        #     Usage (0x04)
    0x09, 0x05,        #     Usage (0x05)
    0x09, 0x07,        #     Usage (0x07)
    0x09, 0x08,        #     Usage (0x08)
    0x09, 0x09,        #     Usage (0x09)
    0x09, 0x0A,        #     Usage (0x0A)
    0x09, 0x0B,        #     Usage (0x0B)
    0x09, 0x0C,        #     Usage (0x0C)
    0x09, 0x0E,        #     Usage (0x0E)
    0x09, 0x0F,        #     Usage (0x0F)
    0x81, 0x02,        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x05, 0x0C,        #     Usage Page (Consumer)
    0x09, 0x36,        #     Usage (Function Buttons)
    0x09, 0x84,        #     Usage (Enter Channel)
    0x09, 0xB8,        #     Usage (Eject)
    0x09, 0x9C,        #     Usage (Channel Increment)
    0x09, 0x9D,        #     Usage (Channel Decrement)
    0x09, 0x89,        #     Usage (Media Select TV)
    0x09, 0x8D,        #     Usage (Media Select Program Guide)
    0x09, 0x65,        #     Usage (Snapshot)
    0x09, 0x82,        #     Usage (Mode Step)
    0x09, 0x8A,        #     Usage (Media Select WWW)
    0x75, 0x01,        #     Report Size (1)
    0x95, 0x0F,        #     Report Count (15)
    0x81, 0x02,        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x05, 0x0C,        #     Usage Page (Consumer)
    0x09, 0x69,        #     Usage (Red Menu Button)
    0x75, 0x01,        #     Report Size (1)
    0x95, 0x01,        #     Report Count (1)
    0x81, 0x02,        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x05, 0x02,        #     Usage Page (Simulation Controls)
    0x15, 0x00,        #     Logical Minimum (0)
    0x26, 0xFF, 0x00,  #     Logical Maximum (255)
    0x09, 0xC5,        #     Usage (Brake)
    0x09, 0xC4,        #     Usage (Accelerator)
    0x95, 0x02,        #     Report Count (2)
    0x75, 0x08,        #     Report Size (8)
    0x81, 0x02,        #     Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0xC0,              #   End Collection
    0xC0,              # End Collection

    # 163 bytes
])


def test_hid_descriptor(blueretro):
    ''' Load a HID descriptor and check if it's parsed right. '''
    # Set device name
    rsp = blueretro.send_name(DEVICE_NAME)
    assert rsp['device_name']['device_id'] == 0
    assert rsp['device_name']['device_type'] == 0
    assert rsp['device_name']['device_subtype'] == 0
    assert rsp['device_name']['device_name'] == 'Flydigi APEX3'

    # Validate HID descriptor
    rsp = blueretro.send_hid_desc(HID_DESC)
    assert rsp['hid_reports'][0]['report_id'] == 1
    assert rsp['hid_reports'][0]['report_tag'] == 0
    assert rsp['hid_reports'][0]['report_type'] == 2
    assert rsp['hid_reports'][0]['usages'][18]["bit_offset"] == 104
    assert rsp['hid_reports'][0]['usages'][18]["bit_size"] == 8
    assert rsp['hid_reports'][0]['usages'][18]["usage_page"] == 2
    assert rsp['hid_reports'][0]['usages'][18]["usage"] == 0xC4


def test_hid_axes_default_scaling(blueretro):
    ''' Set the various axes and check if the scaling is right. '''
    blueretro.send_name(DEVICE_NAME)
    blueretro.send_hid_desc(HID_DESC)

    # Init adapter with a few neutral state report
    for _ in range(2):
        blueretro.send_hid_report(
            'a101'
            '00000000'
            '00000000'
            '0000'
            '0000'
            '0000'
        )

    # Sticks are signed, Logical Minimum (-128) & Logical Maximum (127)
    hid_axes = {
        axis.LX: {'neutral': 0, 'abs_max': 127, 'abs_min': 128, 'deadzone': 0},
        axis.LY: {'neutral': 0, 'abs_max': 127, 'abs_min': 128, 'polarity': 1, 'deadzone': 0},
        axis.RX: {'neutral': 0, 'abs_max': 127, 'abs_min': 128, 'deadzone': 0},
        axis.RY: {'neutral': 0, 'abs_max': 127, 'abs_min': 128, 'polarity': 1, 'deadzone': 0},
    }

    # Validate axes default scaling
    for axes in axes_test_data_generator(hid_axes, gc_axes, 0.0135):
        rsp = blueretro.send_hid_report(
            'a101'
            f'{axes[axis.LX]["wireless"] & 0xFF:02x}{axes[axis.LY]["wireless"] & 0xFF:02x}'
            f'{axes[axis.RX]["wireless"] & 0xFF:02x}{axes[axis.RY]["wireless"] & 0xFF:02x}'
            '00000000'
            '0000'
            '0000'
            '0000'
        )

        for ax in islice(axis, 0, 4):
            assert rsp['wireless_input']['axes'][ax] == axes[ax]['wireless']
            assert rsp['generic_input']['axes'][ax] == axes[ax]['generic']
            assert rsp['mapped_input']['axes'][ax] == axes[ax]['mapped']
            assert rsp['wired_output']['axes'][ax] == axes[ax]['wired']
