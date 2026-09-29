''' Common constants for Switch 2 devices. '''
from enum import IntEnum, auto
from bit_helper import bit
from .br import axis


class sw2(IntEnum):
    ''' Buttons bitfield definition for input report 0x05. '''
    Y = 0
    X = auto()
    B = auto()
    A = auto()
    R_SR = auto()
    R_SL = auto()
    R = auto()
    ZR = auto()
    MINUS = auto()
    PLUS = auto()
    RJ = auto()
    LJ = auto()
    HOME = auto()
    CAPTURE = auto()
    C = auto()
    UNKNOWN = auto()
    DOWN = auto()
    UP = auto()
    RIGHT = auto()
    LEFT = auto()
    L_SR = auto()
    L_SL = auto()
    L = auto()
    ZL = auto()
    GR = auto()
    GL = auto()


sw2_pro_btns_mask = [
    0, 0, 0, 0,
    0, 0, 0, 0,
    bit(sw2.LEFT), bit(sw2.RIGHT), bit(sw2.DOWN), bit(sw2.UP),
    bit(sw2.C), 0, 0, 0,
    bit(sw2.Y), bit(sw2.A), bit(sw2.B), bit(sw2.X),
    bit(sw2.PLUS), bit(sw2.MINUS), bit(sw2.HOME), bit(sw2.CAPTURE),
    bit(sw2.ZL), bit(sw2.L), bit(sw2.GL), bit(sw2.LJ),
    bit(sw2.ZR), bit(sw2.R), bit(sw2.GR), bit(sw2.RJ),
]


sw2_gc_btns_mask = [
    0, 0, 0, 0,
    0, 0, 0, 0,
    bit(sw2.LEFT), bit(sw2.RIGHT), bit(sw2.DOWN), bit(sw2.UP),
    0, 0, 0, 0,
    bit(sw2.B), bit(sw2.X), bit(sw2.A), bit(sw2.Y),
    bit(sw2.PLUS), bit(sw2.C), bit(sw2.HOME), bit(sw2.CAPTURE),
    0, bit(sw2.ZL), bit(sw2.L), 0,
    0, bit(sw2.ZR), bit(sw2.R), 0,
]


sw2_jc_btns_mask = [
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    0, 0, 0, 0,
    bit(sw2.B) | bit(sw2.UP), bit(sw2.X) | bit(sw2.DOWN), bit(sw2.A) | bit(sw2.LEFT), bit(sw2.Y) | bit(sw2.RIGHT),
    bit(sw2.CAPTURE) | bit(sw2.PLUS), bit(sw2.MINUS) | bit(sw2.HOME), 0, 0,
    bit(sw2.L_SL) | bit(sw2.R_SL), bit(sw2.ZL) | bit(sw2.ZR), 0, bit(sw2.LJ) | bit(sw2.RJ),
    bit(sw2.L_SR) | bit(sw2.R_SR), bit(sw2.L) | bit(sw2.R), 0, 0,
]


sw2_pro_axes = {
    axis.LX: {'neutral': 0x800, 'abs_max': 1610, 'abs_min': 1610, 'deadzone': 0},
    axis.LY: {'neutral': 0x800, 'abs_max': 1610, 'abs_min': 1610, 'deadzone': 0},
    axis.RX: {'neutral': 0x800, 'abs_max': 1610, 'abs_min': 1610, 'deadzone': 0},
    axis.RY: {'neutral': 0x800, 'abs_max': 1610, 'abs_min': 1610, 'deadzone': 0},
}


sw2_gc_axes = {
    axis.LX: {'neutral': 0x800, 'abs_max': 1225, 'abs_min': 1225, 'deadzone': 0},
    axis.LY: {'neutral': 0x800, 'abs_max': 1225, 'abs_min': 1225, 'deadzone': 0},
    axis.RX: {'neutral': 0x800, 'abs_max': 1120, 'abs_min': 1120, 'deadzone': 0},
    axis.RY: {'neutral': 0x800, 'abs_max': 1120, 'abs_min': 1120, 'deadzone': 0},
}


sw2_gc_triggers = {
    axis.LM: {'neutral': 30, 'abs_max': 195, 'abs_min': 0x00, 'deadzone': 8},
    axis.RM: {'neutral': 30, 'abs_max': 195, 'abs_min': 0x00, 'deadzone': 8},
}


sw2_ljc_axes = {
    axis.LX: {'neutral': 0x800, 'abs_max': 1610, 'abs_min': 1610, 'deadzone': 0, 'polarity': 1},
    axis.LY: {'neutral': 0x800, 'abs_max': 1610, 'abs_min': 1610, 'deadzone': 0},
}


sw2_rjc_axes = {
    axis.LX: {'neutral': 0x800, 'abs_max': 1610, 'abs_min': 1610, 'deadzone': 0},
    axis.LY: {'neutral': 0x800, 'abs_max': 1610, 'abs_min': 1610, 'deadzone': 0, 'polarity': 1},
}
