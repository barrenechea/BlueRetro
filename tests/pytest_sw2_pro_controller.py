''' Tests for the Switch 2 Pro controller. '''
import pytest
from itertools import islice
from device_data.test_data_generator import btns_generic_test_data
from device_data.test_data_generator import axes_test_data_generator
from bit_helper import swap24, swap32
from device_data.sw2 import sw2_pro_btns_mask, sw2_pro_axes
from device_data.br import system, dev_mode, bt_conn_type, axis, bt_type, bt_subtype
from device_data.gc import gc_axes


DEVICE_NAME = 'DeviceName'
VID = 0x057E
PID = 0x2069
UNKNOWN_PID = 0x20FF


@pytest.mark.parametrize('blueretro', [[system.GC, dev_mode.PAD, bt_conn_type.BT_LE]], indirect=True)
def test_sw2_pro_controller_default_buttons_mapping(blueretro):
    ''' Press each buttons and check if default mapping is right. '''
    # Set device name
    rsp = blueretro.send_name(DEVICE_NAME)
    assert rsp['device_name']['device_id'] == 0
    assert rsp['device_name']['device_type'] == bt_type.SW2
    assert rsp['device_name']['device_subtype'] == bt_subtype.SUBTYPE_DEFAULT
    assert rsp['device_name']['device_name'] == 'DeviceName'

    # Set device VID & PID
    rsp = blueretro.send_vid_pid(VID, PID)
    assert rsp['device_vid_pid']['device_id'] == 0
    assert rsp['device_vid_pid']['vid'] == VID
    assert rsp['device_vid_pid']['pid'] == PID

    # Init adapter with a few neutral state report
    for _ in range(2):
        blueretro.send_to_bridge(0x01,
            '00000000'
            '00000000'
            '0000'
            '000880'
            '000880'
            '00000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000'
            '0000'
            '00'
        )

    # Validate buttons default mapping
    for sw2_btns, br_btns in btns_generic_test_data(sw2_pro_btns_mask):
        rsp = blueretro.send_to_bridge(0x01,
            '00000000'
            f'{swap32(sw2_btns):08x}'
            '0000'
            '000880'
            '000880'
            '00000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000'
            '0000'
            '00'
        )

        assert rsp['wireless_input']['btns'] == sw2_btns
        assert rsp['generic_input']['btns'][0] == br_btns


@pytest.mark.parametrize('blueretro', [[system.GC, dev_mode.PAD, bt_conn_type.BT_LE]], indirect=True)
def test_sw2_pro_controller_axes_default_scaling(blueretro):
    ''' Set the various axes and check if the scaling is right. '''
    # Set device name
    rsp = blueretro.send_name(DEVICE_NAME)
    assert rsp['device_name']['device_id'] == 0
    assert rsp['device_name']['device_type'] == bt_type.SW2
    assert rsp['device_name']['device_subtype'] == bt_subtype.SUBTYPE_DEFAULT
    assert rsp['device_name']['device_name'] == 'DeviceName'

    # Set device VID & PID
    rsp = blueretro.send_vid_pid(VID, PID)
    assert rsp['device_vid_pid']['device_id'] == 0
    assert rsp['device_vid_pid']['vid'] == VID
    assert rsp['device_vid_pid']['pid'] == PID

    # Init adapter with a few neutral state report
    for _ in range(2):
        blueretro.send_to_bridge(0x01,
            '00000000'
            '00000000'
            '0000'
            '000880'
            '000880'
            '00000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000'
            '0000'
            '00'
        )

    # Validate axes default scaling
    for axes in axes_test_data_generator(sw2_pro_axes, gc_axes, 0.0135):
        rsp = blueretro.send_to_bridge(0x01,
            '00000000'
            '00000000'
            '0000'
            f'{swap24(axes[axis.LX]["wireless"] | axes[axis.LY]["wireless"] << 12):06x}'
            f'{swap24(axes[axis.RX]["wireless"] | axes[axis.RY]["wireless"] << 12):06x}'
            '00000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000'
            '0000'
            '00'
        )

        for ax in islice(axis, 0, 4):
            assert rsp['wireless_input']['axes'][ax] == axes[ax]['wireless']
            assert rsp['generic_input']['axes'][ax] == axes[ax]['generic']
            assert rsp['mapped_input']['axes'][ax] == axes[ax]['mapped']
            assert rsp['wired_output']['axes'][ax] == axes[ax]['wired']


@pytest.mark.parametrize('blueretro', [[system.GC, dev_mode.PAD, bt_conn_type.BT_LE]], indirect=True)
def test_sw2_unknown_controller_default_buttons_mapping(blueretro):
    ''' Press each buttons and check an unknown PID falls back to the Pro 2 mapping. '''
    # Set device name
    rsp = blueretro.send_name(DEVICE_NAME)
    assert rsp['device_name']['device_id'] == 0
    assert rsp['device_name']['device_type'] == bt_type.SW2
    assert rsp['device_name']['device_subtype'] == bt_subtype.SUBTYPE_DEFAULT
    assert rsp['device_name']['device_name'] == 'DeviceName'

    # Set device VID & PID
    rsp = blueretro.send_vid_pid(VID, UNKNOWN_PID)
    assert rsp['device_vid_pid']['device_id'] == 0
    assert rsp['device_vid_pid']['vid'] == VID
    assert rsp['device_vid_pid']['pid'] == UNKNOWN_PID

    # Init adapter with a few neutral state report
    for _ in range(2):
        blueretro.send_to_bridge(0x01,
            '00000000'
            '00000000'
            '0000'
            '000880'
            '000880'
            '00000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000'
            '0000'
            '00'
        )

    # Validate buttons default mapping
    for sw2_btns, br_btns in btns_generic_test_data(sw2_pro_btns_mask):
        rsp = blueretro.send_to_bridge(0x01,
            '00000000'
            f'{swap32(sw2_btns):08x}'
            '0000'
            '000880'
            '000880'
            '00000000000000000000000000000000000000000000'
            '00000000000000000000000000000000000000000000'
            '0000'
            '00'
        )

        assert rsp['wireless_input']['btns'] == sw2_btns
        assert rsp['generic_input']['btns'][0] == br_btns
