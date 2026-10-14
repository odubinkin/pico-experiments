"""Управление моторами от аналогового джойстика и вывод в USB-консоль."""

import uasyncio as asyncio
from time import ticks_ms, ticks_diff

import motor
from drive import Drive
from machine import ADC, Pin

from config import (JOYSTICK_X_PIN, JOYSTICK_Y_PIN, JOYSTICK_SW_PIN,
                    JOYSTICK_POLL_MS, JOYSTICK_LOG_MS)


_x = ADC(Pin(JOYSTICK_X_PIN))
_y = ADC(Pin(JOYSTICK_Y_PIN))
_sw = Pin(JOYSTICK_SW_PIN, Pin.IN, Pin.PULL_UP)


def read():
    """Вернуть (X, Y, SW): оси 0–65535, кнопка 0 при нажатии, иначе 1."""
    return _x.read_u16(), _y.read_u16(), _sw.value()


async def watch():
    """Управлять моторами и периодически печатать показания."""
    drive = Drive()
    previous = ticks_ms()
    log_elapsed = JOYSTICK_LOG_MS
    try:
        while True:
            now = ticks_ms()
            elapsed = ticks_diff(now, previous)
            previous = now
            x, y, sw = read()
            drive.update(x, y, sw, elapsed)
            log_elapsed += elapsed
            if log_elapsed >= JOYSTICK_LOG_MS:
                print("[joystick] X=%d Y=%d SW=%d motors=%s" %
                      (x, y, sw, "ON" if drive.enabled else "OFF"))
                log_elapsed = 0
            await asyncio.sleep_ms(JOYSTICK_POLL_MS)
    finally:
        motor.stop()
